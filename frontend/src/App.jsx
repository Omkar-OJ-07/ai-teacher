import { useState } from 'react'
import LessonForm from './components/LessonForm.jsx'
import LessonPlanView from './components/LessonPlanView.jsx'

/**
 * App — top-level state manager.
 *
 * States:
 *   idle    → show LessonForm
 *   loading → show loading indicator inside LessonForm
 *   plan    → show LessonPlanView with the returned lesson plan
 *   error   → show error message inside LessonForm, allow retry
 */
export default function App() {
  const [lessonPlan, setLessonPlan] = useState(null)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)

  async function handleSubmit(formData) {
    setLoading(true)
    setError(null)
    setLessonPlan(null)

    try {
      const res = await fetch('/api/lesson-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        let detail = 'Failed to generate lesson plan. Please try again.'
        try {
          const body = await res.json()
          if (body.detail) detail = body.detail
        } catch { /* ignore parse errors */ }
        throw new Error(detail)
      }

      const data = await res.json()
      setLessonPlan(data)
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

  function handleReset() {
    setLessonPlan(null)
    setError(null)
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

      <main className="app-main">
        {lessonPlan ? (
          <LessonPlanView plan={lessonPlan} onBack={handleReset} />
        ) : (
          <LessonForm
            onSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        )}
      </main>
    </div>
  )
}
