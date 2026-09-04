import { useState } from 'react'

const LEVELS = ['Beginner', 'Intermediate', 'Advanced']
const LANGUAGES = ['English', 'Hindi', 'Hinglish']
const TIMES = [
  { value: 5,  label: '5 min'  },
  { value: 20, label: '20 min' },
  { value: 60, label: '60 min' },
]

const DEFAULTS = {
  topic: '',
  learner_level: 'Beginner',
  language: 'English',
  available_time_minutes: 20,
  learning_goal: '',
}

/**
 * LessonForm — input form for the learner profile.
 *
 * Props:
 *   onSubmit(formData) — called with validated form data
 *   loading            — bool, shows loading state when true
 *   error              — string | null, shows error message when set
 */
export default function LessonForm({ onSubmit, loading, error }) {
  const [form, setForm] = useState(DEFAULTS)

  function set(key, value) {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!form.topic.trim()) return
    if (!form.learning_goal.trim()) return
    onSubmit({
      ...form,
      topic: form.topic.trim(),
      learning_goal: form.learning_goal.trim(),
    })
  }

  if (loading) {
    return (
      <div className="lesson-form-wrapper">
        <div className="form-card">
          <div className="loading-state">
            <div className="spinner" />
            <h3>Creating your personalized lesson plan…</h3>
            <p>Gemini AI is designing a lesson tailored just for you.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lesson-form-wrapper">
      <div className="form-hero">
        <h2>Start Your Learning Journey</h2>
        <p>Tell us what you want to learn and we'll build a personalized lesson plan.</p>
      </div>

      <form className="form-card" onSubmit={handleSubmit} noValidate>

        {/* Topic */}
        <div className="form-group">
          <label htmlFor="topic">What do you want to learn?</label>
          <input
            id="topic"
            type="text"
            placeholder="e.g. Newton's Laws of Motion, Photosynthesis, React Hooks…"
            value={form.topic}
            onChange={e => set('topic', e.target.value)}
            required
            maxLength={500}
            disabled={loading}
          />
        </div>

        {/* Learner Level */}
        <div className="form-group">
          <label>Your Level</label>
          <div className="options-row">
            {LEVELS.map(level => (
              <button
                key={level}
                type="button"
                className={`option-btn ${form.learner_level === level ? 'selected' : ''}`}
                onClick={() => set('learner_level', level)}
                disabled={loading}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Language */}
        <div className="form-group">
          <label htmlFor="language">Teaching Language</label>
          <select
            id="language"
            value={form.language}
            onChange={e => set('language', e.target.value)}
            disabled={loading}
          >
            {LANGUAGES.map(lang => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>

        {/* Available Time */}
        <div className="form-group">
          <label>Available Time</label>
          <div className="options-row">
            {TIMES.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                className={`option-btn ${form.available_time_minutes === value ? 'selected' : ''}`}
                onClick={() => set('available_time_minutes', value)}
                disabled={loading}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Learning Goal */}
        <div className="form-group">
          <label htmlFor="goal">Learning Goal</label>
          <textarea
            id="goal"
            placeholder="e.g. Understand the basics and be able to explain them simply"
            value={form.learning_goal}
            onChange={e => set('learning_goal', e.target.value)}
            required
            maxLength={500}
            disabled={loading}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="error-box">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !form.topic.trim() || !form.learning_goal.trim()}
        >
          ✨ Create My Lesson
        </button>
      </form>
    </div>
  )
}
