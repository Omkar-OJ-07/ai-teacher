/**
 * VisualPanel — deterministic HTML/CSS/SVG visuals based on visual_type.
 *
 * No external APIs. All visuals are rendered locally from the visual_spec
 * returned by the Gemini teaching content generator.
 *
 * Supported types:
 *   diagram    → SVG flow diagram (boxes + arrows)
 *   equation   → styled equation card (large formula + variable definitions)
 *   graph      → SVG bar chart with labels
 *   code       → monospace code block
 *   timeline   → SVG horizontal timeline
 *   table      → styled HTML table
 *   text_slide → large concept card with key terms
 *   image / *  → illustrated placeholder card
 */

// ── Helpers ───────────────────────────────────────────────────

function truncate(str, n) {
  return str && str.length > n ? str.slice(0, n) + '…' : str
}

// ── Diagram (SVG boxes + arrows) ──────────────────────────────

function DiagramVisual({ elements, title }) {
  const nodes = elements.slice(0, 5)
  const boxW = 160, boxH = 50, gap = 30, rx = 8
  const totalW = nodes.length * boxW + (nodes.length - 1) * gap
  const svgW = Math.min(totalW + 40, 700)
  const svgH = 120

  return (
    <svg
      viewBox={`0 0 ${totalW + 40} ${svgH}`}
      className="visual-svg"
      role="img"
      aria-label={title}
    >
      {nodes.map((node, i) => {
        const x = 20 + i * (boxW + gap)
        const y = (svgH - boxH) / 2
        const label = truncate(node, 28)
        const isLast = i === nodes.length - 1

        return (
          <g key={i}>
            {/* Box */}
            <rect
              x={x} y={y} width={boxW} height={boxH} rx={rx}
              fill="#EEF2FF" stroke="#4F46E5" strokeWidth="1.5"
            />
            {/* Label — word wrap by splitting on space */}
            <text
              x={x + boxW / 2} y={y + boxH / 2 - 4}
              textAnchor="middle" dominantBaseline="middle"
              fontSize="11" fontFamily="system-ui, sans-serif"
              fill="#312e81" fontWeight="600"
            >
              {label.split(' → ')[0]}
            </text>
            {label.includes(' → ') && (
              <text
                x={x + boxW / 2} y={y + boxH / 2 + 12}
                textAnchor="middle" dominantBaseline="middle"
                fontSize="10" fontFamily="system-ui, sans-serif"
                fill="#4338CA"
              >
                → {label.split(' → ').slice(1).join(' → ')}
              </text>
            )}
            {/* Arrow to next */}
            {!isLast && (
              <g>
                <line
                  x1={x + boxW} y1={y + boxH / 2}
                  x2={x + boxW + gap - 6} y2={y + boxH / 2}
                  stroke="#6366F1" strokeWidth="2"
                />
                <polygon
                  points={`${x + boxW + gap},${y + boxH / 2} ${x + boxW + gap - 8},${y + boxH / 2 - 5} ${x + boxW + gap - 8},${y + boxH / 2 + 5}`}
                  fill="#6366F1"
                />
              </g>
            )}
          </g>
        )
      })}
    </svg>
  )
}

// ── Equation card ─────────────────────────────────────────────

function EquationVisual({ elements }) {
  const formula = elements[0] || ''
  const vars = elements.slice(1)

  return (
    <div className="visual-equation">
      <div className="eq-formula">{formula}</div>
      {vars.length > 0 && (
        <div className="eq-vars">
          {vars.map((v, i) => (
            <div key={i} className="eq-var-row">
              <span className="eq-var-symbol">{v.split(':')[0]?.trim()}</span>
              {v.includes(':') && (
                <span className="eq-var-def">{v.split(':').slice(1).join(':').trim()}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Bar graph (SVG) ───────────────────────────────────────────

function GraphVisual({ elements }) {
  const axisX = elements[0] || 'X'
  const axisY = elements[1] || 'Y'
  const dataPoints = elements.slice(2).filter(e => e.includes(':'))

  const svgW = 400, svgH = 180
  const padL = 48, padB = 40, padT = 16, padR = 16
  const chartW = svgW - padL - padR
  const chartH = svgH - padB - padT

  const values = dataPoints.map(p => {
    const parts = p.split(':')
    return { label: parts[0].trim(), value: parseFloat(parts[1]) || 0 }
  }).filter(p => !isNaN(p.value))

  if (values.length === 0) {
    return <div className="visual-placeholder">📈 {axisY} vs {axisX}</div>
  }

  const maxVal = Math.max(...values.map(v => v.value)) * 1.15
  const barW = Math.min(chartW / values.length - 8, 50)

  return (
    <svg viewBox={`0 0 ${svgW} ${svgH}`} className="visual-svg" aria-label="Graph">
      {/* Axes */}
      <line x1={padL} y1={padT} x2={padL} y2={svgH - padB} stroke="#6B7280" strokeWidth="1.5" />
      <line x1={padL} y1={svgH - padB} x2={svgW - padR} y2={svgH - padB} stroke="#6B7280" strokeWidth="1.5" />
      {/* Axis labels */}
      <text x={svgW / 2} y={svgH - 4} textAnchor="middle" fontSize="10" fill="#6B7280" fontFamily="system-ui">{axisX}</text>
      <text x={10} y={svgH / 2} textAnchor="middle" fontSize="10" fill="#6B7280" fontFamily="system-ui"
        transform={`rotate(-90, 10, ${svgH / 2})`}>{axisY}</text>
      {/* Bars */}
      {values.map((pt, i) => {
        const barH = (pt.value / maxVal) * chartH
        const x = padL + 12 + i * (chartW / values.length)
        const y = padT + chartH - barH
        return (
          <g key={i}>
            <rect x={x} y={y} width={barW} height={barH} rx="3"
              fill="#4F46E5" fillOpacity="0.8" />
            <text x={x + barW / 2} y={y - 4} textAnchor="middle" fontSize="9" fill="#312e81" fontFamily="system-ui">
              {pt.value}
            </text>
            <text x={x + barW / 2} y={svgH - padB + 12} textAnchor="middle" fontSize="9" fill="#6B7280" fontFamily="system-ui">
              {truncate(pt.label, 8)}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

// ── Code block ────────────────────────────────────────────────

function CodeVisual({ elements }) {
  const code = elements.join('\n')
  return (
    <pre className="visual-code"><code>{code}</code></pre>
  )
}

// ── Timeline (SVG horizontal) ─────────────────────────────────

function TimelineVisual({ elements }) {
  const events = elements.slice(0, 6)
  const svgW = 660, svgH = 100
  const y = 50, dotR = 7

  if (events.length === 0) return <div className="visual-placeholder">📅 Timeline</div>

  const spacing = (svgW - 60) / Math.max(events.length - 1, 1)

  return (
    <svg viewBox={`0 0 ${svgW} ${svgH}`} className="visual-svg" aria-label="Timeline">
      {/* Line */}
      <line x1={30} y1={y} x2={svgW - 30} y2={y} stroke="#C7D2FE" strokeWidth="2" />
      {events.map((ev, i) => {
        const x = 30 + i * spacing
        const label = truncate(ev, 22)
        const above = i % 2 === 0
        return (
          <g key={i}>
            <circle cx={x} cy={y} r={dotR} fill="#4F46E5" />
            <line x1={x} y1={above ? y - dotR : y + dotR}
                  x2={x} y2={above ? y - 16 : y + 16}
                  stroke="#6366F1" strokeWidth="1.5" />
            <text x={x} y={above ? y - 20 : y + 28}
              textAnchor="middle" fontSize="9.5"
              fontFamily="system-ui" fill="#312e81" fontWeight="500">
              {label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

// ── Table ─────────────────────────────────────────────────────

function TableVisual({ elements }) {
  if (elements.length === 0) return <div className="visual-placeholder">📋 Table</div>

  const rows = elements.map(row =>
    row.split(',').map(cell => cell.trim())
  )
  const headers = rows[0] || []
  const dataRows = rows.slice(1)

  return (
    <div className="visual-table-wrapper">
      <table className="visual-table">
        <thead>
          <tr>
            {headers.map((h, i) => <th key={i}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            <tr key={ri}>
              {row.map((cell, ci) => <td key={ci}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Text slide ────────────────────────────────────────────────

function TextSlideVisual({ elements }) {
  const title = elements[0] || ''
  const terms = elements.slice(1)
  return (
    <div className="visual-text-slide">
      {title && <div className="ts-title">{title}</div>}
      {terms.map((term, i) => {
        const [key, ...rest] = term.split(':')
        return (
          <div key={i} className="ts-term">
            <span className="ts-key">{key.trim()}</span>
            {rest.length > 0 && <span className="ts-def">{rest.join(':').trim()}</span>}
          </div>
        )
      })}
    </div>
  )
}

// ── Concept card (replaces empty image placeholder) ──────────
// Renders the elements as icon + feature rows so the visual is
// always informative even when Gemini picks "image" type.

const CONCEPT_ICONS = ['🔵', '🟢', '🟡', '🟠', '🔴', '🟣', '⚪']

function ConceptCardVisual({ elements, title }) {
  const description = elements[0] || title || 'Concept illustration'
  const features = elements.slice(1)

  return (
    <div className="visual-concept-card">
      <div className="concept-card-header">
        <span className="concept-card-icon">🖼️</span>
        <span className="concept-card-desc">{description}</span>
      </div>
      {features.length > 0 && (
        <div className="concept-card-features">
          {features.map((feat, i) => (
            <div key={i} className="concept-card-feature">
              <span className="concept-card-bullet">{CONCEPT_ICONS[i % CONCEPT_ICONS.length]}</span>
              <span>{feat}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Generic fallback for unknown types ───────────────────────

function FallbackVisual({ type, title, description, elements }) {
  return (
    <div className="visual-placeholder">
      <div className="visual-placeholder-icon">📐</div>
      <div className="visual-placeholder-title">{title || type}</div>
      {description && <div className="visual-placeholder-desc">{description}</div>}
      {elements.length > 0 && (
        <ul className="visual-placeholder-list">
          {elements.slice(0, 4).map((el, i) => <li key={i}>{el}</li>)}
        </ul>
      )}
    </div>
  )
}


// ═══════════════════════════════════════════════════════════════
// Main export — VisualPanel
// ═══════════════════════════════════════════════════════════════

/**
 * VisualPanel
 * Props:
 *   visualSpec — VisualSpec object { type, title, elements, description }
 */
export default function VisualPanel({ visualSpec }) {
  if (!visualSpec) return null
  const { type, title, elements = [], description } = visualSpec
  const t = (type || '').toLowerCase()

  const renderVisual = () => {
    switch (t) {
      case 'diagram':    return <DiagramVisual elements={elements} title={title} />
      case 'equation':   return <EquationVisual elements={elements} />
      case 'graph':      return <GraphVisual elements={elements} />
      case 'code':       return <CodeVisual elements={elements} />
      case 'timeline':   return <TimelineVisual elements={elements} />
      case 'table':      return <TableVisual elements={elements} />
      case 'text_slide': return <TextSlideVisual elements={elements} />
      case 'image':      return <ConceptCardVisual elements={elements} title={title} />
      default:           return <FallbackVisual type={t} title={title} description={description} elements={elements} />
    }
  }

  return (
    <div className="visual-panel">
      <div className="visual-panel-header">
        <span className="visual-panel-label">📊 Visual Aid</span>
        <span className="visual-panel-title">{title}</span>
      </div>
      <div className="visual-panel-body">
        {renderVisual()}
      </div>
      {description && (
        <div className="visual-panel-footer">{description}</div>
      )}
    </div>
  )
}
