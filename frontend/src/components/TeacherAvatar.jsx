/**
 * TeacherAvatar — lightweight animated AI teacher presence.
 *
 * This is intentionally NOT a realistic video avatar (no external
 * avatar-generation API, no video assets). It is a state-aware SVG/CSS
 * component that gives the AI Teacher a visible, professional "presence"
 * during the lesson. Disclosed in project docs as an MVP substitute for
 * a full video avatar, given hackathon time constraints.
 *
 * Props:
 *   state: 'idle' | 'speaking' | 'thinking' | 'correct' | 'encouraging' | 'misconception'
 *   size:  pixel size of the avatar circle (default 84)
 */

const STATE_META = {
  idle:          { label: 'Ready to teach',        color: 'var(--primary)' },
  speaking:      { label: 'Explaining...',          color: 'var(--primary)' },
  thinking:      { label: 'Reviewing your answer...', color: 'var(--warning)' },
  correct:       { label: 'Nice work!',             color: 'var(--success)' },
  encouraging:   { label: 'Almost there...',        color: 'var(--warning)' },
  misconception: { label: "Let's re-explain this",  color: 'var(--error)' },
}

export default function TeacherAvatar({ state = 'idle', size = 84 }) {
  const meta = STATE_META[state] || STATE_META.idle

  return (
    <div className="teacher-avatar-wrap" title="AI Teacher">
      <div
        className={`teacher-avatar teacher-avatar--${state}`}
        style={{ width: size, height: size, '--avatar-color': meta.color }}
      >
        {/* Idle/ambient rings — pulse while speaking */}
        <span className="ta-ring ta-ring-1" />
        <span className="ta-ring ta-ring-2" />

        <svg viewBox="0 0 100 100" className="ta-face" xmlns="http://www.w3.org/2000/svg">
          {/* Head */}
          <circle cx="50" cy="50" r="34" fill="var(--card)" stroke="var(--avatar-color)" strokeWidth="2.5" />

          {/* Eyes */}
          <g className="ta-eyes">
            <circle cx="38" cy="46" r="4" fill="var(--avatar-color)" />
            <circle cx="62" cy="46" r="4" fill="var(--avatar-color)" />
          </g>

          {/* Mouth — shape driven by state via CSS class on parent path set */}
          <path className="ta-mouth" d={mouthPath(state)} fill="none" stroke="var(--avatar-color)" strokeWidth="3" strokeLinecap="round" />

          {/* Graduation cap accent */}
          <path
            d="M50 14 L74 24 L50 34 L26 24 Z"
            fill="var(--avatar-color)"
            opacity="0.9"
          />
          <rect x="48.5" y="24" width="3" height="10" fill="var(--avatar-color)" opacity="0.9" />
        </svg>

        {/* Thinking dots */}
        {state === 'thinking' && (
          <div className="ta-thinking-dots">
            <span /><span /><span />
          </div>
        )}

        {/* Speaking waveform */}
        {state === 'speaking' && (
          <div className="ta-waveform">
            <span /><span /><span /><span /><span />
          </div>
        )}
      </div>
      <div className="ta-status-label" style={{ color: meta.color }}>{meta.label}</div>
    </div>
  )
}

function mouthPath(state) {
  switch (state) {
    case 'correct':
      return 'M36 58 Q50 70 64 58' // wide smile
    case 'encouraging':
      return 'M36 60 Q50 66 64 60' // gentle smile
    case 'misconception':
      return 'M36 62 Q50 58 64 62' // thoughtful/neutral concerned
    case 'thinking':
      return 'M38 60 L62 60' // flat line
    case 'speaking':
      return 'M38 58 Q50 68 62 58' // open, animated via CSS scaling
    default:
      return 'M38 60 Q50 64 62 60' // idle, soft neutral smile
  }
}
