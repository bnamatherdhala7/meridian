import { useEffect, useRef, useState } from 'react'
import type { FeedItem, PreTriageEntry, RagEvent, ToolCall } from '../types'

interface Props {
  feedItems: FeedItem[]
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

// ── PreTriage card ────────────────────────────────────────────
function PreTriageCard({ entry }: { entry: PreTriageEntry }) {
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
function RagCard({ event }: { event: RagEvent }) {
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
function ToolCard({ call, seq, expanded, onToggle }: {
  call: ToolCall
  seq: number
  expanded: boolean
  onToggle: () => void
}) {
  return (
    <div className="tool-item">
      <div className="tool-item-top" onClick={onToggle} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <span className={`tool-badge ${TOOL_BADGE[call.tool] ?? 'sp'}`}>
          {String(seq).padStart(2, '0')} {TOOL_LABEL[call.tool] ?? call.tool}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {call.anomaly && <div className="tool-anomaly-dot" title="Anomaly detected" />}
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
export default function ToolCallFeed({ feedItems }: Props) {
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
      {feedItems.map(item => {
        if (item.kind === 'pre_triage') {
          return <PreTriageCard key={item.id} entry={item.data} />
        }
        if (item.kind === 'rag') {
          return <RagCard key={item.id} event={item.data} />
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
          />
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}
