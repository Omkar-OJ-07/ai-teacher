import { API_URL } from '../api.js'
import { useState, useEffect, useRef } from 'react'
import VisualPanel from './VisualPanel.jsx'
import TeacherAvatar from './TeacherAvatar.jsx'

/**
 * TeachingSession — Phase 2 adaptive teaching loop (Phase 2.1 upgraded).
 *
 * New in 2.1:
 *   - Reads from prefetchCacheRef (instant display when cache is ready)
 *   - Triggers prefetch of next segment after segment loads
 *   - "Give Up & Reveal Answer" button after first genuine attempt
 *   - Demo score/progress system (+10/+7/+5/+0)
 *   - Suspicious-answer heuristic (playful, non-accusatory)
 *   - Improved loading messages for retry transparency
 */

const STATUS = {
  LOADING:       'loading',
  TEACHING:      'teaching',
  EVALUATING:    'evaluating',
  CORRECT:       'correct',
  PARTIAL:       'partial',
  MISCONCEPTION: 'misconception',
  REVEALED:      'revealed',
  COMPLETE:      'complete',
  ERROR:         'error',
}

// ── Scoring constants ────────────────────────────────────────
const SCORE = {
  FIRST_ATTEMPT:  10,
  AFTER_FOLLOWUP:  7,
  AFTER_RETEACH:   5,
  REVEALED:        0,
}

// ── Suspicious-answer heuristic ─────────────────────────────
// Checks for unusually formal / polished / AI-like patterns.
// Returns a string if suspicious, null otherwise.
// This NEVER affects classification — it is a playful nudge only.
const SUSPICIOUS_PATTERNS = [
  /\b(furthermore|moreover|in conclusion|it is worth noting|it should be noted)\b/i,
  /\b(pertaining to|with respect to|in the context of|one must consider)\b/i,
  /\bin summary,?\s/i,
  /\bthis concept (can be|is best|may be) (understood|described|explained) as\b/i,
  /^(certainly|absolutely|of course|indeed),/i,
]

function detectSuspiciousAnswer(text) {
  if (!text || text.trim().length < 30) return null
  const matchCount = SUSPICIOUS_PATTERNS.filter(p => p.test(text)).length
  if (matchCount >= 1) {
    const msgs = [
      "🤨 That answer sounds suspiciously polished! If an AI helped you, make sure it teaches you something too 😄",
      "✨ Very eloquent! If you used an AI assistant, try also explaining it in your own words — that's where real learning happens.",
      "🧐 Impressively formal! Make sure you understand this in your own words, not just in textbook language.",
    ]
    return msgs[Math.floor(Math.random() * msgs.length)]
  }
  return null
}

let _msgId = 0
function newMsg(role, text, kind = 'text') {
  _msgId += 1
  return { id: _msgId, role, text, kind }
}

function buildAskQuestionPayload(plan, seg, teachingContent, question, history) {
  return {
    topic: plan.title,
    segment_title: seg.title,
    concept: seg.concept,
    teaching_goal: seg.teaching_goal,
    explanation: teachingContent?.explanation || '',
    key_points: teachingContent?.key_points || [],
    example: teachingContent?.example || '',
    learner_level: plan.learner_level,
    language: plan.language,
    student_question: question,
    conversation_history: history.slice(-6).map(m => ({
      role: m.role === 'teacher' ? 'teacher' : 'student',
      content: m.text,
    })),
  }
}

function buildTeachingPayload(plan, seg) {
  return {
    topic: plan.title,
    lesson_title: plan.title,
    segment_id: seg.id,
    segment_title: seg.title,
    concept: seg.concept,
    teaching_goal: seg.teaching_goal,
    key_points: seg.key_points,
    example: seg.example,
    visual_type: seg.visual_type,
    learner_level: plan.learner_level,
    language: plan.language,
  }
}

export default function TeachingSession({ plan, prefetchCacheRef, prefetchSegment, onBack }) {
  const [segmentIndex, setSegmentIndex] = useState(0)
  const [teachingContent, setTeachingContent] = useState(null)

  const [activeQuestion, setActiveQuestion]   = useState('')
  const [expectedAnswer, setExpectedAnswer]   = useState('')
  const [acceptablePoints, setAcceptablePoints] = useState([])

  const [studentAnswer, setStudentAnswer]  = useState('')
  const [evaluation, setEvaluation]        = useState(null)
  const [attemptCount, setAttemptCount]    = useState(1)
  const [hasAttempted, setHasAttempted]    = useState(false)
  const [suspiciousMsg, setSuspiciousMsg]  = useState(null)
  const [showGiveUpConfirm, setShowGiveUpConfirm] = useState(false)

  // Score across all segments
  const [totalScore, setTotalScore]        = useState(0)
  const [segmentOutcome, setSegmentOutcome] = useState(null) // 'first'|'followup'|'reteach'|'revealed'

  const [status, setStatus]     = useState(STATUS.LOADING)
  const [errorMsg, setErrorMsg] = useState('')
  const [loadingMsg, setLoadingMsg] = useState('Your AI teacher is preparing your lesson...')

  // ── Conversation (persistent chat history for this segment) ──
  const [messages, setMessages] = useState([])
  const [chatDraft, setChatDraft] = useState('')
  const [chatSending, setChatSending] = useState(false)
  const [chatError, setChatError] = useState('')
  const chatEndRef = useRef(null)

  // ── Voice (browser-native Web Speech API — no external API/key) ──
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [voicesReady, setVoicesReady] = useState(false)
  const voiceSupported = typeof window !== 'undefined' && 'speechSynthesis' in window
  const speechQueueRef = useRef([])

  const feedbackRef = useRef(null)

  const totalSegments = plan.segments.length
  const currentSegment = plan.segments[segmentIndex]

  useEffect(() => { loadTeachingContent() }, [segmentIndex])

  useEffect(() => {
    if ([STATUS.CORRECT, STATUS.PARTIAL, STATUS.MISCONCEPTION, STATUS.REVEALED].includes(status)) {
      setTimeout(() => feedbackRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100)
    }
  }, [status])

  // ── Load teaching content (cache-aware) ─────────────────────
  async function loadTeachingContent() {
    setStatus(STATUS.LOADING)
    setLoadingMsg('Your AI teacher is preparing your lesson...')
    setErrorMsg('')
    setStudentAnswer('')
    setEvaluation(null)
    setAttemptCount(1)
    setHasAttempted(false)
    setSuspiciousMsg(null)
    setShowGiveUpConfirm(false)
    setSegmentOutcome(null)
    setMessages([])
    setChatDraft('')
    setChatError('')

    const seg = plan.segments[segmentIndex]
    const key = `${plan.title}::${seg.id}::${seg.concept}`
    const cache = prefetchCacheRef?.current

    try {
      let content = null

      if (cache?.has(key)) {
        const entry = cache.get(key)
        if (entry.status === 'ready') {
          content = entry.content
        } else if (entry.status === 'loading' && entry.promise) {
          setLoadingMsg('Your AI teacher is almost ready...')
          content = await entry.promise
        }
        // entry.status === 'error' falls through to a fresh fetch below
      }

      if (!content) {
        setLoadingMsg('Connecting to your AI teacher...')
        const res = await fetch(`${API_URL}/api/start-teaching`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(buildTeachingPayload(plan, seg)),
        })
        if (!res.ok) {
          const body = await res.json().catch(() => ({}))
          throw new Error(body.detail || 'Failed to load teaching content.')
        }
        content = await res.json()
      }

      applyTeachingContent(content)

      // Prefetch next segment in background
      if (prefetchSegment && segmentIndex + 1 < totalSegments) {
        prefetchSegment(segmentIndex + 1, plan)
      }
    } catch (err) {
      setLoadingMsg('')
      setErrorMsg(err.message || 'Failed to connect to AI Teacher.')
      setStatus(STATUS.ERROR)
    }
  }

  function applyTeachingContent(content) {
    setTeachingContent(content)
    setActiveQuestion(content.question.prompt)
    setExpectedAnswer(content.correct_answer)
    setAcceptablePoints(content.acceptable_answer_points || [])
    setStatus(STATUS.TEACHING)
    setMessages([
      newMsg('teacher', content.explanation, 'explanation'),
      newMsg('teacher', content.question.prompt, 'question'),
    ])
  }

  // ── Ask the teacher a free-form question (context-aware chat) ──
  async function handleAskQuestion() {
    const question = chatDraft.trim()
    if (!question || chatSending) return
    setChatDraft('')
    setChatError('')
    const historySnapshot = messages
    setMessages(prev => [...prev, newMsg('student', question, 'chat')])
    setChatSending(true)
    try {
      const res = await fetch(`${API_URL}/api/ask-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          buildAskQuestionPayload(plan, currentSegment, teachingContent, question, historySnapshot)
        ),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || 'Failed to get an answer.')
      }
      const data = await res.json()
      setMessages(prev => [...prev, newMsg('teacher', data.answer, data.source === 'fallback' ? 'chat-fallback' : 'chat')])
    } catch (err) {
      setChatError(err.message || 'Failed to reach your AI teacher. Please try again.')
    } finally {
      setChatSending(false)
      setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50)
    }
  }

  // ── Voice: speak the current explanation aloud ───────────────
  // Uses window.speechSynthesis (Web Speech API) — zero cost, zero
  // external dependency, works entirely client-side. This is a
  // disclosed MVP substitute for a full generated-voice pipeline.
  // Load available voices — Chrome/Edge populate this list asynchronously,
  // so we must wait for the 'voiceschanged' event rather than reading it once.
  useEffect(() => {
    if (!voiceSupported) return
    function loadVoices() {
      if (window.speechSynthesis.getVoices().length > 0) setVoicesReady(true)
    }
    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
    return () => { window.speechSynthesis.onvoiceschanged = null }
  }, [voiceSupported])

  // Map the lesson language to a BCP-47 locale prefix for voice matching.
  function langueLocalePrefix() {
    switch (plan.language) {
      case 'Hindi':    return 'hi'
      case 'Hinglish': return 'hi' // closest available browser voice; text itself is mixed
      default:         return 'en'
    }
  }

  // Pick the best available voice: prefer a matching-language voice that
  // looks like a higher-quality "Natural"/"Neural"/"Google" voice over the
  // generic OS default, but gracefully fall back if none match.
  function pickBestVoice() {
    if (!voiceSupported) return null
    const voices = window.speechSynthesis.getVoices()
    if (!voices.length) return null
    const prefix = langueLocalePrefix()
    const sameLang = voices.filter(v => v.lang?.toLowerCase().startsWith(prefix))
    const pool = sameLang.length ? sameLang : voices.filter(v => v.lang?.toLowerCase().startsWith('en'))
    const qualityRank = v => {
      const n = v.name.toLowerCase()
      if (n.includes('neural')) return 3
      if (n.includes('natural')) return 3
      if (n.includes('google')) return 2
      if (v.localService === false) return 1
      return 0
    }
    const finalPool = pool.length ? pool : voices
    return [...finalPool].sort((a, b) => qualityRank(b) - qualityRank(a))[0] || voices[0]
  }

  function stopSpeech() {
    if (voiceSupported) window.speechSynthesis.cancel()
    speechQueueRef.current = []
    setIsSpeaking(false)
    setIsPaused(false)
  }

  function togglePauseSpeech() {
    if (!voiceSupported) return
    if (isPaused) {
      window.speechSynthesis.resume()
      setIsPaused(false)
    } else {
      window.speechSynthesis.pause()
      setIsPaused(true)
    }
  }

  // Break long narration into natural sentence-level chunks and speak them
  // sequentially. This avoids the common Web Speech API bug where very long
  // utterances cut off partway through, and produces more natural pausing.
  function speakExplanation() {
    if (!voiceSupported || !teachingContent?.explanation) return
    window.speechSynthesis.cancel()

    const chunks = teachingContent.explanation
      .split(/(?<=[.!?।])\s+/) // '।' = Hindi danda sentence terminator
      .map(s => s.trim())
      .filter(Boolean)
    if (!chunks.length) return

    speechQueueRef.current = chunks
    const voice = pickBestVoice()
    setIsSpeaking(true)
    setIsPaused(false)

    function speakNext() {
      const text = speechQueueRef.current.shift()
      if (!text) { setIsSpeaking(false); return }
      const utterance = new SpeechSynthesisUtterance(text)
      if (voice) utterance.voice = voice
      utterance.lang = voice?.lang || (langueLocalePrefix() === 'hi' ? 'hi-IN' : 'en-US')
      utterance.rate = 0.96
      utterance.pitch = 1.0
      utterance.onend = () => speakNext()
      utterance.onerror = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    }
    speakNext()
  }

  // Cancel any in-progress speech whenever the segment changes or on unmount
  useEffect(() => {
    return () => { if (voiceSupported) window.speechSynthesis.cancel() }
  }, [segmentIndex])

  useEffect(() => {
    return () => { if (voiceSupported) window.speechSynthesis.cancel() }
  }, [])

  // ── Submit answer ────────────────────────────────────────────
  async function handleSubmitAnswer() {
    if (!studentAnswer.trim() || status === STATUS.EVALUATING) return
    stopSpeech()

    const suspicious = detectSuspiciousAnswer(studentAnswer)
    setSuspiciousMsg(suspicious)

    setMessages(prev => [...prev, newMsg('student', studentAnswer.trim(), 'answer')])
    setHasAttempted(true)
    setStatus(STATUS.EVALUATING)

    try {
      const res = await fetch(`${API_URL}/api/evaluate-answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: currentSegment.concept,
          teaching_goal: currentSegment.teaching_goal,
          question_prompt: activeQuestion,
          question_type: teachingContent?.question?.type || 'short_answer',
          correct_answer: expectedAnswer,
          acceptable_answer_points: acceptablePoints,
          student_answer: studentAnswer.trim(),
          learner_level: plan.learner_level,
          language: plan.language,
          teaching_script: teachingContent?.explanation || '',
          attempt_count: attemptCount,
        }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || 'Failed to evaluate answer.')
      }

      const result = await res.json()
      setEvaluation(result)
      setStudentAnswer('')

      const feedbackMsgs = [newMsg('teacher', result.feedback, 'feedback-' + result.classification)]
      if (result.adapted_explanation) {
        feedbackMsgs.push(newMsg('teacher', result.adapted_explanation, 'reteach-explanation'))
      }
      if (result.new_analogy) {
        feedbackMsgs.push(newMsg('teacher', result.new_analogy, 'reteach-analogy'))
      }
      if (result.follow_up_question) {
        feedbackMsgs.push(newMsg('teacher', result.follow_up_question, 'question'))
      }
      setMessages(prev => [...prev, ...feedbackMsgs])

      if (result.classification === 'correct') {
        const pts = attemptCount === 1 ? SCORE.FIRST_ATTEMPT
          : segmentOutcome === 'reteach' ? SCORE.AFTER_RETEACH
          : SCORE.AFTER_FOLLOWUP
        setTotalScore(s => s + pts)
        setSegmentOutcome(attemptCount === 1 ? 'first' : segmentOutcome || 'followup')
        setStatus(STATUS.CORRECT)
      } else if (result.classification === 'partial') {
        if (result.follow_up_question) {
          setActiveQuestion(result.follow_up_question)
          setExpectedAnswer(result.follow_up_correct_answer || expectedAnswer)
          setAcceptablePoints(result.follow_up_acceptable_points?.length
            ? result.follow_up_acceptable_points : acceptablePoints)
        }
        setSegmentOutcome('followup')
        setAttemptCount(prev => prev + 1)
        setStatus(STATUS.PARTIAL)
      } else {
        if (result.follow_up_question) {
          setActiveQuestion(result.follow_up_question)
          setExpectedAnswer(result.follow_up_correct_answer || expectedAnswer)
          setAcceptablePoints(result.follow_up_acceptable_points?.length
            ? result.follow_up_acceptable_points : acceptablePoints)
        }
        setSegmentOutcome('reteach')
        setAttemptCount(prev => prev + 1)
        setStatus(STATUS.MISCONCEPTION)
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to evaluate answer. Please try again.')
      setStatus(STATUS.TEACHING)
    }
  }

  // ── Give up / reveal answer ──────────────────────────────────
  function handleGiveUp() {
    if (!hasAttempted) return
    setShowGiveUpConfirm(true)
  }

  function handleConfirmGiveUp() {
    setShowGiveUpConfirm(false)
    setTotalScore(s => s + SCORE.REVEALED) // +0, but explicit
    setSegmentOutcome('revealed')
    setStatus(STATUS.REVEALED)
    setMessages(prev => [...prev, newMsg('teacher', `The answer is: ${expectedAnswer}`, 'revealed')])
  }

  function handleCancelGiveUp() {
    setShowGiveUpConfirm(false)
  }

  // ── Continue to next segment ─────────────────────────────────
  function handleContinue() {
    if (segmentIndex + 1 < totalSegments) {
      setSegmentIndex(prev => prev + 1)
    } else {
      setStatus(STATUS.COMPLETE)
    }
  }

  // ── Score label ──────────────────────────────────────────────
  function renderScoreBadge() {
    return (
      <div className="ts-score-badge" title="Demo score — not an academic grade">
        ⭐ {totalScore} pts
      </div>
    )
  }

  // ── Answer input ─────────────────────────────────────────────
  function renderAnswerInput(placeholder = 'Type your answer here...', inFeedback = false) {
    const idle = status !== STATUS.EVALUATING
    return (
      <div className="answer-section">
        {suspiciousMsg && idle && (
          <div className="suspicious-notice">{suspiciousMsg}</div>
        )}
        <textarea
          className="answer-textarea"
          placeholder={placeholder}
          value={studentAnswer}
          onChange={e => setStudentAnswer(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmitAnswer() }}
          rows={3}
          disabled={status === STATUS.EVALUATING}
        />
        <div className="answer-footer">
          <span className="answer-hint">Ctrl+Enter to submit</span>
          <div className="answer-actions">
            {hasAttempted && !inFeedback && (
              <button
                className="btn-give-up"
                onClick={handleGiveUp}
                disabled={status === STATUS.EVALUATING}
              >
                ⚠ Give Up & Reveal
              </button>
            )}
            <button
              className="btn-submit-answer"
              onClick={handleSubmitAnswer}
              disabled={!studentAnswer.trim() || status === STATUS.EVALUATING}
            >
              {status === STATUS.EVALUATING ? '⏳ Evaluating...' : 'Submit Answer →'}
            </button>
          </div>
        </div>
        {errorMsg && status === STATUS.TEACHING && (
          <div className="ts-inline-error">⚠ {errorMsg}</div>
        )}
      </div>
    )
  }

  // ═══════════════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════════════

  if (status === STATUS.LOADING) {
    return (
      <div className="ts-shell">
        <div className="ts-loading">
          <div className="spinner" />
          <h3>{loadingMsg}</h3>
          <p>This usually takes a few seconds.</p>
        </div>
      </div>
    )
  }

  if (status === STATUS.ERROR) {
    return (
      <div className="ts-shell">
        <div className="ts-error">
          <div className="ts-error-icon">⚠️</div>
          <h3>Something went wrong</h3>
          <p>{errorMsg}</p>
          <div className="ts-error-actions">
            <button className="btn-primary" onClick={loadTeachingContent}>Try Again</button>
            <button className="btn-secondary" onClick={onBack}>← Back to Plan</button>
          </div>
        </div>
      </div>
    )
  }

  if (status === STATUS.COMPLETE) {
    return (
      <div className="ts-shell">
        <div className="ts-complete">
          <div className="ts-complete-icon">🎉</div>
          <h2>Lesson Complete!</h2>
          <p>You finished all {totalSegments} segment{totalSegments !== 1 ? 's' : ''} of <strong>{plan.title}</strong>.</p>
          {totalScore > 0 && (
            <div className="ts-final-score">
              ⭐ Final Score: <strong>{totalScore}</strong> / {totalSegments * SCORE.FIRST_ATTEMPT} pts
              <div className="ts-score-note">Demo metric only — not an academic grade</div>
            </div>
          )}
          <button className="btn-primary" onClick={onBack} style={{ marginTop: '1.5rem' }}>
            ← Back to Lesson Plan
          </button>
        </div>
      </div>
    )
  }

  const progressPercent = ((segmentIndex + (status === STATUS.CORRECT || status === STATUS.REVEALED ? 1 : 0)) / totalSegments) * 100

  // ── Derive avatar state from app status + speech state ────────
  let avatarState = 'idle'
  if (status === STATUS.EVALUATING || chatSending) avatarState = 'thinking'
  else if (status === STATUS.CORRECT) avatarState = 'correct'
  else if (status === STATUS.PARTIAL) avatarState = 'encouraging'
  else if (status === STATUS.MISCONCEPTION) avatarState = 'misconception'
  else if (isSpeaking) avatarState = 'speaking'

  return (
    <div className="ts-shell">

      {/* Give-up confirmation modal */}
      {showGiveUpConfirm && (
        <div className="ts-modal-overlay">
          <div className="ts-modal">
            <div className="ts-modal-icon">🤔</div>
            <h3>Are you sure?</h3>
            <p>Trying to work out the answer yourself is where the real learning happens. Revealing it now means you miss that practice.</p>
            <p className="ts-modal-sub">You can still continue to the next segment after seeing the answer.</p>
            <div className="ts-modal-actions">
              <button className="btn-secondary" onClick={handleCancelGiveUp}>Keep Trying</button>
              <button className="btn-give-up-confirm" onClick={handleConfirmGiveUp}>Yes, Reveal Answer</button>
            </div>
          </div>
        </div>
      )}

      {/* Progress bar */}
      <div className="ts-progress-bar">
        <div className="ts-progress-inner" style={{ width: `${progressPercent}%` }} />
      </div>

      {/* Session header */}
      <div className="ts-header">
        <button className="ts-back-btn" onClick={onBack}>← Plan</button>
        <div className="ts-progress-label">Segment {segmentIndex + 1} of {totalSegments}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {renderScoreBadge()}
          <div className="ts-segment-dots">
            {plan.segments.map((_, i) => (
              <span key={i} className={`ts-dot ${i < segmentIndex ? 'done' : i === segmentIndex ? 'active' : ''}`} />
            ))}
          </div>
        </div>
      </div>

      {/* Teacher avatar + concept header */}
      <div className="ts-avatar-row">
        <TeacherAvatar state={avatarState} size={72} />
        <div className="ts-concept-header" style={{ marginBottom: 0, flex: 1 }}>
          <div className="ts-segment-num">{segmentIndex + 1}</div>
          <div>
            <div className="ts-segment-title">{currentSegment.title}</div>
            <div className="ts-segment-concept">{currentSegment.concept}</div>
          </div>
        </div>
      </div>

      {/* Teaching content */}
      {teachingContent && (
        <div className="ts-teaching-card">
          <div className="ts-section">
            <div className="ts-section-label">🧑‍🏫 Explanation</div>
            <div className="ts-explanation">{teachingContent.explanation}</div>
            {voiceSupported && (
              <div className="ts-voice-row">
                {!isSpeaking ? (
                  <button className="btn-listen" onClick={speakExplanation}>
                    🔊 Listen to Teacher
                  </button>
                ) : (
                  <>
                    <button className="btn-listen btn-listen--active" onClick={togglePauseSpeech}>
                      {isPaused ? '▶ Resume' : '⏸ Pause'}
                    </button>
                    <button className="btn-listen" onClick={stopSpeech}>
                      ⏹ Stop
                    </button>
                  </>
                )}
                {!voicesReady && <span className="ts-voice-hint">loading voices…</span>}
              </div>
            )}
          </div>

          {teachingContent.key_points?.length > 0 && (
            <div className="ts-section">
              <div className="ts-section-label">📌 Key Points</div>
              <ul className="ts-key-points">
                {teachingContent.key_points.map((pt, i) => (
                  <li key={i} className="ts-key-point">{pt}</li>
                ))}
              </ul>
            </div>
          )}

          {teachingContent.example && (
            <div className="ts-section">
              <div className="ts-section-label">💡 Example</div>
              <div className="ts-example">{teachingContent.example}</div>
            </div>
          )}

          <div className="ts-section">
            <VisualPanel visualSpec={teachingContent.visual_spec} />
          </div>

          {(status === STATUS.TEACHING || status === STATUS.EVALUATING) && (
            <div className="ts-section ts-question-section">
              <div className="ts-section-label">💬 Check Your Understanding</div>
              <div className="ts-question-text">{activeQuestion}</div>
              {renderAnswerInput()}
            </div>
          )}
        </div>
      )}

      {/* Conversation with the AI Teacher */}
      {teachingContent && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            <span className="chat-panel-title">🗨 Conversation with your AI Teacher</span>
            <span className="chat-panel-sub">Ask a question any time — it stays on this concept</span>
          </div>
          <div className="chat-log">
            {messages.map(m => (
              <div key={m.id} className={`chat-bubble chat-bubble--${m.role}`}>
                <span className="chat-bubble-author">{m.role === 'teacher' ? '🧑‍🏫 AI Teacher' : '🙋 You'}</span>
                <span className="chat-bubble-text">{m.text}</span>
                {m.kind === 'chat-fallback' && (
                  <span className="chat-bubble-tag" title="AI service was unavailable — this is a deterministic fallback answer">offline fallback</span>
                )}
              </div>
            ))}
            {chatSending && (
              <div className="chat-bubble chat-bubble--teacher chat-bubble--pending">
                <span className="chat-bubble-author">🧑‍🏫 AI Teacher</span>
                <span className="chat-typing"><span/><span/><span/></span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          {chatError && <div className="ts-inline-error">⚠ {chatError}</div>}
          <div className="chat-input-row">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask your AI teacher a question about this concept…"
              value={chatDraft}
              onChange={e => setChatDraft(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleAskQuestion() }}
              maxLength={1000}
              disabled={chatSending}
            />
            <button
              className="chat-send-btn"
              onClick={handleAskQuestion}
              disabled={!chatDraft.trim() || chatSending}
            >
              {chatSending ? '…' : 'Ask →'}
            </button>
          </div>
        </div>
      )}

      {/* Feedback panels */}
      <div ref={feedbackRef}>

        {/* CORRECT */}
        {status === STATUS.CORRECT && evaluation && (
          <div className="ts-feedback ts-feedback--correct">
            <div className="ts-feedback-header">
              <span className="ts-feedback-icon">✓</span>
              <span className="ts-feedback-title">
                Well done!
                {segmentOutcome === 'first' && <span className="ts-score-inline"> +{SCORE.FIRST_ATTEMPT} pts</span>}
                {segmentOutcome === 'followup' && <span className="ts-score-inline"> +{SCORE.AFTER_FOLLOWUP} pts</span>}
                {segmentOutcome === 'reteach' && <span className="ts-score-inline"> +{SCORE.AFTER_RETEACH} pts</span>}
              </span>
            </div>
            <div className="ts-feedback-body">
              <p className="ts-feedback-text">{evaluation.feedback}</p>
            </div>
            <div className="ts-feedback-actions">
              <button className="btn-continue" onClick={handleContinue}>
                {segmentIndex + 1 < totalSegments
                  ? `Continue to Segment ${segmentIndex + 2} →`
                  : 'Complete Lesson ✓'}
              </button>
            </div>
          </div>
        )}

        {/* PARTIAL */}
        {status === STATUS.PARTIAL && evaluation && (
          <div className="ts-feedback ts-feedback--partial">
            <div className="ts-feedback-header">
              <span className="ts-feedback-icon">△</span>
              <span className="ts-feedback-title">Almost there — let's strengthen this</span>
            </div>
            <div className="ts-feedback-body">
              <p className="ts-feedback-text">{evaluation.feedback}</p>
            </div>
            {evaluation.follow_up_question && (
              <div className="ts-reteach-question">
                <div className="ts-section-label">💬 Let's try another angle</div>
                <div className="ts-question-text">{activeQuestion}</div>
                {renderAnswerInput('Refine your answer...', true)}
                <div className="ts-give-up-row">
                  <button className="btn-give-up" onClick={handleGiveUp}>⚠ Give Up & Reveal Answer</button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MISCONCEPTION */}
        {status === STATUS.MISCONCEPTION && evaluation && (
          <div className="ts-feedback ts-feedback--misconception">
            <div className="ts-feedback-header">
              <span className="ts-feedback-icon">↻</span>
              <span className="ts-feedback-title">Let's look at this differently</span>
            </div>
            <div className="ts-feedback-body">
              <p className="ts-feedback-text">{evaluation.feedback}</p>
            </div>
            {evaluation.adapted_explanation && (
              <div className="ts-reteach-section">
                <div className="ts-reteach-label">🔄 New Explanation</div>
                <div className="ts-reteach-explanation">{evaluation.adapted_explanation}</div>
              </div>
            )}
            {evaluation.new_analogy && (
              <div className="ts-reteach-section">
                <div className="ts-reteach-label">💡 New Analogy</div>
                <div className="ts-reteach-analogy">
                  <span className="ts-analogy-icon">🔗</span>
                  {evaluation.new_analogy}
                </div>
              </div>
            )}
            {evaluation.follow_up_question && (
              <div className="ts-reteach-question">
                <div className="ts-section-label">💬 Let's try a new question</div>
                <div className="ts-question-text">{activeQuestion}</div>
                {renderAnswerInput('Write your answer based on the new explanation...', true)}
                <div className="ts-give-up-row">
                  <button className="btn-give-up" onClick={handleGiveUp}>⚠ Give Up & Reveal Answer</button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* REVEALED */}
        {status === STATUS.REVEALED && (
          <div className="ts-feedback ts-feedback--revealed">
            <div className="ts-feedback-header">
              <span className="ts-feedback-icon">📖</span>
              <span className="ts-feedback-title">Answer Revealed</span>
            </div>
            <div className="ts-feedback-body">
              <p className="ts-feedback-text ts-revealed-pretext">
                No worries — learning takes practice. Here is the answer for this question:
              </p>
              <div className="ts-revealed-answer">{expectedAnswer}</div>
              {acceptablePoints.length > 0 && (
                <div className="ts-revealed-points">
                  <div className="ts-reteach-label" style={{marginTop:'0.75rem'}}>Key ideas you need to understand:</div>
                  <ul className="ts-key-points" style={{marginTop:'0.4rem'}}>
                    {acceptablePoints.map((pt, i) => <li key={i} className="ts-key-point">{pt}</li>)}
                  </ul>
                </div>
              )}
              <p className="ts-revealed-nudge">
                💪 Try to understand why this is the answer, not just memorise it. That's what will help you next time.
              </p>
            </div>
            <div className="ts-feedback-actions">
              <button className="btn-continue btn-continue--revealed" onClick={handleContinue}>
                {segmentIndex + 1 < totalSegments
                  ? `Continue to Segment ${segmentIndex + 2} →`
                  : 'Finish Lesson →'}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
