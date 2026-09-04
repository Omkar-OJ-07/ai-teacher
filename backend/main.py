"""
main.py — FastAPI application entry point.

Phase 1 endpoints:
  GET  /health           → service health check
  POST /api/lesson-plan  → generate personalized lesson plan via Gemini
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import LessonPlanRequest, LessonPlanResponse
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
    description="Phase 1 — Lesson Plan Generation",
    version="0.1.0",
)

# ─────────────────────────────────────────────
# CORS — allow the Vite dev server
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """Quick health check — confirms the backend is running."""
    return {"status": "ok", "service": "AI Teacher API", "phase": 1}


@app.post(
    "/api/lesson-plan",
    response_model=LessonPlanResponse,
    tags=["Lesson"],
    summary="Generate a personalized lesson plan",
)
def create_lesson_plan(request: LessonPlanRequest):
    """
    Accept a learner profile and topic, call Gemini to generate
    a structured lesson plan, and return it as validated JSON.
    """
    logger.info(
        "Lesson plan request — topic=%r level=%s language=%s time=%d min",
        request.topic,
        request.learner_level,
        request.language,
        request.available_time_minutes,
    )

    try:
        plan = gemini_service.generate_lesson_plan(request)
        logger.info("Lesson plan generated — %d segments", len(plan.segments))
        return plan

    except (ValueError, RuntimeError) as exc:
        logger.warning("Lesson plan generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    except Exception as exc:
        logger.error("Unexpected error: %s: %s", type(exc).__name__, exc)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again.",
        )
