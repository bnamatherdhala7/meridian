import { useEffect, useRef, useState } from 'react'
import type { FeedItem, ForecastTriggerEntry, PreTriageEntry, RagEvent, StateTransitionEntry, ToolCall } from '../types'

interface Props {
  feedItems: FeedItem[]
  startTimeMs: number | null
}

// Format epoch ms as elapsed-from-start label, e.g. "T+1.8s" or "T+420ms"
function elapsedLabel(ts: number, start: number | null): string {
  if (start === null) return ''
  const delta = ts - start
  if (delta < 0) return 'T+0ms'
  if (delta < 1000) return `T+${delta}ms`
  return `T+${(delta / 1000).toFixed(1)}s`
}

const TRIGGER_COLOR: Record<string, string> = {
  threshold:   'var(--orange)',
  trajectory:  'var(--amber)',
  uncertainty: 'var(--violet)',
}

const STATE_COLOR: Record<string, string> = {
  PRE_TRIAGE:    'var(--teal)',
  TRIAGE:        'var(--brand)',
  INVESTIGATING: 'var(--brand)',
  HYPOTHESIZING: 'var(--brand)',
  REMEDIATING:   'var(--green)',
  ESCALATING:    'var(--orange)',
  SUPPRESSED:    'var(--violet)',
  RESOLVED:      'var(--green)',
  IDLE:          'var(--subtle)',
}

// ── Tool metadata ─────────────────────────────────────────────
const TOOL_BADGE: Record<string, string> = {
  run_spl_query:         'sp',
  search_indexes:        'sp',
  get_knowledge_objects: 'sp',
  generate_spl:          'sp',
  get_metadata:          'sp',
  get_user_context:      'sp',
  get_network_topology:  'ci',
  get_telemetry_metrics: 'ci',
}

const TOOL_LABEL: Record<string, string> = {
  run_spl_query:         'run_spl',
  search_indexes:        'search_idx',
  get_knowledge_objects: 'knowledge',
  generate_spl:          'gen_spl',
  get_metadata:          'metadata',
  get_user_context:      'user_ctx',
  get_network_topology:  'topology',
  get_telemetry_metrics: 'telemetry',
}

const BAND_COLOR: Record<string, string> = {
  high:   'var(--orange)',
  medium: 'var(--amber)',
  low:    'var(--violet)',
}

const ACTION_COLOR: Record<string, string> = {
  investigate: 'var(--green)',
  monitor:     'var(--amber)',
  suppress:    'var(--violet)',
}

const OUTCOME_COLOR: Record<string, string> = {
  REMEDIATING: 'var(--green)',
  ESCALATING:  'var(--orange)',
}

// ── Score helpers ─────────────────────────────────────────────
function scoreColor(score: number): string {
  if (score >= 0.80) return 'var(--green)'
  if (score >= 0.65) return 'var(--teal)'
  return 'var(--muted)'
}

function ScoreBar({ score }: { score: number }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
      <span style={{
        display: 'inline-block',
        width: Math.round(score * 40),
        height: 3,
        borderRadius: 2,
        background: scoreColor(score),
        opacity: 0.8,
        transition: 'width 0.3s ease',
      }} />
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: scoreColor(score), fontWeight: 600 }}>
        {Math.round(score * 100)}%
      </span>
    </span>
  )
}

// ── State Transition banner ──────────────────────────────────
function StateTransitionCard({ entry, elapsed }: { entry: StateTransitionEntry; elapsed: string }) {
  const fromColor = STATE_COLOR[entry.from_state] ?? 'var(--subtle)'
  const toColor = STATE_COLOR[entry.to_state] ?? 'var(--subtle)'

  return (
    <div className="state-transition" role="row">
      <div className="state-transition-line" />
      <div className="state-transition-body">
        <div className="state-transition-arrow">
          <span
            className="state-pill"
            style={{ color: fromColor, borderColor: `${fromColor}55`, background: `${fromColor}10` }}
          >
            {entry.from_state}
          </span>
          <span className="state-transition-chevron">›</span>
          <span
            className="state-pill state-pill-to"
            style={{ color: toColor, borderColor: `${toColor}55`, background: `${toColor}14` }}
          >
            {entry.to_state}
          </span>
          {elapsed && <span className="state-transition-elapsed">{elapsed}</span>}
        </div>
        <div className="state-transition-reason">{entry.reason}</div>
      </div>
    </div>
  )
}

// ── Forecast Trigger card (proactive pre-alert) ──────────────
function ForecastTriggerCard({ entry, elapsed }: { entry: ForecastTriggerEntry; elapsed: string }) {
  const [open, setOpen] = useState(false)
  const color = TRIGGER_COLOR[entry.trigger_type] ?? 'var(--orange)'
  const isCritical = entry.severity === 'critical'

  return (
    <div
      className="tool-item forecast-trigger-item"
      style={{
        borderColor: `${color}55`,
        background: `${color}0a`,
        boxShadow: isCritical ? `0 0 0 1px ${color}55, 0 4px 12px ${color}22` : undefined,
      }}
    >
      <div className="tool-item-top" onClick={() => setOpen(v => !v)} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <span
          className="tool-badge"
          style={{
            background: `${color}1a`,
            color: color,
            border: `1px solid ${color}40`,
            animation: isCritical ? 'forecastPulse 1.4s ease-in-out infinite' : undefined,
          }}
        >
          ◆ predictive · {entry.trigger_type}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {entry.projected_minutes_ahead !== null && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              fontWeight: 700,
              color: color,
              letterSpacing: '0.04em',
            }}>
              T−{entry.projected_minutes_ahead}min ahead
            </span>
          )}
          {elapsed && <span className="tool-timing">{elapsed}</span>}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', lineHeight: 1 }}>
            {open ? '▾' : '▸'}
          </span>
        </div>
      </div>
      <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 10 }}>
        <span className="tool-preview" style={{ flex: 1 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text)', fontWeight: 600 }}>
            {entry.metric}
          </span>
          {' · '}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--subtle)' }}>
            {entry.device}
          </span>
        </span>
        <ScoreBar score={entry.confidence} />
      </div>
      <div style={{ marginTop: 6, fontSize: 11, color: 'var(--muted)', lineHeight: 1.4 }}>
        {entry.message}
      </div>
      {open && (
        <div className="tool-trace" style={{ marginTop: 8 }}>
          <div className="tool-trace-section">
            <div className="tool-trace-label">FORECAST TRIGGER</div>
            <pre className="tool-trace-body">{JSON.stringify({
              metric: entry.metric,
              device: entry.device,
              trigger_type: entry.trigger_type,
              severity: entry.severity,
              projected_minutes_ahead: entry.projected_minutes_ahead,
              model: entry.model,
              confidence: entry.confidence,
            }, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Trace Summary header ─────────────────────────────────────
function TraceSummary({ items, startTimeMs }: { items: FeedItem[]; startTimeMs: number | null }) {
  if (items.length === 0 || startTimeMs === null) return null

  const lastTs = items[items.length - 1].timestamp_ms
  const elapsedMs = lastTs - startTimeMs
  const elapsedLabel = elapsedMs < 1000 ? `${elapsedMs}ms` : `${(elapsedMs / 1000).toFixed(1)}s`

  const toolCount = items.filter(i => i.kind === 'tool').length
  const ragCount = items.filter(i => i.kind === 'rag').length
  const transitionCount = items.filter(i => i.kind === 'state').length
  const forecastCount = items.filter(i => i.kind === 'forecast').length

  return (
    <div className="trace-summary">
      <div className="trace-summary-item">
        <span className="trace-summary-icon">⏱</span>
        <span className="trace-summary-value">{elapsedLabel}</span>
      </div>
      {transitionCount > 0 && (
        <div className="trace-summary-item">
          <span className="trace-summary-icon">▸</span>
          <span className="trace-summary-value">{transitionCount}</span>
          <span className="trace-summary-label">states</span>
        </div>
      )}
      {toolCount > 0 && (
        <div className="trace-summary-item">
          <span className="trace-summary-icon">⚡</span>
          <span className="trace-summary-value">{toolCount}</span>
          <span className="trace-summary-label">tools</span>
        </div>
      )}
      {ragCount > 0 && (
        <div className="trace-summary-item">
          <span className="trace-summary-icon">◈</span>
          <span className="trace-summary-value">{ragCount}</span>
          <span className="trace-summary-label">rag</span>
        </div>
      )}
      {forecastCount > 0 && (
        <div className="trace-summary-item" style={{ color: 'var(--orange)' }}>
          <span className="trace-summary-icon">◆</span>
          <span className="trace-summary-value">{forecastCount}</span>
          <span className="trace-summary-label">predictive</span>
        </div>
      )}
    </div>
  )
}

// ── PreTriage card ────────────────────────────────────────────
function PreTriageCard({ entry, elapsed }: { entry: PreTriageEntry; elapsed: string }) {
  const [open, setOpen] = useState(false)
  const score = Math.round(entry.confidence_score * 100)

  return (
    <div className="tool-item pre-triage-item" style={{ borderColor: 'rgba(6,182,212,0.25)', background: 'rgba(6,182,212,0.04)' }}>
      <div className="tool-item-top" onClick={() => setOpen(v => !v)} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <span className="tool-badge" style={{ background: 'rgba(6,182,212,0.12)', color: 'var(--teal)', border: '1px solid rgba(6,182,212,0.25)' }}>
          00 pre_triage
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {entry.escalate_immediately && <div className="tool-anomaly-dot" title="Escalating immediately" />}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, fontWeight: 600, color: ACTION_COLOR[entry.recommended_action] ?? 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {entry.recommended_action}
          </span>
          {elapsed && <span className="tool-elapsed">{elapsed}</span>}
          <span className="tool-timing">0ms · 0 tokens</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', lineHeight: 1 }}>
            {open ? '▾' : '▸'}
          </span>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
        <span className="tool-preview" style={{ flex: 1 }}>
          {entry.alert_type} · signal_strength={entry.signal_strength} · score=
          <span style={{ color: BAND_COLOR[entry.confidence_band] ?? 'var(--muted)', fontWeight: 600 }}>
            {score}%
          </span>
          {' '}({entry.confidence_band})
        </span>
      </div>
      {open && (
        <div className="tool-trace" style={{ marginTop: 6 }}>
          <div className="tool-trace-section">
            <div className="tool-trace-label">SCORING RATIONALE</div>
            <pre className="tool-trace-body">{entry.scoring_rationale}</pre>
          </div>
          {entry.suppression_reason && (
            <div className="tool-trace-section">
              <div className="tool-trace-label">SUPPRESSION REASON</div>
              <pre className="tool-trace-body">{entry.suppression_reason}</pre>
            </div>
          )}
          <div className="tool-trace-section">
            <div className="tool-trace-label">RESULT</div>
            <pre className="tool-trace-body">{JSON.stringify({
              alert_id: entry.alert_id,
              confidence_band: entry.confidence_band,
              confidence_score: entry.confidence_score,
              signal_strength: entry.signal_strength,
              recommended_action: entry.recommended_action,
              escalate_immediately: entry.escalate_immediately,
              tokens_used: 0,
            }, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

// ── RAG card ─────────────────────────────────────────────────
function RagCard({ event, elapsed }: { event: RagEvent; elapsed: string }) {
  const [open, setOpen] = useState(false)
  const isSPL = event.layer === 'SPL'
  const accentColor = isSPL ? '#8B5CF6' : '#6366F1'
  const label = isSPL ? 'rag · spl' : 'rag · memory'
  const heading = isSPL ? 'Pinecone SPL Knowledge' : 'Pinecone Incident Memory'
  const topScore = event.hits[0]?.score ?? 0

  return (
    <div
      className="tool-item rag-item"
      style={{
        borderColor: `${accentColor}40`,
        background: `${accentColor}08`,
      }}
    >
      <div className="tool-item-top" onClick={() => setOpen(v => !v)} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <span
          className="tool-badge"
          style={{
            background: `${accentColor}18`,
            color: accentColor,
            border: `1px solid ${accentColor}35`,
          }}
        >
          ◈ {label}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: accentColor, fontWeight: 600, letterSpacing: '0.04em' }}>
            {event.hits.length} hits
          </span>
          <ScoreBar score={topScore} />
          {elapsed && <span className="tool-elapsed">{elapsed}</span>}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>
            {open ? '▾' : '▸'}
          </span>
        </div>
      </div>

      {/* Hit list — always visible */}
      <div style={{ marginTop: 6, display: 'flex', flexDirection: 'column', gap: 4 }}>
        {event.hits.map((hit, i) => (
          <div key={hit.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', minWidth: 14, paddingTop: 1 }}>
              {i + 1}.
            </span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text)', fontWeight: 500 }}>
                  {hit.title}
                </span>
                <ScoreBar score={hit.score} />
                {hit.outcome && (
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 8,
                    fontWeight: 700,
                    color: OUTCOME_COLOR[hit.outcome] ?? 'var(--muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    background: `${OUTCOME_COLOR[hit.outcome] ?? 'var(--subtle)'}18`,
                    padding: '1px 6px',
                    borderRadius: 20,
                  }}>
                    {hit.outcome}
                  </span>
                )}
                {hit.phase && (
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 8,
                    color: accentColor,
                    background: `${accentColor}14`,
                    padding: '1px 6px',
                    borderRadius: 20,
                  }}>
                    {hit.phase}
                  </span>
                )}
              </div>
              {open && (
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: 10, color: 'var(--muted)', marginTop: 2, lineHeight: 1.4 }}>
                  {hit.text}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {open && (
        <div className="tool-trace" style={{ marginTop: 8 }}>
          <div className="tool-trace-section">
            <div className="tool-trace-label">{heading} · QUERY</div>
            <pre className="tool-trace-body">{event.query}</pre>
          </div>
          <div className="tool-trace-section">
            <div className="tool-trace-label">RAW HITS</div>
            <pre className="tool-trace-body">{JSON.stringify(event.hits, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Tool call card ────────────────────────────────────────────
function ToolCard({ call, seq, expanded, onToggle, elapsed }: {
  call: ToolCall
  seq: number
  expanded: boolean
  onToggle: () => void
  elapsed: string
}) {
  return (
    <div className="tool-item">
      <div className="tool-item-top" onClick={onToggle} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <span className={`tool-badge ${TOOL_BADGE[call.tool] ?? 'sp'}`}>
          {String(seq).padStart(2, '0')} {TOOL_LABEL[call.tool] ?? call.tool}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {call.anomaly && <div className="tool-anomaly-dot" title="Anomaly detected" />}
          {elapsed && <span className="tool-elapsed">{elapsed}</span>}
          <span className="tool-timing">{call.duration_ms}ms</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', lineHeight: 1 }}>
            {expanded ? '▾' : '▸'}
          </span>
        </div>
      </div>
      {call.result_preview && (
        <div className="tool-preview" title={call.result_preview}>
          {call.result_preview}
        </div>
      )}
      {expanded && (
        <div className="tool-trace">
          <div className="tool-trace-section">
            <div className="tool-trace-label">INPUT</div>
            <pre className="tool-trace-body">{call.input_full || JSON.stringify({ note: 'no input captured' })}</pre>
          </div>
          <div className="tool-trace-section">
            <div className="tool-trace-label">OUTPUT</div>
            <pre className="tool-trace-body">{call.result_full || JSON.stringify({ note: 'no output captured' })}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Feed ──────────────────────────────────────────────────────
export default function ToolCallFeed({ feedItems, startTimeMs }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [feedItems.length])

  function toggle(id: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  if (feedItems.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">⚡</div>
        <div className="empty-text">awaiting tool calls</div>
      </div>
    )
  }

  let toolSeq = 0

  return (
    <div className="tool-list">
      <TraceSummary items={feedItems} startTimeMs={startTimeMs} />
      {feedItems.map(item => {
        const elapsed = elapsedLabel(item.timestamp_ms, startTimeMs)
        if (item.kind === 'state') {
          return <StateTransitionCard key={item.id} entry={item.data} elapsed={elapsed} />
        }
        if (item.kind === 'forecast') {
          return <ForecastTriggerCard key={item.id} entry={item.data} elapsed={elapsed} />
        }
        if (item.kind === 'pre_triage') {
          return <PreTriageCard key={item.id} entry={item.data} elapsed={elapsed} />
        }
        if (item.kind === 'rag') {
          return <RagCard key={item.id} event={item.data} elapsed={elapsed} />
        }
        // tool
        toolSeq++
        return (
          <ToolCard
            key={item.id}
            call={item.data}
            seq={toolSeq}
            expanded={expanded.has(item.id)}
            onToggle={() => toggle(item.id)}
            elapsed={elapsed}
          />
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}
