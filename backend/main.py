"""
main.py — FastAPI application entry point.

Phase 1 endpoints (unchanged):
  GET  /health             → service health check
  POST /api/lesson-plan    → generate personalized lesson plan via Gemini

Phase 2 endpoints (new):
  POST /api/start-teaching   → generate structured teaching content for one segment
  POST /api/evaluate-answer  → evaluate student answer and return pedagogical decision
"""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    LessonPlanRequest, LessonPlanResponse,
    StartTeachingRequest, TeachingContent,
    EvaluateAnswerRequest, EvaluationResult,
    AskQuestionRequest, AskQuestionResponse,
)
import gemini_service

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────

app = FastAPI(
    title="AI Teacher API",
    description="Phase 1: Lesson Plan | Phase 2: Adaptive Teaching Loop",
    version="0.2.0",
)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "AI Teacher Backend is running!",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }
# ═══════════════════════════════════════════════════════════════
# SYSTEM
# ═══════════════════════════════════════════════════════════════

@app.get("/health", tags=["System"])
def health():
    """Quick health check — confirms the backend is running."""
    return {"status": "ok", "service": "AI Teacher API", "phase": 2}


# ═══════════════════════════════════════════════════════════════
# PHASE 1 — Lesson Plan (unchanged)
# ═══════════════════════════════════════════════════════════════

@app.post(
    "/api/lesson-plan",
    response_model=LessonPlanResponse,
    tags=["Phase 1 — Lesson Plan"],
    summary="Generate a personalized lesson plan",
)
def create_lesson_plan(request: LessonPlanRequest):
    """
    Accept a learner profile and topic, call Gemini to generate
    a structured lesson plan, and return it as validated JSON.
    """
    logger.info(
        "Lesson plan request — topic=%r level=%s language=%s time=%d min",
        request.topic, request.learner_level,
        request.language, request.available_time_minutes,
    )
    try:
        plan = gemini_service.generate_lesson_plan(request)
        logger.info("Lesson plan generated — %d segments", len(plan.segments))
        return plan
    except (ValueError, RuntimeError) as exc:
        logger.warning("Lesson plan failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error (lesson-plan): %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")


# ═══════════════════════════════════════════════════════════════
# PHASE 2 — Adaptive Teaching Loop
# ═══════════════════════════════════════════════════════════════

@app.post(
    "/api/start-teaching",
    response_model=TeachingContent,
    tags=["Phase 2 — Teaching"],
    summary="Generate structured teaching content for one lesson segment",
)
def start_teaching(request: StartTeachingRequest):
    """
    Accept a lesson segment and learner profile.
    Call Gemini to generate a teacher-voice explanation, visual spec,
    and conceptual question with correct answer and acceptable answer points.
    """
    logger.info(
        "Teaching content request — segment=%d concept=%r level=%s language=%s",
        request.segment_id, request.concept,
        request.learner_level, request.language,
    )
    try:
        content = gemini_service.generate_teaching_content(request)
        logger.info(
            "Teaching content generated — segment=%d visual=%s question_type=%s",
            content.segment_id, content.visual_spec.type, content.question.type,
        )
        return content
    except (ValueError, RuntimeError) as exc:
        logger.warning("Teaching content failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error (start-teaching): %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")


@app.post(
    "/api/evaluate-answer",
    response_model=EvaluationResult,
    tags=["Phase 2 — Teaching"],
    summary="Evaluate a student answer and return a pedagogical decision",
)
def evaluate_answer(request: EvaluateAnswerRequest):
    """
    Accept the student's answer with teaching context.
    Call Gemini to classify it (correct / partial / misconception)
    and determine the next pedagogical action (continue / follow_up / reteach).
    If reteaching, includes a different explanation and analogy.
    """
    logger.info(
        "Answer evaluation — concept=%r attempt=%d answer_len=%d",
        request.concept, request.attempt_count, len(request.student_answer),
    )
    try:
        result = gemini_service.evaluate_student_answer(request)
        logger.info(
            "Evaluation complete — classification=%s next_action=%s",
            result.classification, result.next_action,
        )
        return result
    except (ValueError, RuntimeError) as exc:
        logger.warning("Evaluation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error (evaluate-answer): %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")


# ═══════════════════════════════════════════════════════════════
# PHASE 2.2 — Conversational Chat
# ═══════════════════════════════════════════════════════════════

@app.post(
    "/api/ask-question",
    response_model=AskQuestionResponse,
    tags=["Phase 2.2 — Conversation"],
    summary="Ask the AI Teacher a free-form question, grounded in the current lesson context",
)
def ask_question(request: AskQuestionRequest):
    """
    Accept a student's free-form question plus the current lesson context
    (topic, segment, concept, explanation, key points, example) and recent
    conversation history. Calls Gemini for a context-aware answer, or the
    deterministic fallback if Gemini is unavailable.
    """
    logger.info(
        "Ask-question — concept=%r question_len=%d history_len=%d",
        request.concept, len(request.student_question), len(request.conversation_history),
    )
    try:
        result = gemini_service.answer_student_question(request)
        logger.info("Ask-question answered — source=%s", result.source)
        return result
    except (ValueError, RuntimeError) as exc:
        logger.warning("Ask-question failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error (ask-question): %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")
