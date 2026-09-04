"""
schemas.py — Pydantic request and response models for Phase 1.
"""

from pydantic import BaseModel, Field
from typing import List


# ─────────────────────────────────────────────
# REQUEST
# ─────────────────────────────────────────────

class LessonPlanRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    learner_level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced)$")
    language: str = Field(..., pattern="^(English|Hindi|Hinglish)$")
    available_time_minutes: int = Field(..., ge=1, le=120)
    learning_goal: str = Field(..., min_length=1, max_length=500)


# ─────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────

class LessonSegment(BaseModel):
    id: int
    title: str
    concept: str
    duration_minutes: int
    teaching_goal: str
    key_points: List[str]
    example: str
    visual_type: str
    interaction_required: bool


class LessonPlanResponse(BaseModel):
    title: str
    learner_level: str
    language: str
    total_duration_minutes: int
    learning_objectives: List[str]
    segments: List[LessonSegment]
