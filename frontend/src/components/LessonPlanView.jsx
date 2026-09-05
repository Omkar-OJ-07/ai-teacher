/**
 * LessonPlanView — displays the Gemini-generated lesson plan.
 *
 * Props:
 *   plan             — LessonPlanResponse object from the backend
 *   onBack           — callback to return to the form
 *   onStartLearning  — callback to enter the teaching session (Phase 2)
 */

// Maps visual_type values to human-readable labels and emoji
const VISUAL_LABELS = {
  text_slide: { label: 'Text Slide',  icon: '📄' },
  diagram:    { label: 'Diagram',     icon: '📊' },
  graph:      { label: 'Graph',       icon: '📈' },
  code:       { label: 'Code',        icon: '💻' },
  equation:   { label: 'Equation',    icon: '🔢' },
  timeline:   { label: 'Timeline',    icon: '📅' },
  table:      { label: 'Table',       icon: '📋' },
  image:      { label: 'Image',       icon: '🖼️' },
}

function getVisual(type) {
  const key = (type || '').toLowerCase()
  return VISUAL_LABELS[key] || { label: type || 'Visual', icon: '🎨' }
}

export default function LessonPlanView({ plan, onBack, onStartLearning }) {
  const totalSegments  = plan.segments.length
  const interactSegs   = plan.segments.filter(s => s.interaction_required).length

  return (
    <div>
      {/* ── Plan Header ─────────────────────────────────────────────── */}
      <div className="plan-header">
        <button className="plan-back-btn" onClick={onBack}>
          ← Create Another Lesson
        </button>

        <h2 className="plan-title">{plan.title}</h2>

        <div className="plan-meta">
          <span className="meta-badge">📚 {plan.learner_level}</span>
          <span className="meta-badge">🌐 {plan.language}</span>
          <span className="meta-badge">⏱ {plan.total_duration_minutes} minutes</span>
          <span className="meta-badge">📑 {totalSegments} segment{totalSegments !== 1 ? 's' : ''}</span>
          <span className="meta-badge">💬 {interactSegs} interaction{interactSegs !== 1 ? 's' : ''}</span>
        </div>
      </div>

      {/* ── Summary Bar ─────────────────────────────────────────────── */}
      <div className="plan-summary-bar">
        <div className="summary-stat">
          <span className="summary-stat-label">Total Duration</span>
          <span className="summary-stat-value">{plan.total_duration_minutes} min</span>
        </div>
        <div className="summary-stat">
          <span className="summary-stat-label">Segments</span>
          <span className="summary-stat-value">{totalSegments}</span>
        </div>
        <div className="summary-stat">
          <span className="summary-stat-label">Level</span>
          <span className="summary-stat-value">{plan.learner_level}</span>
        </div>
        <div className="summary-stat">
          <span className="summary-stat-label">Language</span>
          <span className="summary-stat-value">{plan.language}</span>
        </div>
        <div className="summary-stat">
          <span className="summary-stat-label">Interactions</span>
          <span className="summary-stat-value">{interactSegs}</span>
        </div>
      </div>

      {/* ── Learning Objectives ──────────────────────────────────────── */}
      {plan.learning_objectives && plan.learning_objectives.length > 0 && (
        <div className="plan-section">
          <h3 className="section-title">Learning Objectives</h3>
          <div className="objectives-card">
            <ul className="objectives-list">
              {plan.learning_objectives.map((obj, i) => (
                <li key={i} className="objective-item">
                  <span className="objective-icon">✓</span>
                  <span>{obj}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* ── Lesson Segments ─────────────────────────────────────────── */}
      <div className="plan-section">
        <h3 className="section-title">Lesson Plan — {totalSegments} Segment{totalSegments !== 1 ? 's' : ''}</h3>
        <div className="segments-grid">
          {plan.segments.map(seg => {
            const visual = getVisual(seg.visual_type)
            return (
              <div key={seg.id} className="segment-card">

                {/* Card Header */}
                <div className="segment-card-header">
                  <div className="segment-number">{seg.id}</div>
                  <div className="segment-header-text">
                    <div className="segment-title">{seg.title}</div>
                    <div className="segment-concept">{seg.concept}</div>
                  </div>
                  <div className="segment-badges">
                    <span className="badge badge-duration">
                      ⏱ {seg.duration_minutes} min
                    </span>
                    <span className="badge badge-visual">
                      {visual.icon} {visual.label}
                    </span>
                    {seg.interaction_required ? (
                      <span className="badge badge-interact">💬 Interactive</span>
                    ) : (
                      <span className="badge badge-no-interact">📖 Lecture</span>
                    )}
                  </div>
                </div>

                {/* Card Body */}
                <div className="segment-card-body">

                  {/* Teaching Goal */}
                  <div className="segment-field full-width">
                    <span className="field-label">Teaching Goal</span>
                    <span className="field-value">{seg.teaching_goal}</span>
                  </div>

                  {/* Key Points */}
                  <div className="segment-field">
                    <span className="field-label">Key Points</span>
                    {seg.key_points && seg.key_points.length > 0 ? (
                      <ul className="key-points-list">
                        {seg.key_points.map((pt, i) => (
                          <li key={i} className="key-point-item">{pt}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="field-value">—</span>
                    )}
                  </div>

                  {/* Example */}
                  <div className="segment-field">
                    <span className="field-label">Example</span>
                    <div className="example-box">{seg.example}</div>
                  </div>

                </div>
              </div>
            )
          })}
        </div>
      </div>
      {/* ── Start Learning CTA ──────────────────────────────────── */}
      <div className="start-learning-cta">
        <div className="start-learning-inner">
          <div className="start-learning-text">
            <h3>Ready to start learning?</h3>
            <p>Your AI teacher will explain each concept, ask you questions, and adapt based on your responses.</p>
          </div>
          <button className="btn-start-learning" onClick={onStartLearning}>
            ▶ Start Learning
          </button>
        </div>
      </div>
    </div>
  )
}
