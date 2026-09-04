# AI Teacher Hackathon 2026 — Complete Master Context

> **Purpose:** This file is the single source-of-truth context for the AI Teacher hackathon project. It is intended to be uploaded into a ChatGPT Project and/or given to a coding AI so the project can continue without repeatedly rediscovering requirements, decisions, constraints, or previous setup work.
>
> **Security:** The actual Gemini API key is intentionally NOT included in this file. Keep the real key in a local `.env` file only. Never put the real key in this markdown, GitHub, screenshots, chats, or prompts.

---

# 0. CURRENT PROJECT STATUS

## Competition

**AI Innovation Hackathon 2026 – Build Real-World AI Solutions**

Organizer: **Bharat Academix**

Current stage: **Round 2 — Technical Assessment**

Final submission deadline from organizer email:
**5 September 2026, 5:00 PM IST**

At the time of planning, approximately **22 hours remained**, so this is a strict time-constrained hackathon build.

## Core strategic philosophy

- WORKING > PERFECT
- DEMONSTRABLE > COMPLETE
- HIGH-SCORING FEATURES > EXTRA FEATURES
- SIMPLE > ENTERPRISE ARCHITECTURE
- One complete working journey is more valuable than many half-working features.

## Current tool roles

### ChatGPT
Use ChatGPT as the **Project Director / technical strategist / reviewer**.

Responsibilities:
- Keep the project aligned with the original challenge.
- Decide what to build next.
- Control scope.
- Review architecture and implementation decisions.
- Review Cursor output and errors.
- Prioritize according to hackathon scoring.
- Prevent unnecessary feature creep.

### Cursor
Use **Cursor only** as the main coding environment.

Do NOT use multiple coding agents independently on the same codebase. Antigravity is available but intentionally not part of the active workflow because the user does not want to be overwhelmed by multiple coding tools.

Cursor responsibilities:
- Create and modify files.
- Implement one phase at a time.
- Run the application.
- Run terminal commands.
- Debug errors.
- Modify existing code without rewriting unrelated working code.

### Gemini API
Gemini is the **AI brain inside the actual application**.

It will be responsible for:
- Lesson planning
- Teaching explanation generation
- Question generation
- Answer evaluation
- Misconception detection
- Adaptive teaching decisions
- Final learning report
- Multilingual generation

The Gemini API key has been obtained and successfully tested from Python.

---

# 1. ORIGINAL HACKATHON CHALLENGE

## Challenge title

**AI Teacher: Build a Human-Like AI Educator That Teaches Through Video**

## Problem statement

Traditional digital learning platforms generally provide pre-recorded lectures or text-based AI assistants. However, these systems often fail to provide the personalized interaction and adaptive teaching approach of a real teacher.

The challenge is to design and develop an AI-powered virtual teacher capable of understanding learning material, creating personalized lessons, and teaching students through an AI-generated video experience.

The AI Teacher should be able to take an uploaded book, textbook, PDF, notes, presentation, research paper, or other educational material, or accept a topic directly from the student, and transform it into a structured and personalized teaching session.

The system should not function as a basic question-answer chatbot. It should demonstrate the behavior of a real teacher by understanding the learner, planning the lesson, explaining concepts, providing examples, asking questions, evaluating responses, identifying areas of difficulty, and adapting the teaching approach.

---

# 2. OBJECTIVE / CAPABILITIES REQUIRED

The AI Teacher should be able to:

- Understand uploaded educational content.
- Teach any user-provided topic.
- Generate a structured lesson plan.
- Explain concepts according to the learner's level.
- Adapt the lesson according to available learning time.
- Teach in multiple languages.
- Present lessons through a human-like AI avatar and voice.
- Generate appropriate visual explanations.
- Interact with the student during the lesson.
- Evaluate the student's understanding.
- Identify misconceptions and provide alternative explanations.
- Track learning progress.
- Recommend what the student should learn or revise next.

---

# 3. USER SCENARIO SPECIFIED BY THE HACKATHON

Example student request:

> "I am a beginner. Teach me Chapter 4 in 20 minutes. Explain it in Hindi using simple examples. Ask me questions during the lesson and test me at the end."

The AI Teacher should determine:

1. What needs to be taught.
2. Which concepts should be covered first.
3. How deeply each concept should be explained.
4. Which examples or visuals should be used.
5. When the student should be questioned.
6. Whether the student has understood the concept.
7. Whether the lesson needs to be simplified or expanded.
8. What should be taught next.

The final experience should resemble an actual personalized teaching session rather than a conventional chatbot interaction.

---

# 4. LEARNING MATERIAL PROCESSING

The system should support learning from:

- Books
- Textbooks
- PDF documents
- Lecture notes
- DOC/DOCX files
- PPT/PPTX files
- Research papers
- Course material
- Other text-based educational resources

The AI should identify:

- Relevant chapters
- Sections
- Concepts
- Definitions
- Examples
- Other useful information

The organizers encourage **Retrieval-Augmented Generation (RAG)** or another suitable knowledge-grounding approach.

The system should minimize unsupported or hallucinated information when answering questions related to uploaded material.

---

# 5. TOPIC-BASED LEARNING

The AI Teacher must also teach without uploaded material.

Examples given by the organizers:

- "Teach me Artificial Intelligence from the beginning."
- "Explain Newton's Laws to a Class 8 student."
- "Teach me React for a technical interview."

Therefore there are two primary input paths:

### A. Uploaded material

Material -> extraction -> RAG -> grounded teaching

### B. Direct topic

Topic -> LLM knowledge/teaching workflow -> lesson

The hackathon problem itself is fixed: **AI Teacher**. The demonstration subject/topic can be chosen by the project team.

---

# 6. HUMAN-LIKE TEACHING — PRIMARY REQUIREMENT

The challenge explicitly defines the teaching process as:

# Understand -> Plan -> Explain -> Demonstrate -> Question -> Evaluate -> Adapt -> Continue

The teacher should:

- Introduce the topic.
- Explain concepts progressively.
- Use appropriate examples.
- Ask questions at suitable points.
- Analyze the student's responses.
- Correct mistakes constructively.
- Re-explain difficult concepts.
- Adjust difficulty.
- Confirm understanding before moving forward.

A system that only generates answers to questions is **not** considered a complete solution.

---

# 7. PERSONALIZED TEACHING

Learner inputs may include:

- Educational level
- Existing knowledge
- Learning objective
- Preferred teaching style
- Preferred language
- Available time
- Desired depth

## Beginner

- Simple terminology
- Analogies
- Fundamental concepts
- Simple examples

## Intermediate

- More technical explanations
- Practical examples

## Advanced

- Detailed concepts
- Technical terminology
- Mathematics
- Implementation details
- Advanced examples

Important: personalization must actually change teaching structure/depth, not merely change a label.

---

# 8. TIME-BASED LEARNING

Required behavior:

## 5 minutes

- Concise explanation
- Most important concepts

## 20 minutes

- Structured lesson
- Key concepts
- Examples
- Questions

## 60 minutes

- Deeper teaching
- Explanations
- Examples
- Questions
- Assessment

## 7 days

- Personalized learning plan
- Revision plan

For the MVP, 5/20/60 tier behavior can be treated as P1 if necessary, but the 20-minute scenario is the primary demo.

---

# 9. MULTILINGUAL TEACHING

Students should be able to select or naturally request a preferred language.

Examples:

- "Explain this topic in Hindi."
- "Now explain it in English."
- "Mujhe ye Hinglish mein simple example ke saath samjhao."

The lesson context should remain intact when the language changes.

Cross-language material examples:

- English textbook -> Hindi teaching
- Hindi textbook -> English teaching

Supporting multiple Indian and international languages may receive additional consideration.

MVP target:
- English
- Hindi
- Hinglish where practical

---

# 10. AI TEACHING VIDEO

The teacher must present lessons through a video-based teaching experience.

Ideally include:

- Human-like AI avatar
- Natural voice
- Spoken explanation
- On-screen text
- Diagrams and illustrations
- Relevant images
- Subject-specific visualizations
- Mathematical/technical demonstrations where applicable

Important warning from organizers:

> Simply placing a talking avatar in front of generated text is not enough for a strong implementation.

The teaching video should feel like an actual AI-led lesson.

For the MVP, at least the intro and 1–2 key teaching segments should use real avatar video, with simpler narrated visual segments allowed where necessary for speed.

---

# 11. SUBJECT-AWARE VISUAL EXPLANATION

The system should use appropriate visual forms according to subject.

## Mathematics

- Equations
- Graphs
- Step-by-step solutions

## Physics

- Diagrams
- Formulas
- Processes
- Simulations/visual demonstrations where possible

## Biology

- Labeled diagrams
- Biological processes
- Structures

## History

- Timelines
- Maps
- Events

## Programming

- Code
- Output
- Execution flow
- Architecture diagrams

The system should demonstrate how it determines which visual representation is appropriate.

For the MVP, deeply support 2–3 useful visual types rather than attempting every category shallowly.

---

# 12. INTERACTIVE LEARNING

The teacher must periodically interact with the student.

Possible interaction types:

- Conceptual questions
- Multiple-choice questions
- Short-answer questions
- Problem-solving questions
- Application-based questions
- "Explain in your own words" questions

The student's response must influence subsequent teaching.

---

# 13. MISCONCEPTION DETECTION AND ADAPTIVE TEACHING

Example specified by the organizers:

Teacher:
> "What happens to current if resistance increases while voltage remains constant?"

Student:
> "Current increases."

The AI should not merely mark it wrong.

It should:

1. Identify the misconception.
2. Explain the underlying concept again.
3. Use a different analogy.
4. Provide another example.
5. Ask a new question.
6. Re-evaluate the student's understanding.

This adaptive loop is the highest-weighted criterion and therefore a top priority.

---

# 14. ASSESSMENT AND FEEDBACK

The AI may generate:

- Quiz questions
- Conceptual questions
- Practical problems
- MCQs
- Short-answer questions

Learning report may contain:

- Score
- Concepts understood
- Weak areas
- Incorrect concepts
- Recommended revision
- Suggested next topic

Example:

Topic: Electricity
Score: 80%
Strong Areas: Current, Voltage
Needs Improvement: Resistance, Ohm's Law
Recommendation: Revise Ohm's Law and complete two additional practice problems.

---

# 15. STUDENT LEARNING PROFILE

Potential learner profile fields:

- Topics studied
- Progress
- Assessment scores
- Weak concepts
- Strong concepts
- Learning history
- Current learning path

For this hackathon MVP, persistent long-term memory is intentionally not prioritized. Session-scoped state is sufficient.

---

# 16. AI-GENERATED LEARNING PATH

For broad topics, the AI should be able to create a structured learning path.

Example Machine Learning path:

1. Python Fundamentals
2. Mathematics for ML
3. Data Processing
4. Supervised Learning
5. Unsupervised Learning
6. Model Evaluation
7. Neural Networks
8. Advanced Machine Learning

For the MVP, broad learning paths are P1 rather than core P0.

---

# 17. ALLOWED TECHNOLOGY CATEGORIES FROM THE CHALLENGE

Teams may use:

- Large Language Models
- Generative AI
- Machine Learning models
- RAG systems
- Vector databases
- Speech-to-Text
- Text-to-Speech
- AI Avatar technologies
- Computer Vision
- Generative media technologies
- Web/mobile technologies
- Cloud services
- Open-source models and frameworks

Teams must clearly disclose significant third-party APIs, models, libraries, and services.

---

# 18. MANDATORY REQUIREMENTS

A valid submission should demonstrate at least:

1. Learning from uploaded material or documents.
2. Topic-based teaching.
3. AI-generated lesson structure.
4. Personalized teaching.
5. Human-like teaching interaction.
6. Video-based AI Teacher presentation.
7. AI voice.
8. Human-like AI avatar.
9. Multilingual capability.
10. Student questioning and assessment.
11. Adaptive response to student performance.
12. Working application/prototype.

These are the core non-negotiables.

---

# 19. ADVANCED FEATURES — NOT REQUIRED

Possible enhancements:

- Real-time conversational teaching
- Multiple teacher personalities
- Emotion-aware interaction
- Long-term student memory
- Automatic study planner
- Exam preparation mode
- Revision mode
- Flashcard generation
- Automatic notes
- Concept maps
- Coding demonstration
- Interactive diagrams
- Personalized homework
- Learning analytics
- Offline/local AI models
- Accessibility features
- Multiple AI teacher characters

With the current deadline, these are intentionally deprioritized unless the core path is already complete.

---

# 20. EVALUATION CRITERIA — 100 MARKS

| Evaluation Area | Weightage |
|---|---:|
| Human-Like Teaching and Adaptation | 20 |
| AI/ML and LLM Implementation | 15 |
| RAG and Knowledge Grounding | 15 |
| AI Teaching Video Generation | 15 |
| Multilingual Capability | 10 |
| Voice and AI Avatar | 10 |
| Innovation and Originality | 5 |
| User Experience and Interface | 5 |
| Documentation and Technical Presentation | 5 |
| **TOTAL** | **100** |

The highest-value areas account for 65/100 marks:

- Human-like teaching and adaptation: 20
- AI/ML and LLM: 15
- RAG: 15
- AI teaching video: 15

Therefore effort must focus heavily on those areas.

The jury primarily evaluates whether the solution demonstrates genuine AI-driven teaching capability.

Explicitly insufficient by itself:
- Basic chatbot
- Static video
- Talking avatar reading a generated script

---

# 21. SUBMISSION REQUIREMENTS

## Source Code

GitHub repository or ZIP.

## Project Documentation

Should include:

- Problem statement
- Solution overview
- Key features
- System architecture
- AI/ML models used
- RAG implementation
- Prompt/agent architecture
- Personalization approach
- Assessment methodology
- Multilingual implementation
- Voice implementation
- Avatar/video generation approach
- APIs and third-party services
- Setup instructions
- Deployment instructions
- Known limitations

## Working Prototype

Functional application or deployed demonstration.

## Demo Video

Recommended duration: **3–7 minutes**.

The demo should show:

Upload/Topic -> Lesson Planning -> AI Teaching Video -> Student Interaction -> Adaptation -> Assessment -> Learning Feedback

---

# 22. FINAL CHALLENGE / TWO TASKS

## Task 1 — AI Teaching Video

Build an AI Teacher that takes a topic or uploaded educational content and creates a personalized teaching video.

Must:

- Understand material/topic.
- Create structured lesson.
- Adapt explanation according to learner level and available time.
- Use human-like avatar and natural voice.
- Use relevant visual explanations.
- Support multiple languages.
- Deliver an engaging educational video rather than simple text.

## Task 2 — Interactive & Adaptive AI Teacher

Extend the teacher so it can:

- Ask questions during the lesson.
- Understand and evaluate responses.
- Identify incorrect answers and knowledge gaps.
- Re-explain concepts.
- Change difficulty.
- Answer follow-up questions while maintaining context.
- Conduct final assessment/quiz.
- Provide personalized feedback and next/revision recommendation.

Final instruction from organizers:

> Do not build a chatbot that simply answers questions.
>
> Build an AI Teacher that understands, explains, interacts, adapts, and actually teaches.

---

# 23. STRATEGIC MVP DECISION

We are not trying to build a production EdTech platform in 22 hours.

We are building a focused **high-scoring end-to-end prototype**.

Primary demo journey:

```text
Upload Physics material OR choose Physics topic
        ↓
Learner profile
Beginner + Hindi/Hinglish + 20 minutes
        ↓
RAG / knowledge grounding
        ↓
Personalized lesson plan
        ↓
AI Teacher begins teaching
        ↓
Avatar + natural voice + subject-aware visual
        ↓
Teacher asks a question
        ↓
Student intentionally gives a misconception answer
        ↓
AI evaluates answer
        ↓
AI identifies misconception
        ↓
AI changes explanation strategy
        ↓
New analogy + new visual/example
        ↓
Teacher asks again
        ↓
Student demonstrates understanding
        ↓
Continue lesson
        ↓
Final quiz
        ↓
Learning report
        ↓
Weak concepts + recommendation + next topic
```

This scenario simultaneously demonstrates:

- RAG
- Personalization
- Hindi
- Avatar
- Voice
- Video
- Interaction
- Misconception detection
- Adaptive teaching
- Assessment
- Learning feedback

---

# 24. PREVIOUS CLAUDE IMPLEMENTATION SPECIFICATION — DECISIONS ALREADY MADE

The previous architecture recommendation was:

```text
[Upload PDF/DOCX/PPT or Topic Text]
        ↓
[Extraction]
        ↓
[Chunk + Embed]
        ↓
[Vector Store]
        ↓
[LLM Teacher Brain]
    ├── Lesson Planner
    ├── Segment Script Generator
    ├── Question Generator
    ├── Answer Evaluator + Misconception Detector
    └── Report Generator
        ↓
[Per-Segment Rendering]
    ├── TTS
    ├── Avatar API
    ├── Slide/Visual generator
    └── video assembly
        ↓
[Frontend]
    ├── upload/topic
    ├── lesson player
    ├── question widget
    ├── adaptation
    └── report
```

Session state can be held in a single object containing:

- Learner profile
- Lesson plan
- Segment history
- Q&A log
- Running mastery by concept

No database is necessary for the initial prototype.

---

# 25. FINAL MVP PRIORITIES

## P0 — Must build

- Upload PDF/DOCX/PPTX OR enter topic directly
- Text extraction + chunking + embedding + retrieval (real RAG, not keyword search)
- LLM-generated structured lesson plan (level, time, language)
- Script generation grounded strictly in retrieved chunks
- TTS narration (English + Hindi)
- Avatar video for intro + 1–2 key teaching segments
- On-screen slide/visual per segment
- In-lesson MCQ or short-answer question
- LLM evaluation of student answer
- Misconception detection -> adaptive re-explanation with a different analogy
- Final quiz (3–5 questions)
- Learning report: score, strong/weak concepts, recommendation
- One complete reliable end-to-end demo path
- Recorded backup video of the full flow

## P1 — Build only if time remains

- Mid-lesson language switching
- More visual types such as graph via matplotlib / simple diagram
- Real 5/20/60 minute depth differences
- Additional question types
- Simple learner profile panel visible in UI
- Broad-topic learning path generation

## P2 — Do not build unless everything else is complete

- 7-day learning plans
- Multiple teacher personalities/characters
- Long-term persistent memory across sessions
- Authentication/user accounts
- PostgreSQL/Mongo or other full database
- Microservices
- Queues/background workers
- Offline/local LLM
- Accessibility tooling
- Deployment hardening beyond one running instance

---

# 26. CURRENT TECH STACK — REVISED AROUND ACTUAL AVAILABLE ACCESS

Previous Claude blueprint proposed Claude API, but the project has now been changed to use **Gemini API**, because a working Gemini API key is available.

## Current intended stack

| Layer | Current Choice |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI + Python, single process |
| Application LLM | Gemini API |
| PDF processing | PyMuPDF or pdfplumber; prefer the simpler reliable option during implementation |
| DOCX | python-docx if needed |
| PPTX | python-pptx if needed |
| Embeddings | Local multilingual sentence-transformers |
| Vector store | FAISS, in-memory |
| State | In-memory Python dict / optional JSON |
| TTS | Fast validated provider; Azure was proposed but must be validated before commitment |
| Avatar | Fast validated provider such as D-ID/HeyGen; must be validated before commitment |
| Visuals | Deterministic HTML/CSS slides, simple diagrams, graphs, code blocks, etc. |
| Video assembly | ffmpeg / moviepy only if actually needed; keep pipeline as simple as possible |

## Important stack rule

Do not change the stack casually.

Any external dependency must be validated for:

- API availability
- Free/trial access
- Immediate access
- Billing requirements
- Generation latency
- Rate limits
- Hindi quality
- Fallback behavior

---

# 27. CURRENT GEMINI API STATUS

## Gemini API key

A Gemini API key has already been created.

The key was successfully loaded from `.env` in Python.

The test printed:

```text
API key found: True
```

A successful Gemini response was obtained.

The exact successful test response was:

> An object will remain at rest or keep moving in a straight line at a constant speed unless acted upon by an external force.

Therefore:

- Python works.
- pip works.
- google-genai is installed.
- python-dotenv is installed.
- `.env` loading works.
- Gemini API authentication works.
- Gemini text generation works.

## Model detail discovered during testing

An initial test used `gemini-2.5-flash` and returned a 404 stating that the model was no longer available to new users and recommending `gemini-3.6-flash`.

The code was changed to `gemini-3.6-flash` and then successfully generated the test answer.

Therefore the current working application code should use the model that is actually confirmed working for this API key, currently:

```text
gemini-3.6-flash
```

Do not silently revert to `gemini-2.5-flash`.

## AFC warning

The Google SDK printed:

```text
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message...
```

This was treated as a warning, not a failure, and the normal text generation succeeded.

Do not spend hackathon time fixing this warning unless function calling is later required.

---

# 28. GEMINI ENVIRONMENT SETUP

The actual API key is stored locally in `.env`.

Example:

```env
GEMINI_API_KEY=YOUR_REAL_KEY_HERE
```

The Python test used:

```python
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explain Newton's First Law in one simple sentence."
)

print(response.text)
```

## Security rules

- Never expose the real API key.
- Never commit `.env` to GitHub.
- Add `.env` to `.gitignore`.
- Use `.env.example` for documentation.
- Never ask the user to paste the actual API key into chat.

---

# 29. PYTHON/PIP SETUP STATUS

The `py` launcher is not installed/available:

```text
'py' is not recognized as an internal or external command
```

However `pip` works and installed packages successfully.

Successful installation:

```text
google-genai
python-dotenv
```

The current Python environment is Python 3.13, accessed via Windows/WindowsApps installation.

The warning about installed scripts not being on PATH is not currently blocking development.

Use:

```bash
pip install ...
```

and:

```bash
python ...
```

rather than relying on `py`.

---

# 30. DEVELOPMENT ENVIRONMENT

Current working area on Windows:

```text
C:\Users\techo\OneDrive\Desktop\AI teach
```

Gemini test folder:

```text
C:\Users\techo\OneDrive\Desktop\AI teach\test
```

The intended main project folder is:

```text
C:\Users\techo\OneDrive\Desktop\AI teach\ai-teacher
```

The user has both **Cursor** and **Antigravity**, but only **Cursor** should be used for the actual coding workflow to avoid tool overload.

---

# 31. MINIMAL PROJECT STRUCTURE

Initial implementation should be intentionally small.

Recommended target structure:

```text
ai-teacher/
│
├── backend/
│   ├── main.py
│   ├── gemini_service.py
│   ├── rag.py
│   ├── teacher.py
│   ├── media.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── state.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadOrTopic.jsx
│   │   │   ├── LessonPlanView.jsx
│   │   │   ├── LessonPlayer.jsx
│   │   │   ├── QuestionWidget.jsx
│   │   │   └── ReportView.jsx
│   │   └── api.js
│   ├── index.html
│   └── package.json
│
├── media_cache/
├── docs/
├── .gitignore
└── README.md
```

However, during the first vertical slice, do not feel obligated to create every file immediately. Start with the smallest working set and split modules as the code becomes real.

No:
- auth folder
- database folder
- Docker/Kubernetes
- microservices
- queues

unless the strategy explicitly changes later.

---

# 32. CORE DATA STRUCTURES / JSON SHAPES

## LearnerProfile

```json
{
  "learner_id": "session_1",
  "level": "beginner | intermediate | advanced",
  "language": "hi | en | hinglish",
  "available_time_minutes": 20,
  "goal": "understand Chapter 4",
  "known_concepts": [],
  "weak_concepts": []
}
```

## LessonPlan

```json
{
  "topic": "Newton's Laws",
  "source": "uploaded | topic_direct",
  "total_time_minutes": 20,
  "segments": [
    {
      "segment_id": "seg_1",
      "concept": "Newton's First Law",
      "objective": "Understand inertia",
      "depth": "brief | standard | deep",
      "planned_duration_seconds": 180,
      "has_question": true
    }
  ]
}
```

## LessonSegment

```json
{
  "segment_id": "seg_1",
  "concept": "string",
  "script_text": "spoken narration grounded in retrieved chunks",
  "source_chunks_used": ["chunk_id_3", "chunk_id_7"],
  "visual_type": "text_slide | diagram | graph | code | equation",
  "visual_spec": {
    "type": "graph",
    "description": "V vs I linear plot"
  },
  "language": "hi",
  "audio_path": null,
  "video_path": null
}
```

## Question

```json
{
  "question_id": "q_1",
  "segment_id": "seg_1",
  "type": "mcq | short_answer",
  "prompt": "string",
  "options": ["A", "B", "C", "D"],
  "correct_answer": "string",
  "concept_tested": "string"
}
```

## StudentAnswerEvaluation

```json
{
  "question_id": "q_1",
  "student_answer": "string",
  "is_correct": false,
  "misconception_detected": true,
  "misconception_description": "confuses direct vs inverse proportionality",
  "confidence": 0.85
}
```

## AdaptiveDecision

```json
{
  "based_on_question_id": "q_1",
  "action": "reexplain | new_analogy | proceed | simplify | go_deeper",
  "reason": "string",
  "next_segment": {}
}
```

## LearningReport

```json
{
  "topic": "Electricity",
  "score_percent": 80,
  "strong_concepts": ["Current", "Voltage"],
  "weak_concepts": ["Resistance"],
  "incorrect_concepts": ["Ohm's Law"],
  "recommendation": "Revise Ohm's Law and complete two additional practice problems.",
  "suggested_next_topic": "Resistance in circuits"
}
```

## SessionState

```json
{
  "session_id": "string",
  "learner_profile": {},
  "lesson_plan": {},
  "current_segment_index": 0,
  "segments_delivered": [],
  "qa_log": [
    {
      "question": {},
      "evaluation": {},
      "decision": {}
    }
  ],
  "report": null
}
```

---

# 33. MINIMAL AI PROMPT ARCHITECTURE

All structured prompts should request valid JSON only where appropriate, with no markdown fences or preamble.

## Lesson Planner

Role: expert curriculum planner.

Inputs:
- topic
- retrieved chunks if uploaded material
- learner level
- available time
- language
- goal

Requirements:
- 2–6 segments for MVP.
- ordered by prerequisite.
- depth adjusted to learner level.
- total duration matches available time.
- if material was uploaded, only include concepts supported by material.

## Teaching Segment Generator

Role: patient human-like teacher speaking directly to the student.

Inputs:
- concept
- objective
- depth
- retrieved chunks
- learner level
- language

Requirements:
- spoken narration.
- only information supported by retrieved chunks when uploaded material is the source.
- include a relatable example.
- say when material does not cover something rather than inventing it.
- choose a suitable visual type and specification.

## Question Generator

Inputs:
- concept
- teaching script
- learner level

Requirements:
- one MCQ or short-answer question.
- test genuine understanding rather than wording recall.
- include correct answer and tested concept.

## Answer + Misconception Evaluator

Inputs:
- question
- correct answer
- student answer

Requirements:
- judge correctness.
- when incorrect, diagnose the specific misconception rather than saying only "wrong".
- reason about what belief could have produced the answer.

## Adaptive Re-Teaching

Inputs:
- answer evaluation
- original segment script
- retrieved chunks
- learner profile

Requirements:
- choose action.
- if misconception exists, create a genuinely different explanation.
- use a different analogy.
- directly address the misconception.
- remain grounded in retrieved material.

## Final Report

Inputs:
- full Q&A log
- learner profile
- lesson plan

Requirements:
- compute score based on correctness.
- identify strong, weak, incorrect concepts.
- provide concise recommendation.
- suggest next topic.

---

# 34. RAG DESIGN

Target flow:

```text
Uploaded PDF
    ↓
Extract text
    ↓
Chunk text
    ↓
Generate embeddings
    ↓
Store vectors in FAISS
    ↓
User asks for lesson/segment/question
    ↓
Retrieve relevant chunks
    ↓
Pass context to Gemini
    ↓
Generate grounded response
```

Important:

- This must be **real retrieval**, not pretend keyword search.
- The system should be able to show source snippets in the UI where practical.
- If retrieved context is insufficient, the AI should say so instead of inventing information.

For time efficiency, single-document, in-memory indexing is sufficient.

---

# 35. TEACHING LOOP — THE ACTUAL CORE ENGINE

The central state machine should conceptually behave like:

```text
Start Session
    ↓
Understand Learner + Material/Topic
    ↓
Generate Lesson Plan
    ↓
Generate Current Teaching Segment
    ↓
Present Explanation + Visual + Voice/Avatar
    ↓
Ask Question
    ↓
Student Answers
    ↓
Evaluate Answer
    ↓
 ┌───────────────────────────────────────┐
 │ Correct                               │
 │   ↓                                   │
 │ Continue to next concept              │
 │                                       │
 │ Partially understood                  │
 │   ↓                                   │
 │ Additional example / simplified       │
 │ explanation                           │
 │                                       │
 │ Misconception                         │
 │   ↓                                   │
 │ New analogy + new explanation +       │
 │ possibly new visual                   │
 │   ↓                                   │
 │ Ask again                              │
 └───────────────────────────────────────┘
    ↓
Final Assessment
    ↓
Learning Report
    ↓
Recommendation / Next Topic
```

The important point is that student performance must actually alter the subsequent content.

---

# 36. VIDEO/VOICE/AVATAR STRATEGY

The project should not depend on generating an entire long video from scratch in real time.

Practical strategy:

- Generate video for intro and key explanation segments.
- Use TTS + visual slides for routine segments if necessary.
- Cache generated demo-path media.
- Keep a recorded backup of the full journey.

Potential primary avatar provider considered:
- D-ID

Potential primary TTS provider considered:
- Azure Neural TTS

But neither is locked until the user confirms immediate practical access.

For each external service:

```text
PRIMARY
   ↓ if unavailable
FALLBACK
```

Fallbacks should preserve as much of the teaching experience as possible.

---

# 37. EXTERNAL DEPENDENCY TESTS — DO THESE EARLY

## LLM

Test:
- Lesson Planner prompt
- Teaching Segment prompt
- Structured JSON reliability across multiple runs

The LLM side is already validated at basic text generation level.

## Avatar

Before building anything deeply dependent on avatar generation:

- Create one short audio file.
- Use one static teacher image.
- Call the avatar API.
- Confirm a playable video is returned.
- Measure latency.
- Verify account access, billing, quotas, and rate limits.

If it is too slow or inaccessible, change strategy immediately rather than at hour 15.

## TTS

Generate:
- one Hindi sample
- one English sample

Verify:
- naturalness
- latency
- API access
- language/voice support

---

# 38. RECOMMENDED BUILD ORDER FOR THE CURRENT SITUATION

Because the original external services were not yet verified, use this practical sequence:

## Step 0 — Validate external dependencies

- Gemini: DONE
- Avatar: next
- TTS: next

## Step 1 — Minimal foundation

- Create `ai-teacher` folder.
- Open it in Cursor.
- Backend FastAPI skeleton.
- Frontend React/Vite skeleton.
- `.env` handling.
- `/health` endpoint.

## Step 2 — First AI vertical slice

Topic + learner profile
-> Gemini
-> structured LessonPlan
-> display in frontend

This is the first major milestone.

## Step 3 — Teaching segment

LessonPlan
-> Gemini teaching script
-> visual specification
-> show lesson segment

## Step 4 — RAG

PDF
-> extract
-> chunk
-> embed
-> FAISS retrieval
-> grounded lesson/script

## Step 5 — Question/evaluation/adaptation

Question
-> student answer
-> evaluation
-> misconception
-> adaptive explanation
-> re-question

## Step 6 — TTS + avatar

Teaching script
-> TTS
-> avatar
-> teaching video

## Step 7 — Assessment/report

Quiz
-> evaluation
-> learning report

## Step 8 — Full end-to-end integration

Test the primary demo scenario repeatedly.

## Step 9 — Backup video

Record 3–7 minute demo.

## Step 10 — Documentation/submission

README, setup, architecture, APIs, known limitations, demo links.

---

# 39. FIRST CODING PHASE — EXACT SCOPE

Do not build the entire project at once.

The first coding task is ONLY:

```text
USER INPUT
    ↓
Learner Profile
    ↓
Gemini Lesson Planner
    ↓
Structured Lesson Plan
    ↓
Frontend Display
```

Do NOT include in the first phase:

- Avatar
- TTS
- Video generation
- RAG
- Database
- Authentication
- Final assessment

They will be added incrementally.

---

# 40. CURSOR OPERATING RULES

Cursor is the single coding environment.

The AI must:

1. Read this master context before coding.
2. Work on one phase at a time.
3. Not implement future phases unless explicitly requested.
4. Not change the chosen technology stack without approval.
5. Not create enterprise architecture.
6. Not create unnecessary agents.
7. Not add authentication/database/microservices unless explicitly approved.
8. Not rewrite unrelated working files.
9. Prefer simple reliable implementations.
10. Before editing, tell the user which files will change.
11. After editing, tell the user how to run and test the result.
12. Preserve the hackathon's high-scoring requirements.
13. Treat this file and the original challenge as the source of truth.

---

# 41. SUGGESTED CURSOR MASTER INSTRUCTION

Use the following as a persistent project instruction / `AGENTS.md`-style rule:

```text
You are the implementation engineer for the AI Teacher Hackathon 2026 project.

Read the project master context before making changes.

The original challenge is authoritative.

Core teaching loop:
Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue

This is not a chatbot.

Prioritize:
1. Human-like teaching and adaptation
2. AI/LLM implementation
3. RAG and knowledge grounding
4. AI teaching video
5. Multilingual capability
6. Voice + avatar

Rules:
- Work one implementation phase at a time.
- Do not implement future phases unless explicitly asked.
- Do not over-engineer.
- Do not add microservices, queues, database infrastructure, auth, or unnecessary agents.
- Do not change technology choices without approval.
- Do not rewrite unrelated working code.
- Prefer a simple reliable hackathon implementation.
- Keep Gemini API keys secret and use .env.
- Always preserve a working end-to-end demo path.
- Before code changes, list intended files.
- After code changes, provide exact run/test commands.
```

---

# 42. PREVIOUS INITIAL CURSOR PROMPT — PHASE 1

This was the intended initial coding prompt:

```text
We are building a hackathon MVP called:

AI Teacher — Adaptive Human-Like AI Educator

This is a time-critical hackathon project.

We must prioritize:
WORKING > PERFECT
DEMONSTRABLE > COMPLETE
HIGH-SCORING FEATURES > EXTRA FEATURES

Do NOT over-engineer.
Do NOT introduce:
- Microservices
- Authentication
- Complex databases
- Docker
- Queues
- Multiple AI agents
- Enterprise architecture
- Unnecessary abstractions

We need the smallest working architecture that demonstrates:
Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue

The LLM is Gemini.
Gemini API is already tested and working.
Python environment is working.
API key is stored in .env.
Never expose the API key.

PHASE 1 ONLY:
Build the first vertical slice:
USER INPUT
↓
Learner Profile
↓
Gemini Lesson Planner
↓
Structured Lesson Plan JSON
↓
Display Lesson Plan in UI

Do NOT build:
- Avatar
- TTS
- Video generation
- PDF RAG yet
- Database
- Authentication
- Final assessment

Tech stack:
Frontend: React + Vite
Backend: FastAPI + Python
LLM: Gemini API using google-genai
State: in-memory
Styling: modern simple CSS

UI fields:
1. Topic
2. Learner Level: Beginner / Intermediate / Advanced
3. Language: English default
4. Available Time: 5 / 20 / 60
5. Learning Goal

Button:
Create My Lesson

Backend endpoint:
POST /api/lesson-plan

Request:
{
  "topic": "Newton's Laws of Motion",
  "learner_level": "Beginner",
  "language": "English",
  "available_time_minutes": 20,
  "learning_goal": "Understand the basics"
}

Lesson plan JSON:
{
  "title": "",
  "learner_level": "",
  "language": "",
  "total_duration_minutes": 0,
  "learning_objectives": [],
  "segments": [
    {
      "id": 1,
      "title": "",
      "concept": "",
      "duration_minutes": 0,
      "teaching_goal": "",
      "key_points": [],
      "example": "",
      "visual_type": "",
      "interaction_required": true
    }
  ]
}

Gemini must adapt complexity to learner level, respect available time, teach progressively, include examples, choose appropriate visual types, insert interaction points, and avoid trying to cover too much.

Keep project structure minimal.

START WITH PHASE 1 ONLY.
Do not build future phases.
```

---

# 43. UI/UX DIRECTION

The product should look and feel like an educational platform rather than a generic AI chatbot.

## Screen 1 — Start Learning

Inputs:
- Topic or upload
- Level
- Language
- Time
- Goal

## Screen 2 — Personalized Lesson Plan

Show:
- lesson title
- objectives
- segments
- timing
- questions planned

## Screen 3 — Teaching Room

This is the most important interface.

Conceptually:

```text
┌───────────────────────────────────────┐
│                                       │
│         VISUAL / TEACHING AREA       │
│                                       │
│              AI TEACHER              │
│                                       │
├───────────────────────────────────────┤
│ Current Concept                       │
│ Teacher explanation                  │
├───────────────────────────────────────┤
│ Student response / interaction       │
└───────────────────────────────────────┘
```

The visual area and teacher/avatar area should work together.

## Screen 4 — Question

Show the teacher question and answer input.

## Screen 5 — Adaptive Feedback

The teacher should explain the error constructively, not merely show a red "wrong".

## Screen 6 — Learning Report

Show:
- score
- strong concepts
- weak concepts
- misconceptions
- recommendation
- next topic

---

# 44. DEMO STORY

Recommended exact story:

### User setup

```text
Topic/material: Electricity / Ohm's Law
Level: Beginner
Language: Hindi or Hinglish
Time: 20 minutes
Goal: Understand the concept and test understanding
```

### Teacher

Generates a plan.

### Teaching

Explains voltage, current, resistance, and Ohm's Law with a suitable visual.

### Interaction

Teacher asks:

> What happens to current if resistance increases while voltage remains constant?

### Deliberately wrong demo answer

> Current increases.

### AI behavior

Detects misconception:
- student is treating current and resistance as directly proportional under constant voltage.

Then:
- explains the inverse relationship again.
- uses a different analogy.
- provides another example/visual.
- asks another question.

### Student

Answers correctly.

### Final assessment

3–5 questions.

### Report

Shows:
- score
- strengths
- weak concepts
- recommendation
- next topic

This is intentionally aligned with the challenge's own example.

---

# 45. CRITICAL RISKS AND FALLBACKS

## Risk: Avatar API unavailable or too slow

Fallback:
- cache/pre-generate demo segments
- use a recorded demo as backup
- use a simpler avatar/video presentation while keeping the AI teaching logic live

## Risk: TTS poor in Hindi

Fallback:
- try a different voice/provider
- retain English live path if necessary while preserving a recorded Hindi demo

## Risk: RAG hallucination

Mitigation:
- answer only from retrieved context for uploaded-material mode
- say "insufficient information in the provided material" when context is insufficient
- show retrieved source snippets in UI for transparency

## Risk: Video generation too slow

Fallback:
- avatar video only for intro/key/misconception moments
- routine segments = TTS + visual slide
- cache demo assets

## Risk: Time runs out

Cut P2 features.

A rough but complete teaching loop is better than a polished partial application.

## Risk: Live internet/API failure

A recorded backup demo video is mandatory.

---

# 46. WHAT NOT TO DO

Do not:

- Build a generic chatbot.
- Spend hours on authentication.
- Build a full LMS.
- Build a complex database.
- Build microservices.
- Train a custom LLM.
- Build custom lip-sync.
- Support every document format before PDF works.
- Build all advanced features before P0 works.
- Let different AI tools independently change the architecture.
- Keep changing the technology stack.
- Spend hours polishing UI before the teaching loop works.
- Generate a huge codebase in one prompt.

---

# 47. DECISION RULE FOR EVERY FEATURE

Before implementing any new feature, ask:

1. Does it satisfy a mandatory hackathon requirement?
2. Does it directly improve a high-weight scoring area?
3. Can it be implemented safely within the remaining time?
4. Will it help the end-to-end demo?

If the answer is mostly no, defer it.

---

# 48. HOW THE AI ASSISTANTS SHOULD BE USED

## ChatGPT

Do not use ChatGPT primarily to dump giant codebases.

Use it to:
- direct the project
- review Cursor output
- troubleshoot errors
- make architecture decisions
- keep the project focused
- interpret hackathon requirements

## Cursor

Use it to:
- implement the current task
- modify files
- run code
- debug

## Gemini API

Use it inside the application as the actual Teacher Brain.

---

# 49. EFFICIENT AI WORK STYLE

Bad prompt:

> Build the whole AI Teacher.

Better prompt:

> Read the master context. Implement Phase 1 only. Do not touch future phases.

Then test.

Then:

> Implement Phase 2 only.

Then test.

Use incremental vertical slices.

Do not repeat the entire 30-page context in every prompt if the AI can read the project files. Keep permanent rules in project instructions and only provide the current task.

---

# 50. ORIGINAL PROJECT DIRECTION DECISION

The user considered using Claude, Cursor, Antigravity, and Gemini.

The final simplification was:

### One coding environment only:
**Antigravity**

Antigravity = the ONE coding environment for this project.

- ChatGPT = Project Director / reviewer.
- Claude Sonnet 4.6 in Antigravity = Implementation engineer.
- Gemini API = AI brain inside the application.

Do not use Cursor and Antigravity to modify the same codebase.

This separation was chosen specifically because the user does not want to be overwhelmed with multiple coding environments or conflicting implementations.

---

# 51. CHATGPT PROJECT SETUP RECOMMENDATION

Create a dedicated ChatGPT Project:

# AI Teacher Hackathon 2026

Suggested main conversation:

**AI Teacher — Master Build**

Upload this file and the original hackathon material to that Project.

The Project should act as the persistent control center for:

- requirements
- architecture
- implementation progress
- debugging
- design decisions
- demo strategy
- submission preparation

Do not create many separate chats immediately.

---

# 52. PROJECT CONTEXT MANAGEMENT RULE

The project must distinguish between:

## Authoritative source

The original hackathon challenge.

## Strategic interpretation

This master context and approved project decisions.

## Implementation state

What currently works in the repository.

## Experimental ideas

Things considered but not yet approved.

A coding AI must not treat experimental ideas as confirmed requirements.

---

# 53. CURRENT IMPLEMENTATION MILESTONE

Completed:

- Hackathon challenge fully understood.
- MVP priorities identified.
- Architecture concept established.
- ChatGPT selected as project director.
- Cursor selected as sole coding environment.
- Gemini selected as application LLM.
- Gemini API key created.
- Python package installation completed.
- `.env` loading tested.
- Gemini API text generation tested successfully.

Not yet completed:

- Main `ai-teacher` application scaffold
- Lesson Planner vertical slice
- RAG implementation
- Teaching UI
- Adaptive teaching loop in code
- TTS validation
- Avatar validation
- Video pipeline
- Final assessment implementation
- Learning report implementation
- Deployment
- Backup demo recording
- Final documentation

---

# 54. IMMEDIATE NEXT ACTION

The next action is NOT to write the entire application.

First:

1. Open `C:\Users\techo\OneDrive\Desktop\AI teach\ai-teacher` in Cursor.
2. Put the master context into the project.
3. Create minimal backend/frontend scaffolding.
4. Build Phase 1 only:
   - topic
   - learner profile
   - Gemini lesson planner
   - structured JSON
   - frontend lesson-plan display
5. Run it successfully.
6. Only then proceed to teaching segments and RAG.

Before committing significant time to media generation, validate:
- avatar access
- TTS access

---

# 55. MASTER PRINCIPLE

Everything in the project should reinforce this:

# DO NOT BUILD AN AI THAT ANSWERS QUESTIONS.
# BUILD AN AI THAT MAKES TEACHING DECISIONS.

The final system should visibly demonstrate:

```text
Understand
   ↓
Plan
   ↓
Explain
   ↓
Demonstrate
   ↓
Question
   ↓
Evaluate
   ↓
Adapt
   ↓
Continue
```

That is the central identity of this project and the strongest interpretation of the challenge.

---

# 56. QUICK REFERENCE — ONE-PAGE VERSION

## Problem
Build an AI teacher that teaches through video and behaves like a human educator.

## High-score areas
1. Human-like teaching/adaptation — 20
2. AI/LLM — 15
3. RAG — 15
4. Teaching video — 15
5. Multilingual — 10
6. Voice/avatar — 10

## Core demo
Physics/Ohm's Law -> Beginner -> Hindi/Hinglish -> 20 min -> lesson plan -> avatar/voice -> visual -> question -> intentionally wrong answer -> misconception detection -> alternative explanation -> new question -> final quiz -> report.

## Core stack
React + Vite / FastAPI / Gemini API / local multilingual embeddings / FAISS / validated TTS / validated avatar.

## Coding tool
Cursor only.

## Project director
ChatGPT.

## Application AI
Gemini.

## API status
Gemini key works; `gemini-3.6-flash` confirmed working for the tested key.

## Main rule
One phase at a time. Never overbuild.

## Deadline
5 September 2026, 5:00 PM IST.

