"""
schemas.py — Pydantic request and response models.

Phase 1: LessonPlanRequest, LessonSegment, LessonPlanResponse
Phase 2: StartTeachingRequest, TeachingContent, EvaluateAnswerRequest, EvaluationResult
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════
# PHASE 1 — LESSON PLAN (unchanged)
# ═══════════════════════════════════════════════════════════════

class LessonPlanRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    learner_level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced)$")
    language: str = Field(..., pattern="^(English|Hindi|Hinglish)$")
    available_time_minutes: int = Field(..., ge=1, le=120)
    learning_goal: str = Field(..., min_length=1, max_length=500)
    source_material: str | None = None  # optional pasted text for lexical grounding


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


# ═══════════════════════════════════════════════════════════════
# PHASE 2 — TEACHING CONTENT
# ═══════════════════════════════════════════════════════════════

class StartTeachingRequest(BaseModel):
    topic: str
    lesson_title: str
    segment_id: int
    segment_title: str
    concept: str
    teaching_goal: str
    key_points: List[str]
    example: str
    visual_type: str
    learner_level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced)$")
    language: str = Field(..., pattern="^(English|Hindi|Hinglish)$")


class VisualSpec(BaseModel):
    type: str
    title: str
    elements: List[str]
    description: str


class QuestionData(BaseModel):
    type: str  # "mcq" | "short_answer"
    prompt: str
    options: Optional[List[str]] = None
    correct_answer: str
    acceptable_answer_points: List[str]


class TeachingContent(BaseModel):
    segment_id: int
    explanation: str
    key_points: List[str]
    example: str
    visual_spec: VisualSpec
    question: QuestionData
    correct_answer: str           # top-level for easy access
    acceptable_answer_points: List[str]   # key ideas a correct answer must contain


# ═══════════════════════════════════════════════════════════════
# PHASE 2 — ANSWER EVALUATION
# ═══════════════════════════════════════════════════════════════

class EvaluateAnswerRequest(BaseModel):
    concept: str
    teaching_goal: str
    question_prompt: str
    question_type: str
    correct_answer: str
    acceptable_answer_points: List[str]
    student_answer: str = Field(..., min_length=1, max_length=2000)
    learner_level: str
    language: str
    teaching_script: str          # original explanation given to student
    attempt_count: int = Field(default=1, ge=1)


class EvaluationResult(BaseModel):
    classification: str           # "correct" | "partial" | "misconception"
    feedback: str                 # teacher-voice response to student
    teaching_decision: str        # internal pedagogical reasoning
    next_action: str              # "continue" | "follow_up" | "reteach"
    adapted_explanation: str = "" # new explanation if reteaching
    new_analogy: str = ""         # different analogy if reteaching
    follow_up_question: str = ""  # new question for follow_up / reteach
    follow_up_correct_answer: str = ""
    follow_up_acceptable_points: List[str] = []


# ═══════════════════════════════════════════════════════════════
# PHASE 2.2 — CONVERSATIONAL CHAT (context-aware student questions)
# ═══════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str      # "teacher" | "student"
    content: str


class AskQuestionRequest(BaseModel):
    topic: str
    segment_title: str
    concept: str
    teaching_goal: str
    explanation: str
    key_points: List[str] = []
    example: str = ""
    learner_level: str
    language: str
    student_question: str = Field(..., min_length=1, max_length=1000)
    conversation_history: List[ChatMessage] = []  # recent turns, most-recent last


class AskQuestionResponse(BaseModel):
    answer: str
    source: str = "gemini"   # "gemini" | "fallback" — disclosed to the frontend, not hidden
