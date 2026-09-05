import { useState, useRef, useCallback } from 'react'
import LessonForm from './components/LessonForm.jsx'
import LessonPlanView from './components/LessonPlanView.jsx'
import TeachingSession from './components/TeachingSession.jsx'

/**
 * App — top-level state manager.
 *
 * States:
 *   idle     -> LessonForm
 *   loading  -> spinner inside LessonForm
 *   plan     -> LessonPlanView
 *   teaching -> TeachingSession (Phase 2)
 *
 * Phase 2.1 — Prefetch cache:
 *   prefetchCacheRef: Map<segmentKey, { status, content, promise }>
 *   Segment 0 is prefetched immediately after lesson plan is received.
 *   TeachingSession reads from cache; App provides prefetchSegment() for next segments.
 */

function buildSegmentKey(plan, segmentIdx) {
  const seg = plan.segments[segmentIdx]
  return `${plan.title}::${seg.id}::${seg.concept}`
}

function buildTeachingPayload(plan, segmentIdx) {
  const seg = plan.segments[segmentIdx]
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

export default function App() {
  const [appState, setAppState]     = useState('idle')
  const [lessonPlan, setLessonPlan] = useState(null)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)

  const prefetchCacheRef = useRef(new Map())

  const prefetchSegment = useCallback((segmentIdx, plan) => {
    if (segmentIdx < 0 || segmentIdx >= plan.segments.length) return
    const key = buildSegmentKey(plan, segmentIdx)
    const cache = prefetchCacheRef.current
    if (cache.has(key)) return

    const promise = fetch('/api/start-teaching', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildTeachingPayload(plan, segmentIdx)),
    })
      .then(res => {
        if (!res.ok) throw new Error('HTTP ' + res.status)
        return res.json()
      })
      .then(content => {
        cache.set(key, { status: 'ready', content, promise: null })
        return content
      })
      .catch(err => {
        cache.set(key, { status: 'error', content: null, promise: null })
        throw err
      })

    cache.set(key, { status: 'loading', content: null, promise })
  }, [])

  async function handleSubmit(formData) {
    setLoading(true)
    setError(null)
    setLessonPlan(null)
    prefetchCacheRef.current.clear()

    try {
      const res = await fetch('/api/lesson-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        let detail = 'Failed to generate lesson plan. Please try again.'
        try { const b = await res.json(); if (b.detail) detail = b.detail } catch {}
        throw new Error(detail)
      }

      const data = await res.json()
      setLessonPlan(data)
      setAppState('plan')
      prefetchSegment(0, data)
    } catch (err) {
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Cannot connect to the AI Teacher backend. Make sure it is running on port 8000.')
      } else {
        setError(err.message || 'Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  function handleBackToForm() {
    setLessonPlan(null)
    setError(null)
    prefetchCacheRef.current.clear()
    setAppState('idle')
  }

  function handleStartLearning() {
    setAppState('teaching')
  }

  function handleBackToPlan() {
    setAppState('plan')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <span className="header-logo">🎓</span>
          <div className="header-text">
            <h1>AI Teacher</h1>
            <p>Personalized AI-Powered Learning</p>
          </div>
        </div>
      </header>

      <main className={appState === 'teaching' ? 'app-main app-main--teaching' : 'app-main'}>
        {appState === 'idle' && (
          <LessonForm onSubmit={handleSubmit} loading={loading} error={error} />
        )}

        {appState === 'plan' && lessonPlan && (
          <LessonPlanView
            plan={lessonPlan}
            onBack={handleBackToForm}
            onStartLearning={handleStartLearning}
          />
        )}

        {appState === 'teaching' && lessonPlan && (
          <TeachingSession
            plan={lessonPlan}
            prefetchCacheRef={prefetchCacheRef}
            prefetchSegment={prefetchSegment}
            onBack={handleBackToPlan}
          />
        )}
      </main>
    </div>
  )
}
