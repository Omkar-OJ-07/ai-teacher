"""
gemini_service.py — Gemini API integration for AI Teacher.

Phase 1:  generate_lesson_plan(req)       → LessonPlanResponse
Phase 2:  generate_teaching_content(req)  → TeachingContent
          evaluate_student_answer(req)    → EvaluationResult

Security:
  API key is loaded from the GEMINI_API_KEY environment variable only.
  It is never logged, printed, or returned to the caller.
"""

import os
import re
import json
import time
import logging
from google import genai
from dotenv import load_dotenv

from schemas import (
    LessonPlanRequest, LessonPlanResponse, LessonSegment,
    StartTeachingRequest, TeachingContent, VisualSpec, QuestionData,
    EvaluateAnswerRequest, EvaluationResult,
    AskQuestionRequest, AskQuestionResponse,
)

load_dotenv()

logger = logging.getLogger(__name__)
MODEL = "gemini-3.6-flash"


# ═══════════════════════════════════════════════════════════════
# Custom exception: quota / rate-limit / service-unavailable
# ═══════════════════════════════════════════════════════════════

class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini is rate-limited, quota-exhausted, or unreachable.

    This is the ONLY exception that triggers the deterministic fallback path.
    It must NOT be raised for malformed output, JSON errors, or Pydantic
    validation failures — those are real bugs that must surface normally.
    """



# ═══════════════════════════════════════════════════════════════
# Gemini client — lazy init so a missing key gives a clear message
# ═══════════════════════════════════════════════════════════════

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Create backend/.env with GEMINI_API_KEY=your_key_here"
            )
        _client = genai.Client(api_key=api_key)
    return _client


# ═══════════════════════════════════════════════════════════════
# Shared utilities
# ═══════════════════════════════════════════════════════════════

_LEVEL_INSTRUCTIONS = {
    "Beginner": (
        "Use very simple language. Avoid jargon. "
        "Use everyday analogies and relatable real-world examples. "
        "Explain foundational concepts before anything else."
    ),
    "Intermediate": (
        "Use clear explanations with moderate technical detail. "
        "Include practical examples. Assume basic familiarity with the subject."
    ),
    "Advanced": (
        "Use precise technical language and terminology. "
        "Include in-depth explanations, edge cases, and advanced examples. "
        "Assume strong prior knowledge."
    ),
}



# ═══════════════════════════════════════════════════════════════
# Retry configuration
# ═══════════════════════════════════════════════════════════════

_MAX_RETRIES   = 3          # total attempts (1 original + 2 retries)
_RETRY_DELAYS  = [1.0, 2.0] # seconds between attempts (exponential-ish)

def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return raw text.

    Raises:
        GeminiUnavailableError — quota exhausted, rate-limited, or service down
                                  after all retries. Triggers the fallback path.
        RuntimeError           — programming/config errors (no retry in caller).
    """
    client = _get_client()
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text or ""

        except Exception as exc:
            last_exc = exc
            exc_name = type(exc).__name__
            error_text = str(exc)

            logger.error(
                "Gemini API error (attempt %d/%d): %s: %s",
                attempt,
                _MAX_RETRIES,
                exc_name,
                error_text,
            )

            # ── Quota / rate-limit: no point retrying, raise immediately ──
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or \
               "quota" in error_text.lower() or "rate" in error_text.lower():
                raise GeminiUnavailableError(
                    "Gemini API rate limit reached. "
                    "Please wait a moment and try again."
                ) from exc

            # ── Programming/config errors: raise immediately, don't retry ──
            if isinstance(exc, (ValueError, TypeError)):
                raise RuntimeError(
                    "The AI service returned an unexpected error. "
                    "Please try again."
                ) from exc

            # ── Transient error: retry with backoff ───────────────────────
            if attempt < _MAX_RETRIES:
                delay = _RETRY_DELAYS[attempt - 1]
                logger.warning(
                    "Retrying Gemini request in %.0fs (attempt %d/%d)...",
                    delay, attempt, _MAX_RETRIES,
                )
                time.sleep(delay)

    # All retries exhausted — treat as service unavailable
    raise GeminiUnavailableError(
        "The AI service is currently unavailable after multiple attempts. "
        "Please try again in a moment."
    ) from last_exc

def _extract_json(text: str) -> str:
    """Strip markdown fences; fall back to first { … } block."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text


def _parse_json(raw: str, context: str) -> dict:
    """Parse JSON from a Gemini response with labelled error context."""
    if not raw or not raw.strip():
        raise ValueError(f"AI returned an empty response ({context}). Please try again.")
    cleaned = _extract_json(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("JSON parse failed (%s). Cleaned length: %d", context, len(cleaned))
        raise ValueError(f"AI returned an unreadable response ({context}). Please try again.")



# ═══════════════════════════════════════════════════════════════
# DETERMINISTIC FALLBACK SYSTEM
# ═══════════════════════════════════════════════════════════════
# Called when Gemini is unavailable (GeminiUnavailableError).
# No API calls are made. Valid Pydantic objects are returned using
# only the request data. Clearly labelled in logs.
# ═══════════════════════════════════════════════════════════════

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "it", "in", "of", "to", "and", "or", "that",
    "this", "are", "was", "be", "as", "at", "by", "we", "so", "for",
    "on", "do", "its", "with", "into", "can", "from", "what", "how",
    "you", "your", "they", "their", "which", "when", "where", "who",
    "has", "have", "had", "not", "but", "also", "just", "very", "more",
    "than", "some", "any", "all", "both", "each", "our", "my", "about",
    "will", "would", "could", "should", "may", "might", "must",
})

_FALLBACK_VISUAL_TYPES = ["diagram", "text_slide", "table", "equation", "timeline"]


def _fallback_visual_spec(visual_type: str, concept: str) -> dict:
    vt = visual_type if visual_type in _FALLBACK_VISUAL_TYPES else "text_slide"
    title = f"{concept} — Overview"
    description = f"A visual summary of {concept} to aid understanding."
    if vt == "diagram":
        elements = [
            f"{concept} — the core idea",
            "Cause → Effect relationship",
            "Key components interact to produce the outcome",
        ]
    elif vt == "equation":
        elements = [
            f"{concept} (conceptual formula)",
            "Variable 1: represents the input or cause",
            "Variable 2: represents the output or result",
        ]
    elif vt == "timeline":
        elements = [
            f"Step 1: Understand the foundations of {concept}",
            f"Step 2: See {concept} in action through examples",
            f"Step 3: Apply {concept} to solve real problems",
        ]
    elif vt == "table":
        elements = [
            "Aspect, Description",
            f"Definition, Core meaning of {concept}",
            f"Example, A real-world instance of {concept}",
            f"Importance, Why {concept} matters",
        ]
    else:
        elements = [
            f"{concept}",
            f"Definition: The core principle of {concept}",
            f"Key insight: Understanding {concept} helps explain the world around us",
        ]
    return {"type": vt, "title": title, "elements": elements, "description": description}


def _fallback_lesson_plan(req: LessonPlanRequest) -> LessonPlanResponse:
    """Deterministic lesson plan — no Gemini call."""
    if req.available_time_minutes <= 5:
        n_segments = 1
    elif req.available_time_minutes <= 20:
        n_segments = 3
    else:
        n_segments = 5

    topic = req.topic
    duration_each = max(1, req.available_time_minutes // n_segments)
    visual_types = ["text_slide", "diagram", "table", "equation", "timeline"]

    templates = [
        {
            "title": f"{topic} — Introduction and Foundations",
            "concept": f"{topic}: core principles and definition",
            "goal": f"define {topic} and explain what it is and why it matters",
            "points": [
                f"{topic} is a foundational concept with specific properties",
                f"Understanding {topic} requires knowing its basic components",
                f"The purpose of {topic} is to explain a specific phenomenon",
            ],
            "example": f"A real-world situation where {topic} is visible every day.",
        },
        {
            "title": f"{topic} — How It Works",
            "concept": f"{topic}: internal mechanism and process",
            "goal": f"explain the mechanism by which {topic} operates",
            "points": [
                f"{topic} operates through a specific process or chain of events",
                f"The inputs and outputs of {topic} follow a predictable pattern",
                f"Understanding the mechanism helps predict behaviour",
            ],
            "example": f"A step-by-step demonstration of {topic} using everyday objects.",
        },
        {
            "title": f"{topic} — Key Relationships",
            "concept": f"{topic}: relationships between components",
            "goal": f"identify how different factors interact within {topic}",
            "points": [
                f"Multiple factors influence {topic}",
                f"Changing one variable affects the outcome in a predictable way",
                f"These relationships can be observed and measured",
            ],
            "example": f"A comparison showing what happens when one factor of {topic} is changed.",
        },
        {
            "title": f"{topic} — Real-World Applications",
            "concept": f"{topic}: practical applications and use cases",
            "goal": f"connect {topic} to real-world problems and solutions",
            "points": [
                f"{topic} is used to solve practical problems in many fields",
                f"Professionals apply {topic} in their work every day",
                f"Technology and tools are built around the principles of {topic}",
            ],
            "example": f"A case study from engineering, science, or daily life involving {topic}.",
        },
        {
            "title": f"{topic} — Summary and Mastery Check",
            "concept": f"{topic}: synthesis and consolidation of learning",
            "goal": f"consolidate understanding and apply {topic} independently",
            "points": [
                f"The key ideas of {topic} connect into a coherent whole",
                f"Being able to explain {topic} in your own words shows mastery",
                f"Practice and application deepen understanding beyond memorisation",
            ],
            "example": f"An original scenario that the student must analyse using {topic}.",
        },
    ]

    segments = []
    for i in range(n_segments):
        tmpl = templates[i % len(templates)]
        segments.append(LessonSegment(
            id=i + 1,
            title=tmpl["title"],
            concept=tmpl["concept"],
            duration_minutes=duration_each,
            teaching_goal=f"Students will be able to {tmpl['goal']}",
            key_points=tmpl["points"],
            example=tmpl["example"],
            visual_type=visual_types[i % len(visual_types)],
            interaction_required=(i == n_segments - 1) or (i == 1),
        ))

    title_suffix = " (Source-Grounded)" if req.source_material and req.source_material.strip() else ""
    return LessonPlanResponse(
        title=f"Understanding {topic}: A Complete Guide{title_suffix}",
        learner_level=req.learner_level,
        language=req.language,
        total_duration_minutes=req.available_time_minutes,
        learning_objectives=[
            f"Define and explain the core concept of {topic}",
            f"Describe how {topic} works and what factors influence it",
            f"Apply knowledge of {topic} to real-world examples",
        ],
        segments=segments,
    )


def _fallback_teaching_content(req: StartTeachingRequest) -> TeachingContent:
    """Deterministic teaching content — no Gemini call."""
    concept = req.concept
    goal = req.teaching_goal
    key_points = req.key_points or [
        f"The core idea of {concept}",
        f"{concept} has specific, observable properties",
    ]
    example = req.example or f"Consider a real-world situation where {concept} is clearly visible."

    explanation = (
        f"Let's explore {concept} together. "
        f"The goal is to help you {goal}. "
        f"Think of it this way: {concept} is a key idea that explains something specific about the world around us. "
        f"Pay close attention to the key points below — they form the foundation of your understanding. "
        f"The example that follows will make this concrete and memorable."
    )
    correct_answer = (
        f"{concept} can be understood as: {'; '.join(key_points[:2])}."
    )
    vs_dict = _fallback_visual_spec(req.visual_type, concept)

    return TeachingContent(
        segment_id=req.segment_id,
        explanation=explanation,
        key_points=key_points,
        example=example,
        visual_spec=VisualSpec(**vs_dict),
        question=QuestionData(
            type="short_answer",
            prompt=f"In your own words, can you explain what {concept} is and why it matters?",
            options=None,
            correct_answer=correct_answer,
            acceptable_answer_points=key_points[:3],
        ),
        correct_answer=correct_answer,
        acceptable_answer_points=key_points[:3],
    )


def _keyword_overlap(text: str, reference: str) -> float:
    """Fraction of meaningful reference words found in student answer. Range 0.0–1.0."""
    def words(s: str) -> set:
        return {w.lower() for w in re.findall(r"\b[a-z]{3,}\b", s.lower())
                if w.lower() not in _STOP_WORDS}
    ref_words = words(reference)
    if not ref_words:
        return 0.0
    return len(ref_words & words(text)) / len(ref_words)


def _shorten(text: str, max_len: int = 70) -> str:
    """Safely truncate a student answer for quoting back in feedback."""
    text = " ".join(text.split())  # collapse whitespace
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return (cut or text[:max_len]) + "..."


def _matched_keywords(answer: str, reference: str, limit: int = 3) -> list[str]:
    """Meaningful words the student actually used that also appear in reference text,
    in the order the student used them. Used to make feedback answer-aware."""
    def words(s: str) -> list[str]:
        return [w for w in re.findall(r"\b[a-z]{3,}\b", s.lower()) if w not in _STOP_WORDS]
    ref_words = set(words(reference))
    matched, seen = [], set()
    for w in words(answer):
        if w in ref_words and w not in seen:
            matched.append(w)
            seen.add(w)
        if len(matched) >= limit:
            break
    return matched


def _fallback_evaluation(req: EvaluateAnswerRequest) -> EvaluationResult:
    """Deterministic keyword-overlap evaluation — no Gemini call.

    Conservative heuristic: errs toward 'partial' rather than 'correct'.
    Feedback text is generated from the student's actual answer and the
    current attempt count, so repeated wrong answers do NOT all produce
    identical text. This is NOT semantic understanding — it is an honest,
    disclosed lexical approximation. Logged clearly as fallback.
    """
    answer = req.student_answer.strip()
    attempt = req.attempt_count
    points = req.acceptable_answer_points or [req.correct_answer]
    concept = req.concept
    goal = req.teaching_goal

    is_empty = len(answer) < 3

    overlaps = [_keyword_overlap(answer, pt) for pt in points]
    correct_overlap = _keyword_overlap(answer, req.correct_answer)
    overlaps.append(correct_overlap)

    strong_hits = sum(1 for o in overlaps if o >= 0.35)
    any_hit = (not is_empty) and any(o >= 0.20 for o in overlaps)
    coverage = strong_hits / len(overlaps) if overlaps else 0.0

    # Which specific point is best-matched vs. still missing (for answer-aware text)
    point_overlaps = list(zip(points, overlaps[:len(points)]))
    point_overlaps.sort(key=lambda p: p[1], reverse=True)
    best_point, best_overlap = point_overlaps[0] if point_overlaps else (points[0], 0.0)
    missing_point = next((p for p, o in point_overlaps if o < 0.20), points[-1])

    matched_words = _matched_keywords(answer, " ".join(points) + " " + req.correct_answer)
    answer_preview = _shorten(answer, 60)

    logger.info(
        "[FALLBACK EVAL] attempt=%d classification_input coverage=%.2f matched_points=%d answer_preview=%r",
        attempt, coverage, strong_hits, answer_preview,
    )

    # ── CORRECT ──────────────────────────────────────────────────────
    if not is_empty and (coverage >= 0.50 or (len(points) == 1 and correct_overlap >= 0.40)):
        highlight = matched_words[0] if matched_words else concept
        logger.info("[FALLBACK EVAL] classification=correct attempt=%d matched_points=%d", attempt, strong_hits)
        return EvaluationResult(
            classification="correct",
            feedback=(
                f"Good work — you correctly identified '{highlight}' as part of {concept}. "
                f"That shows real understanding of the core idea."
            ),
            teaching_decision=f"[FALLBACK] coverage={coverage:.2f} strong_hits={strong_hits}",
            next_action="continue",
        )

    # ── PARTIAL ──────────────────────────────────────────────────────
    elif any_hit:
        logger.info("[FALLBACK EVAL] classification=partial attempt=%d matched_points=%d", attempt, strong_hits)
        recognized = matched_words[0] if matched_words else _shorten(answer, 40)

        if attempt <= 1:
            feedback = (
                f"You're on the right track — you mentioned '{recognized}', which relates to {concept}. "
                f"But there's an important idea still missing: {missing_point} "
                f"Try connecting those two ideas together."
            )
            follow_up = f"Which of these key ideas is most important here: {missing_point}"
        else:
            feedback = (
                f"You correctly recognized '{recognized}'. What's still missing is this: {missing_point} "
                f"Let's focus specifically on that piece."
            )
            follow_up = f"In one sentence, how does '{missing_point}' relate to {concept}?"

        return EvaluationResult(
            classification="partial",
            feedback=feedback,
            teaching_decision=f"[FALLBACK] coverage={coverage:.2f} any_hit=True attempt={attempt}",
            next_action="follow_up",
            follow_up_question=follow_up,
            follow_up_correct_answer=req.correct_answer,
            follow_up_acceptable_points=list(points[:2]),
        )

    # ── MISCONCEPTION (or empty answer) ─────────────────────────────
    else:
        logger.info("[FALLBACK EVAL] classification=misconception attempt=%d matched_points=0", attempt)
        script_excerpt = (req.teaching_script or "")[:180].strip()

        if is_empty:
            ack = "You haven't given much to work with yet."
        else:
            ack = f"You answered: \"{answer_preview}\"."

        # Feedback tone escalates with attempt count
        if attempt <= 1:
            feedback = (
                f"{ack} That doesn't yet connect to the main idea of {concept}. "
                f"Focus instead on this key idea: {points[0]}"
            )
            adapted_explanation = (
                f"The key thing to understand about {concept} is: {points[0]} "
                f"This connects to the lesson goal because you need to {goal}."
            )
            follow_up = f"What is the main purpose or meaning of {concept}?"
        elif attempt == 2:
            second_point = points[1] if len(points) > 1 else points[0]
            feedback = (
                f"{ack} Let's simplify — {concept} isn't about that. "
                f"The important piece is: {second_point}"
            )
            adapted_explanation = (
                f"Let's break {concept} into smaller pieces. "
                f"First: {points[0]} "
                + (f"Second: {second_point} " if second_point != points[0] else "")
                + (f"{script_excerpt}" if script_excerpt else "")
            ).strip()
            follow_up = f"Which of these key ideas is most important: {second_point}?"
        else:
            feedback = (
                f"{ack} Let's make this as direct as possible: {concept} means {req.correct_answer} "
                f"That's the core structure of the answer."
            )
            adapted_explanation = (
                f"Here is the direct structure: {concept} means {req.correct_answer} "
                f"Every part of that sentence matters — try to use similar wording yourself."
            )
            follow_up = f"Complete this idea: {concept} means ______."

        return EvaluationResult(
            classification="misconception",
            feedback=feedback,
            teaching_decision=f"[FALLBACK] coverage={coverage:.2f} no meaningful overlap attempt={attempt}",
            next_action="reteach",
            adapted_explanation=adapted_explanation,
            new_analogy=(
                f"Think of {concept} like something familiar from everyday life — "
                f"the same underlying idea applies in both cases, just with different details."
            ),
            follow_up_question=follow_up,
            follow_up_correct_answer=req.correct_answer,
            follow_up_acceptable_points=list(points[:2]),
        )


# ═══════════════════════════════════════════════════════════════
# PHASE 1 — Lesson Planner
# ═══════════════════════════════════════════════════════════════

_SEGMENT_COUNT = {5: "1 to 2", 20: "3 to 5", 60: "6 to 10"}


def _retrieve_relevant_chunks(source_material: str, topic: str, top_n: int = 3) -> list[str]:
    """Lexical retrieval: split source into chunks, score by topic keyword overlap, return top_n.

    This is a simple keyword/lexical mechanism — NOT embedding-based or semantic.
    It scores each chunk by the fraction of meaningful topic words that appear in it.
    Returns [] immediately if source_material is empty.
    """
    if not source_material or not source_material.strip():
        return []

    # ── Chunk: split on blank lines; fall back to sentence groups if no paragraphs ──
    raw_chunks = [c.strip() for c in re.split(r"\n\s*\n", source_material) if c.strip()]
    if len(raw_chunks) <= 1:
        # No paragraph breaks: split into sentences and group in pairs
        sentences = re.split(r"(?<=[.!?])\s+", source_material.strip())
        raw_chunks = []
        for i in range(0, len(sentences), 2):
            group = " ".join(sentences[i:i+2]).strip()
            if group:
                raw_chunks.append(group)

    # ── Normalise topic into meaningful scoring words ──
    _local_stop = _STOP_WORDS | {"introduction", "basics", "overview", "understanding",
                                  "learn", "study", "course", "lesson"}
    topic_words = {w.lower() for w in re.findall(r"\b[a-z]{3,}\b", topic.lower())
                   if w.lower() not in _local_stop}

    if not topic_words:
        # Fallback: use any word ≥ 4 chars in the topic
        topic_words = {w.lower() for w in re.findall(r"\b\w{4,}\b", topic.lower())}

    def score_chunk(chunk: str) -> float:
        chunk_words = {w.lower() for w in re.findall(r"\b[a-z]{3,}\b", chunk.lower())}
        if not chunk_words:
            return 0.0
        overlap = topic_words & chunk_words
        # Score: fraction of topic words present, weighted by chunk density
        if not topic_words:
            return 0.0
        return len(overlap) / len(topic_words)

    # ── Score and rank ──
    scored = [(score_chunk(c), c) for c in raw_chunks if len(c) > 20]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return original text of top_n chunks (even zero-scoring ones if we have few chunks)
    top = [c for _, c in scored[:top_n] if c]
    return top


def _build_lesson_plan_prompt(req: LessonPlanRequest) -> str:
    segment_count = _SEGMENT_COUNT.get(req.available_time_minutes, "3 to 5")
    level_instruction = _LEVEL_INSTRUCTIONS.get(req.learner_level, _LEVEL_INSTRUCTIONS["Beginner"])

    # ── RAG grounding (Case A / Case B) ───────────────────────────────────────
    if not req.source_material or not req.source_material.strip():
        logger.info("[RAG] no source_material provided — topic-direct mode")
        grounding_block = ""
    else:
        chunks = _retrieve_relevant_chunks(req.source_material, req.topic)
        logger.info("[RAG] retrieved=%d chunks for topic=%s", len(chunks), req.topic)
        if chunks:
            chunks_text = "\n\n".join(f"[Chunk {i+1}]\n{c}" for i, c in enumerate(chunks))
            grounding_block = f"""
GROUNDING MATERIAL
The following source material was retrieved from text provided by the user.
Use this material as the factual basis for the lesson. Do not invent facts
that contradict or go beyond the provided material. If important information
is not covered, avoid presenting unsupported details as facts.

Retrieved material:
{chunks_text}

"""
        else:
            logger.info("[RAG] source_material provided but no scoreable chunks — topic-direct mode")
            grounding_block = ""
    # ─────────────────────────────────────────────────────────────────────────

    return f"""You are an expert AI curriculum designer creating a personalized lesson plan.
{grounding_block}
LEARNER PROFILE:
- Topic: {req.topic}
- Level: {req.learner_level}
- Language: {req.language}
- Available Time: {req.available_time_minutes} minutes
- Learning Goal: {req.learning_goal}

TEACHING LEVEL RULES:
{level_instruction}

LESSON PLAN RULES:
- Generate {segment_count} segments. Each segment must fit within {req.available_time_minutes} minutes total.
- Arrange segments in logical learning order — prerequisites and foundations first.
- Each segment teaches exactly ONE clear, specific concept. Do not combine multiple ideas.
- Keep depth over breadth. Fewer concepts taught well is better than many concepts taught shallowly.
- Every key_points list must have 2 to 4 concrete, specific points — not vague statements.
- The example must be a concrete real-world scenario that makes the concept tangible.
- Choose visual_type from exactly these options: text_slide, diagram, graph, code, equation, timeline, table
- Set interaction_required to true for at least one segment where the student should answer a question.
- The lesson title must be engaging and specific — not generic like "Introduction to {req.topic}".
- Write everything in {req.language}.

OUTPUT FORMAT:
Return ONLY a valid JSON object. No markdown fences. No explanation. No preamble. Just the raw JSON.

{{
  "title": "engaging specific lesson title",
  "learner_level": "{req.learner_level}",
  "language": "{req.language}",
  "total_duration_minutes": {req.available_time_minutes},
  "learning_objectives": [
    "specific measurable objective 1",
    "specific measurable objective 2",
    "specific measurable objective 3"
  ],
  "segments": [
    {{
      "id": 1,
      "title": "segment title",
      "concept": "the single specific concept taught in this segment",
      "duration_minutes": 5,
      "teaching_goal": "what the student will understand or be able to do after this segment",
      "key_points": [
        "concrete specific key point 1",
        "concrete specific key point 2",
        "concrete specific key point 3"
      ],
      "example": "a concrete real-world example that makes this concept tangible",
      "visual_type": "diagram",
      "interaction_required": true
    }}
  ]
}}"""


def generate_lesson_plan(req: LessonPlanRequest) -> LessonPlanResponse:
    """Generate a structured lesson plan. Phase 1 entry point.

    Falls back to _fallback_lesson_plan if Gemini is unavailable.
    """
    try:
        raw = _call_gemini(_build_lesson_plan_prompt(req))
        data = _parse_json(raw, "lesson-plan")

        segments = data.get("segments", [])
        for i, seg in enumerate(segments, start=1):
            seg["id"] = i
            if "duration_minutes" in seg:
                seg["duration_minutes"] = int(round(float(seg["duration_minutes"])))
            if not isinstance(seg.get("key_points"), list):
                seg["key_points"] = [str(seg.get("key_points", ""))]

        if "total_duration_minutes" in data:
            data["total_duration_minutes"] = int(round(float(data["total_duration_minutes"])))

        try:
            result = LessonPlanResponse(**data)
        except Exception as exc:
            logger.error("Pydantic validation failed (lesson-plan): %s", exc)
            raise ValueError("AI response did not match expected structure. Please try again.") from exc

        logger.info("[AI MODE] endpoint=lesson-plan topic=%s", req.topic)
        return result

    except GeminiUnavailableError:
        logger.warning("[FALLBACK USED] endpoint=lesson-plan topic=%s — Gemini unavailable", req.topic)
        return _fallback_lesson_plan(req)


# ═══════════════════════════════════════════════════════════════
# PHASE 2 — Teaching Content Generator
# ═══════════════════════════════════════════════════════════════

_VISUAL_ELEMENT_GUIDE = {
    "diagram":    'elements = concept nodes and relationships, e.g. ["Voltage → pushes current", "Resistance → opposes current", "Current → electrons moving"]',
    "equation":   'elements = [main equation, then each variable explained], e.g. ["V = I × R", "V = Voltage in Volts", "I = Current in Amperes", "R = Resistance in Ohms"]',
    "graph":      'elements = ["x-axis: label", "y-axis: label", then data points as "label: value"], e.g. ["x-axis: Resistance (Ω)", "y-axis: Current (A)", "1Ω: 5A", "2Ω: 2.5A", "5Ω: 1A"]',
    "code":       "elements = lines of code or pseudocode as individual strings",
    "timeline":   'elements = chronological events as strings, e.g. ["1820: Oersted discovers electromagnetism", "1827: Ohm publishes Ohm\'s Law", "1831: Faraday discovers induction"]',
    "table":      'elements = rows as comma-separated strings, first element is the header row, e.g. ["Component, Symbol, Unit", "Voltage, V, Volts", "Current, I, Amperes"]',
    "text_slide": 'elements = ["Main concept title", "Key term 1: brief definition", "Key term 2: brief definition"]',
    "image":      'elements = ["What the image depicts", "Key feature 1", "Key feature 2", "Key feature 3"]',
}


def _build_teaching_content_prompt(req: StartTeachingRequest) -> str:
    level_instruction = _LEVEL_INSTRUCTIONS.get(req.learner_level, _LEVEL_INSTRUCTIONS["Beginner"])
    key_points_json = json.dumps(req.key_points, ensure_ascii=False)
    vguide = _VISUAL_ELEMENT_GUIDE.get(req.visual_type, "elements = list of key concepts to display")

    return f"""You are a patient, human-like AI teacher. You are about to teach one concept to a student. You make pedagogical decisions — you are NOT a chatbot or a question-answering system.

LESSON CONTEXT:
- Topic: {req.lesson_title}
- This Segment: {req.segment_title}
- Core Concept: {req.concept}
- Teaching Goal: {req.teaching_goal}
- Learner Level: {req.learner_level}
- Teaching Language: {req.language}
- Planned Key Points: {key_points_json}
- Planned Example: {req.example}
- Visual Type: {req.visual_type}

LEVEL RULES: {level_instruction}

YOUR TASK:
1. Write a TEACHER-VOICE explanation (4-6 sentences). Speak directly to the student using "you", "let's", "think of it this way". Make it engaging, clear, and appropriately leveled.
2. Produce 2-4 refined, specific key teaching points (concrete, not vague).
3. Write a vivid concrete example that makes the concept tangible and memorable.
4. Create a visual_spec for visual type "{req.visual_type}":
   {vguide}
5. Write ONE conceptual question that tests genuine understanding — not recall of your exact words.
   - Prefer "short_answer" type unless MCQ is clearly better.
   - If MCQ: exactly 4 options where distractors represent REAL common misconceptions.
6. State the correct_answer clearly and specifically — not vague, not "it depends".
7. List 2-3 acceptable_answer_points — the essential conceptual ideas a correct answer must demonstrate.

QUESTION STRICTNESS RULE:
The question must distinguish students who genuinely understand from those who memorized words.
The correct_answer must be unambiguous.
acceptable_answer_points must be the core conceptual ideas, not keyword lists.

OUTPUT: Return ONLY valid JSON. No markdown fences. No preamble. No explanation text. Just the raw JSON object.

{{
  "segment_id": {req.segment_id},
  "explanation": "teacher-voice explanation written in {req.language}",
  "key_points": ["specific concrete point 1", "specific concrete point 2"],
  "example": "vivid concrete example written in {req.language}",
  "visual_spec": {{
    "type": "{req.visual_type}",
    "title": "descriptive title for this visual",
    "elements": ["element 1", "element 2", "element 3"],
    "description": "what this visual shows and why it helps understand the concept"
  }},
  "question": {{
    "type": "short_answer",
    "prompt": "conceptual question written in {req.language}",
    "options": null,
    "correct_answer": "the specific correct answer",
    "acceptable_answer_points": ["key conceptual idea 1", "key conceptual idea 2"]
  }},
  "correct_answer": "the specific correct answer",
  "acceptable_answer_points": ["key conceptual idea 1 that makes an answer correct", "key conceptual idea 2"]
}}"""


def generate_teaching_content(req: StartTeachingRequest) -> TeachingContent:
    """Generate structured teaching content for one lesson segment. Phase 2 entry point.

    Falls back to _fallback_teaching_content if Gemini is unavailable.
    """
    try:
        raw = _call_gemini(_build_teaching_content_prompt(req))
        data = _parse_json(raw, "teaching-content")

        # Guarantee segment_id
        data["segment_id"] = req.segment_id

        # Propagate correct_answer / acceptable_answer_points to top level if missing
        q = data.get("question", {})
        if not data.get("correct_answer"):
            data["correct_answer"] = q.get("correct_answer", "")
        if not data.get("acceptable_answer_points"):
            data["acceptable_answer_points"] = q.get("acceptable_answer_points", [])

        # Ensure acceptable_answer_points is a list
        if not isinstance(data.get("acceptable_answer_points"), list):
            data["acceptable_answer_points"] = []
        if not isinstance(q.get("acceptable_answer_points"), list):
            q["acceptable_answer_points"] = data["acceptable_answer_points"]

        # Normalise question.options: "null" string → None
        if q.get("options") in ("null", "", []):
            q["options"] = None

        # Ensure visual_spec.elements is a list
        vs = data.get("visual_spec", {})
        if not isinstance(vs.get("elements"), list):
            vs["elements"] = [str(vs.get("elements", ""))]
        if not vs.get("title"):
            vs["title"] = req.concept
        if not vs.get("description"):
            vs["description"] = f"Visual aid for {req.concept}"
        data["visual_spec"] = vs
        data["question"] = q

        try:
            result = TeachingContent(**data)
        except Exception as exc:
            logger.error("Pydantic validation failed (teaching-content): %s", exc)
            raise ValueError("AI response did not match expected structure. Please try again.") from exc

        logger.info("[AI MODE] endpoint=start-teaching segment_id=%d", req.segment_id)
        return result

    except GeminiUnavailableError:
        logger.warning(
            "[FALLBACK USED] endpoint=start-teaching segment_id=%d — Gemini unavailable",
            req.segment_id,
        )
        return _fallback_teaching_content(req)


# ═══════════════════════════════════════════════════════════════
# PHASE 2 — Answer Evaluator (pedagogically strict)
# ═══════════════════════════════════════════════════════════════

def _build_evaluation_prompt(req: EvaluateAnswerRequest) -> str:
    points_json = json.dumps(req.acceptable_answer_points, ensure_ascii=False)
    script_excerpt = req.teaching_script[:200].strip()
    attempt_note = (
        f"\n⚠ This is attempt #{req.attempt_count}. The student has already received feedback. "
        "Apply the same strict standards — do NOT lower the bar."
        if req.attempt_count > 1 else ""
    )

    return f"""You are an AI teacher making a strict pedagogical evaluation of a student's answer. You are NOT a chatbot. Your job is to determine exactly what the student understands and what they do not — then decide the next teaching action.{attempt_note}

TEACHING CONTEXT:
- Concept: {req.concept}
- Teaching Goal: {req.teaching_goal}
- Explanation Given to Student: {req.teaching_script}
- Learner Level: {req.learner_level}
- Language: {req.language}

QUESTION ASKED:
{req.question_prompt}

CORRECT ANSWER:
{req.correct_answer}

KEY IDEAS A CORRECT ANSWER MUST DEMONSTRATE:
{points_json}

STUDENT'S ANSWER:
"{req.student_answer}"

STRICT CLASSIFICATION RULES — apply these precisely:

"correct":
  → The student demonstrates genuine understanding of the core concept.
  → Their answer captures the essential idea accurately.
  → Minor wording differences, incomplete sentences, or informal phrasing are acceptable
    as long as the conceptual understanding is clear.

"partial":
  → The student shows SOME correct understanding but is missing a significant element.
  → Their answer is directionally right but incomplete in a way that matters.
  → Example: states the effect but not the cause, or gives the right direction but wrong mechanism.

"misconception":
  → The student's reasoning is fundamentally wrong.
  → They have an incorrect belief about how this concept works.
  → This includes: reversed causality, wrong direction, confused concepts, blank or evasive answers.
  → DO NOT classify fundamentally wrong reasoning as "partial" to be encouraging.
  → A student who says the opposite of the correct answer has a MISCONCEPTION, not a partial answer.

YOUR RESPONSE MUST:
1. Classify the answer using exactly one of: correct, partial, misconception.
2. Write specific teacher-voice feedback in {req.language} — reference what the student actually said, not generic praise/criticism.
3. State your pedagogical reasoning.
4. Choose next_action:
   - "continue"   → if correct
   - "follow_up"  → if partial (address the gap; ask a simpler targeted question)
   - "reteach"    → if misconception (completely different explanation and analogy)
5. If "reteach":
   - adapted_explanation: DIFFERENT explanation approach from this one: "{script_excerpt}..."
     Address the specific wrong belief directly. Do NOT repeat the same explanation.
   - new_analogy: A concrete everyday comparison that resolves the misconception.
6. If "follow_up" or "reteach":
   - follow_up_question: targeted new question
   - follow_up_correct_answer: specific answer
   - follow_up_acceptable_points: 2-3 key ideas

OUTPUT: Return ONLY valid JSON. No markdown fences. No preamble.

{{
  "classification": "correct",
  "feedback": "specific teacher-voice feedback written in {req.language}",
  "teaching_decision": "internal pedagogical reasoning — why this classification and next action",
  "next_action": "continue",
  "adapted_explanation": "",
  "new_analogy": "",
  "follow_up_question": "",
  "follow_up_correct_answer": "",
  "follow_up_acceptable_points": []
}}"""


def evaluate_student_answer(req: EvaluateAnswerRequest) -> EvaluationResult:
    """Evaluate a student answer and determine the pedagogical next step. Phase 2 entry point.

    Falls back to _fallback_evaluation (keyword heuristic) if Gemini is unavailable.
    """
    try:
        raw = _call_gemini(_build_evaluation_prompt(req))
        data = _parse_json(raw, "evaluate-answer")

        # Normalize classification
        classification = str(data.get("classification", "")).lower().strip()
        if classification not in ("correct", "partial", "misconception"):
            logger.warning("Unexpected classification %r — defaulting to 'partial'", classification)
            classification = "partial"
        data["classification"] = classification

        # Normalize next_action — infer from classification if invalid
        next_action = str(data.get("next_action", "")).lower().strip()
        if next_action not in ("continue", "follow_up", "reteach"):
            inferred = {"correct": "continue", "partial": "follow_up", "misconception": "reteach"}
            next_action = inferred[classification]
            logger.warning("Invalid next_action — inferred %r from classification", next_action)
        data["next_action"] = next_action

        # Consistency check: correct must be continue, misconception must be reteach
        if classification == "correct" and next_action != "continue":
            data["next_action"] = "continue"
        if classification == "misconception" and next_action == "continue":
            data["next_action"] = "reteach"

        # Ensure all string fields have defaults
        for field in ("adapted_explanation", "new_analogy", "follow_up_question",
                      "follow_up_correct_answer", "feedback", "teaching_decision"):
            if not isinstance(data.get(field), str):
                data[field] = ""

        # Ensure list field
        if not isinstance(data.get("follow_up_acceptable_points"), list):
            data["follow_up_acceptable_points"] = []

        try:
            result = EvaluationResult(**data)
        except Exception as exc:
            logger.error("Pydantic validation failed (evaluate-answer): %s", exc)
            raise ValueError("AI response did not match expected structure. Please try again.") from exc

        logger.info("[AI MODE] endpoint=evaluate-answer classification=%s", data["classification"])
        return result

    except GeminiUnavailableError:
        logger.warning(
            "[FALLBACK USED] endpoint=evaluate-answer concept=%s — Gemini unavailable",
            req.concept,
        )
        return _fallback_evaluation(req)


# ═══════════════════════════════════════════════════════════════
# PHASE 2.2 — Conversational Chat (context-aware student questions)
# ═══════════════════════════════════════════════════════════════
# The student can ask the AI Teacher a free-form question at any point
# during a segment. The teacher answers using the CURRENT lesson context
# (topic, segment, concept, explanation, key points, example) so the
# reply stays grounded in what is actually being taught — this is not
# a general-purpose chatbot, it is the teacher continuing the same lesson.
# ═══════════════════════════════════════════════════════════════

_MAX_HISTORY_TURNS = 6  # most-recent turns included in the prompt (keeps tokens small)


def _build_ask_question_prompt(req: AskQuestionRequest) -> str:
    level_instruction = _LEVEL_INSTRUCTIONS.get(req.learner_level, _LEVEL_INSTRUCTIONS["Beginner"])
    key_points_text = "\n".join(f"- {p}" for p in (req.key_points or [])) or "(none provided)"

    history = req.conversation_history[-_MAX_HISTORY_TURNS:] if req.conversation_history else []
    if history:
        history_text = "\n".join(
            f"{'Teacher' if m.role == 'teacher' else 'Student'}: {m.content}" for m in history
        )
    else:
        history_text = "(this is the first question in this segment)"

    return f"""You are an AI teacher having a live conversation with a student DURING an ongoing lesson segment. You are NOT a generic chatbot — you are continuing to teach the SAME concept the student is currently learning. Stay grounded in the lesson context below; do not drift into an unrelated topic.

LESSON CONTEXT:
- Overall Topic: {req.topic}
- Current Segment: {req.segment_title}
- Concept Being Taught: {req.concept}
- Teaching Goal: {req.teaching_goal}
- Learner Level: {req.learner_level}
- Language: {req.language}

EXPLANATION ALREADY GIVEN TO THE STUDENT:
{req.explanation}

KEY POINTS:
{key_points_text}

EXAMPLE ALREADY USED:
{req.example or "(none)"}

RECENT CONVERSATION (most recent last):
{history_text}

TEACHING LEVEL RULES:
{level_instruction}

THE STUDENT NOW ASKS:
"{req.student_question}"

YOUR JOB:
1. Answer directly and specifically — reference the actual explanation/example above rather than repeating a generic definition.
2. Stay strictly within the current concept/segment. If the question is genuinely unrelated to the lesson, gently redirect back to the topic rather than answering an unrelated question at length.
3. Keep the tone warm, patient, and teacher-like — as if speaking directly to the student.
4. Respond in {req.language}.
5. Keep the answer focused: 2-5 sentences unless the question genuinely requires a worked example or step-by-step breakdown.

OUTPUT: Return ONLY valid JSON. No markdown fences. No preamble.

{{
  "answer": "your teacher-voice answer here, written in {req.language}"
}}"""


def _fallback_ask_question(req: AskQuestionRequest) -> AskQuestionResponse:
    """Deterministic fallback when Gemini is unavailable.

    Cannot generate a genuinely new answer without an LLM, so it is honest
    about that limitation while still being useful: it restates the most
    relevant part of the existing explanation/key points/example instead
    of inventing new content, and is transparent (source="fallback") so
    the frontend can label it accordingly rather than pretend it is Gemini.
    """
    q_words = {w.lower() for w in re.findall(r"\b[a-z]{3,}\b", req.student_question.lower())} - _STOP_WORDS

    def overlap(text: str) -> int:
        text_words = {w.lower() for w in re.findall(r"\b[a-z]{3,}\b", text.lower())}
        return len(q_words & text_words)

    candidates = [("point", p) for p in (req.key_points or [])]
    if req.example:
        candidates.append(("example", req.example))
    if req.explanation:
        # Split explanation into sentences so we can surface the single most relevant one
        for sentence in re.split(r"(?<=[.!?])\s+", req.explanation.strip()):
            if sentence:
                candidates.append(("sentence", sentence))

    best = max(candidates, key=lambda kv: overlap(kv[1]), default=None)

    if best and overlap(best[1]) > 0:
        answer = (
            f"Good question about \"{req.concept}\". Based on what we just covered: {best[1]} "
            f"If that doesn't fully answer it, try rephrasing your question once the AI service is back online for a more tailored explanation."
        )
    else:
        answer = (
            f"That's a good question about \"{req.concept}\", but I can't generate a fresh, tailored answer "
            f"right now because the AI service is temporarily unavailable. Here's the core idea again: {req.explanation.strip()[:280]} "
            f"Please try asking again in a moment."
        )

    logger.warning("[FALLBACK USED] endpoint=ask-question concept=%s", req.concept)
    return AskQuestionResponse(answer=answer, source="fallback")


def answer_student_question(req: AskQuestionRequest) -> AskQuestionResponse:
    """Answer a free-form student question, grounded in the current lesson context.

    Falls back to _fallback_ask_question if Gemini is unavailable.
    """
    try:
        raw = _call_gemini(_build_ask_question_prompt(req))
        data = _parse_json(raw, "ask-question")

        answer = data.get("answer", "")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("AI returned an empty answer (ask-question). Please try again.")

        logger.info("[AI MODE] endpoint=ask-question concept=%s", req.concept)
        return AskQuestionResponse(answer=answer.strip(), source="gemini")

    except GeminiUnavailableError:
        return _fallback_ask_question(req)

