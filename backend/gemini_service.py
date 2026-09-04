"""
gemini_service.py — Gemini API integration for the lesson planner.

Responsibilities:
- Build the structured lesson planner prompt.
- Call Gemini (gemini-3.6-flash).
- Parse and validate the JSON response.
- Return a LessonPlanResponse.

Security:
- API key is loaded from the environment variable GEMINI_API_KEY.
- The key is never logged, printed, or returned to the caller.
"""

import os
import re
import json
import logging
from google import genai
from dotenv import load_dotenv

from schemas import LessonPlanRequest, LessonPlanResponse

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "gemini-3.6-flash"

# ─────────────────────────────────────────────
# Gemini client (lazy init to give friendly error on missing key)
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────

_SEGMENT_COUNT = {5: "1 to 2", 20: "3 to 5", 60: "6 to 10"}

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


def _build_prompt(req: LessonPlanRequest) -> str:
    segment_count = _SEGMENT_COUNT.get(req.available_time_minutes, "3 to 5")
    level_instruction = _LEVEL_INSTRUCTIONS.get(req.learner_level, _LEVEL_INSTRUCTIONS["Beginner"])

    return f"""You are an expert AI curriculum designer creating a personalized lesson plan.

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
- Choose visual_type from exactly these options: text_slide, diagram, graph, code, equation, timeline, table, image
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


# ─────────────────────────────────────────────
# JSON extraction
# ─────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """
    Strip markdown fences if Gemini wraps the JSON despite being told not to.
    Tries multiple extraction strategies before giving up.
    """
    text = text.strip()

    # Strategy 1: remove ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()

    # Strategy 2: find the first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    return text


# ─────────────────────────────────────────────
# Main service function
# ─────────────────────────────────────────────

def generate_lesson_plan(req: LessonPlanRequest) -> LessonPlanResponse:
    """
    Call Gemini to generate a structured lesson plan.
    Raises RuntimeError or ValueError with user-safe messages on failure.
    Never logs or exposes the API key.
    """
    client = _get_client()
    prompt = _build_prompt(req)

    # ── Call Gemini ──────────────────────────────────────────────────────────
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        raw_text = response.text
    except Exception as exc:
        # Log type only — do not log the exception message (may contain key info)
        logger.error("Gemini API call failed: %s", type(exc).__name__)
        raise RuntimeError(
            "The AI service is currently unavailable. Please try again in a moment."
        ) from exc

    if not raw_text or not raw_text.strip():
        raise ValueError("The AI returned an empty response. Please try again.")

    # ── Parse JSON ───────────────────────────────────────────────────────────
    cleaned = _extract_json(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse failed. Cleaned text length: %d", len(cleaned))
        raise ValueError(
            "The AI returned an unreadable response. Please try again."
        ) from exc

    # ── Post-process ─────────────────────────────────────────────────────────
    # Ensure segment IDs are sequential (Gemini sometimes skips or duplicates)
    segments = data.get("segments", [])
    for i, seg in enumerate(segments, start=1):
        seg["id"] = i
        # Coerce duration_minutes to int (Gemini sometimes returns 5.0)
        if "duration_minutes" in seg:
            seg["duration_minutes"] = int(round(float(seg["duration_minutes"])))
        # Ensure key_points is a list
        if not isinstance(seg.get("key_points"), list):
            seg["key_points"] = [str(seg.get("key_points", ""))]

    # Coerce total_duration_minutes
    if "total_duration_minutes" in data:
        data["total_duration_minutes"] = int(round(float(data["total_duration_minutes"])))

    # ── Validate with Pydantic ───────────────────────────────────────────────
    try:
        return LessonPlanResponse(**data)
    except Exception as exc:
        logger.error("Pydantic validation failed: %s", exc)
        raise ValueError(
            "The AI response did not match the expected structure. Please try again."
        ) from exc
