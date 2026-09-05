# AI Teacher — Hackathon 2026

**AI Innovation Hackathon 2026 — Round 2**
Organizer: Bharat Academix | Deadline: 5 September 2026, 5:00 PM IST

> **Core philosophy:** Working > Perfect. One complete end-to-end journey beats many half-working features.

---
heres link -- https://ai-teacher-ten-gamma.vercel.app/
---

## What This Is

An AI-powered virtual teacher that:
- Takes a topic and learner profile
- Generates a structured, personalized lesson plan via Gemini AI
- Teaches through explanation, interaction, and adaptive feedback
- Supports English, Hindi, and Hinglish
- Adapts to Beginner / Intermediate / Advanced levels

**Phase 1 (this version):** Topic + learner profile → Gemini lesson planner → structured lesson plan display.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI + Python |
| AI Model | Gemini API (`gemini-3.6-flash`) |
| State | In-memory (no database) |

---

## Project Structure

```
ai-teacher/
├── backend/
│   ├── main.py           — FastAPI app, routes
│   ├── gemini_service.py — Gemini API integration + prompt
│   ├── schemas.py        — Pydantic request/response models
│   ├── requirements.txt  — Python dependencies
│   └── .env.example      — API key template
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    — top-level state
│   │   ├── index.css                  — stylesheet
│   │   └── components/
│   │       ├── LessonForm.jsx         — learner profile form
│   │       └── LessonPlanView.jsx     — lesson plan display
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

---

## Setup

### 1. Create your Gemini API key file

Create `backend/.env` (this file is git-ignored — **never commit it**):

```
GEMINI_API_KEY=your_real_gemini_api_key_here
```

> The key is loaded from this file at startup. It is never logged, printed, or sent to the frontend.

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd frontend
npm install
```

---

## Running

### Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

Health check: http://localhost:8000/health

API docs (auto-generated): http://localhost:8000/docs

### Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## Test the Application

Open **http://localhost:5173** and enter:

| Field | Value |
|---|---|
| Topic | Newton's Laws of Motion |
| Level | Beginner |
| Language | English |
| Time | 20 minutes |
| Goal | Understand the basics |

Click **✨ Create My Lesson**.

The AI should return a structured lesson plan with 3–5 segments, learning objectives, key points, and examples.

---

## API Reference

### `POST /api/lesson-plan`

**Request:**
```json
{
  "topic": "Newton's Laws of Motion",
  "learner_level": "Beginner",
  "language": "English",
  "available_time_minutes": 20,
  "learning_goal": "Understand the basics"
}
```

**Response:**
```json
{
  "title": "...",
  "learner_level": "Beginner",
  "language": "English",
  "total_duration_minutes": 20,
  "learning_objectives": ["..."],
  "segments": [
    {
      "id": 1,
      "title": "...",
      "concept": "...",
      "duration_minutes": 5,
      "teaching_goal": "...",
      "key_points": ["..."],
      "example": "...",
      "visual_type": "diagram",
      "interaction_required": true
    }
  ]
}
```

---

## Security Notes

- **Never** commit `backend/.env` to version control
- The `.gitignore` excludes all `.env` files
- The API key is loaded from the environment only — never printed or returned
- Use `backend/.env.example` as a safe template

---

## Known Limitations (Phase 1)

- No PDF/document upload yet (Phase 2)
- No RAG / knowledge grounding yet (Phase 2)
- No teaching interaction or adaptive loop yet (Phase 2+)
- No TTS / avatar / video yet (Phase 2+)
- No quiz or learning report yet (Phase 3+)
- In-memory only — session data is lost on server restart
