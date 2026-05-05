import { useEffect, useRef, useState } from 'react'
import type { PreTriageEntry, ToolCall } from '../types'

interface Props {
  calls: ToolCall[]
  preTriageEntry: PreTriageEntry | null
}

const TOOL_BADGE: Record<string, string> = {
  run_spl_query: 'sp',
  search_indexes: 'sp',
  get_knowledge_objects: 'sp',
  generate_spl: 'sp',
  get_metadata: 'sp',
  get_user_context: 'sp',
  get_network_topology: 'ci',
  get_telemetry_metrics: 'ci',
}

const TOOL_LABEL: Record<string, string> = {
  run_spl_query: 'run_spl',
  search_indexes: 'search_idx',
  get_knowledge_objects: 'knowledge',
  generate_spl: 'gen_spl',
  get_metadata: 'metadata',
  get_user_context: 'user_ctx',
  get_network_topology: 'topology',
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

function PreTriageCard({ entry }: { entry: PreTriageEntry }) {
  const [open, setOpen] = useState(false)
  const score = Math.round(entry.confidence_score * 100)

  return (
    <div className="tool-item pre-triage-item" style={{ borderColor: 'rgba(6,182,212,0.25)', background: 'rgba(6,182,212,0.04)' }}>
      <div
        className="tool-item-top"
        onClick={() => setOpen(v => !v)}
        style={{ cursor: 'pointer', userSelect: 'none' }}
      >
        <span className="tool-badge" style={{ background: 'rgba(6,182,212,0.12)', color: 'var(--teal)', border: '1px solid rgba(6,182,212,0.25)' }}>
          00 pre_triage
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {entry.escalate_immediately && (
            <div className="tool-anomaly-dot" title="Escalating immediately" />
          )}
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            fontWeight: 600,
            color: ACTION_COLOR[entry.recommended_action] ?? 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            {entry.recommended_action}
          </span>
          <span className="tool-timing">0ms · 0 tokens</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', lineHeight: 1 }}>
            {open ? '▾' : '▸'}
          </span>
        </div>
      </div>

      {/* Summary row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
        <span className="tool-preview" style={{ flex: 1 }}>
          {entry.alert_type} · signal_strength={entry.signal_strength} · score=
          <span style={{ color: BAND_COLOR[entry.confidence_band] ?? 'var(--muted)', fontWeight: 600 }}>
            {score}%
          </span>
          {' '}({entry.confidence_band})
        </span>
      </div>

      {/* Expanded detail */}
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

export default function ToolCallFeed({ calls, preTriageEntry }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [calls.length])

  function toggle(id: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const empty = !preTriageEntry && calls.length === 0

  if (empty) {
    return (
      <div className="empty-state">
        <div className="empty-icon">⚡</div>
        <div className="empty-text">awaiting tool calls</div>
      </div>
    )
  }

  return (
    <div className="tool-list">
      {/* PRE_TRIAGE entry always first */}
      {preTriageEntry && <PreTriageCard entry={preTriageEntry} />}

      {calls.map((call, i) => {
        const isExpanded = expanded.has(call.id)
        return (
          <div key={call.id} className="tool-item">
            <div
              className="tool-item-top"
              onClick={() => toggle(call.id)}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              <span className={`tool-badge ${TOOL_BADGE[call.tool] ?? 'sp'}`}>
                {String(i + 1).padStart(2, '0')} {TOOL_LABEL[call.tool] ?? call.tool}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {call.anomaly && <div className="tool-anomaly-dot" title="Anomaly detected" />}
                <span className="tool-timing">{call.duration_ms}ms</span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  color: 'var(--subtle)',
                  lineHeight: 1,
                }}>
                  {isExpanded ? '▾' : '▸'}
                </span>
              </div>
            </div>
            {call.result_preview && (
              <div className="tool-preview" title={call.result_preview}>
                {call.result_preview}
              </div>
            )}
            {isExpanded && (
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
      })}
      <div ref={bottomRef} />
    </div>
  )
}
