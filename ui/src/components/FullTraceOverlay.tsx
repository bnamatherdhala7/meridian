import { useEffect, useState } from 'react'
import type { ArchivedRun } from '../utils/runArchive'

interface Props {
  run: ArchivedRun | null
  onClose: () => void
}

function fmtElapsed(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

function fmtTimestamp(ms: number): string {
  return new Date(ms).toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
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

export default function FullTraceOverlay({ run, onClose }: Props) {
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!run) return
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [run, onClose])

  if (!run) return null
  const r: ArchivedRun = run

  const traceJson = JSON.stringify(r, null, 2)

  function copyJson() {
    navigator.clipboard.writeText(traceJson).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  function downloadJson() {
    const blob = new Blob([traceJson], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const slug = `${r.scenarioMeta.id}-${new Date(r.startTimeMs).toISOString().slice(0, 19).replace(/:/g, '')}`
    a.download = `vigil-trace-${slug}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="trace-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="trace-overlay-panel" onClick={e => e.stopPropagation()}>
        <div className="trace-overlay-header">
          <div className="trace-overlay-header-left">
            <span className="wordmark" style={{ fontSize: 14 }}>FULL TRACE</span>
            <span style={{ color: 'var(--subtle)', fontFamily: 'var(--font-mono)', fontSize: 10 }}>
              {run.scenarioMeta.incident_id} · {run.scenarioMeta.severity} · {run.scenarioMeta.site}
            </span>
            <span
              className="report-state-badge"
              style={{
                color: STATE_COLOR[run.finalState] ?? 'var(--text)',
                background: 'transparent',
                border: `1px solid ${STATE_COLOR[run.finalState] ?? 'var(--border-md)'}`,
                padding: '2px 10px',
                fontSize: 9,
              }}
            >
              {run.finalState}
            </span>
          </div>
          <div className="trace-overlay-header-actions">
            <button className="btn-secondary" onClick={copyJson}>
              {copied ? '✓ Copied' : 'Copy JSON'}
            </button>
            <button className="btn-secondary" onClick={downloadJson}>Download</button>
            <button className="btn-secondary trace-overlay-close" onClick={onClose} aria-label="Close">✕</button>
          </div>
        </div>

        <div className="trace-overlay-body">
          {/* Run metadata */}
          <section className="trace-section">
            <h3 className="trace-section-title">RUN METADATA</h3>
            <div className="trace-meta-grid">
              <MetaCell label="Scenario" value={run.scenarioMeta.label} />
              <MetaCell label="Title" value={run.scenarioMeta.title} />
              <MetaCell label="Started" value={fmtTimestamp(run.startTimeMs)} mono />
              <MetaCell label="Duration" value={fmtElapsed(run.durationMs)} mono />
              <MetaCell label="Final State" value={run.finalState} mono />
              <MetaCell label="Tool Calls" value={String(run.feedItems.filter(f => f.kind === 'tool').length)} mono />
              <MetaCell label="RAG Retrievals" value={String(run.feedItems.filter(f => f.kind === 'rag').length)} mono />
              <MetaCell label="State Transitions" value={String(run.feedItems.filter(f => f.kind === 'state').length)} mono />
              <MetaCell label="Forecast Triggers" value={String(run.feedItems.filter(f => f.kind === 'forecast').length)} mono />
              <MetaCell label="Total Tokens" value={run.totalTokens.toLocaleString()} mono />
            </div>
          </section>

          {/* FSM path */}
          <section className="trace-section">
            <h3 className="trace-section-title">FINITE STATE MACHINE PATH</h3>
            <div className="trace-fsm-path">
              {run.fsmHistory.map((state, i) => (
                <span key={`${state}-${i}`} className="trace-fsm-step">
                  <span
                    className="state-pill"
                    style={{
                      color: STATE_COLOR[state] ?? 'var(--text)',
                      borderColor: `${STATE_COLOR[state] ?? 'var(--border-md)'}55`,
                      background: `${STATE_COLOR[state] ?? 'var(--surface)'}10`,
                    }}
                  >
                    {state}
                  </span>
                  {i < run.fsmHistory.length - 1 && <span className="trace-fsm-arrow">›</span>}
                </span>
              ))}
            </div>
          </section>

          {/* Timeline */}
          <section className="trace-section">
            <h3 className="trace-section-title">CHRONOLOGICAL TRACE — {run.feedItems.length} EVENTS</h3>
            <div className="trace-timeline">
              {run.feedItems.map(item => (
                <TraceEvent key={item.id} item={item} startTimeMs={run.startTimeMs} />
              ))}
            </div>
          </section>

          {/* Final report */}
          {run.report && (
            <section className="trace-section">
              <h3 className="trace-section-title">FINAL INCIDENT REPORT</h3>
              <pre className="trace-json">{JSON.stringify(run.report, null, 2)}</pre>
            </section>
          )}

          {/* Eval results */}
          {run.evalResults && (
            <section className="trace-section">
              <h3 className="trace-section-title">EVALUATOR RESULTS — GENERIC vs CONSTRAINED</h3>
              <pre className="trace-json">{JSON.stringify(run.evalResults, null, 2)}</pre>
            </section>
          )}

          {/* MTTD data */}
          {run.mttdData && (
            <section className="trace-section">
              <h3 className="trace-section-title">MEAN TIME TO DETECT / RESOLVE</h3>
              <pre className="trace-json">{JSON.stringify(run.mttdData, null, 2)}</pre>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}

function MetaCell({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="trace-meta-cell">
      <div className="trace-meta-label">{label}</div>
      <div className={`trace-meta-value${mono ? ' mono' : ''}`}>{value}</div>
    </div>
  )
}

function TraceEvent({ item, startTimeMs }: { item: import('../types').FeedItem; startTimeMs: number }) {
  const elapsed = item.timestamp_ms - startTimeMs
  const elapsedLabel = elapsed < 1000 ? `${elapsed}ms` : `T+${(elapsed / 1000).toFixed(2)}s`

  if (item.kind === 'state') {
    const { from_state, to_state, reason } = item.data
    return (
      <div className="trace-event trace-event-state">
        <div className="trace-event-time">{elapsedLabel}</div>
        <div className="trace-event-body">
          <div className="trace-event-header">
            <span
              className="state-pill"
              style={{
                color: STATE_COLOR[from_state] ?? 'var(--subtle)',
                borderColor: `${STATE_COLOR[from_state] ?? 'var(--border-md)'}55`,
              }}
            >
              {from_state}
            </span>
            <span className="state-transition-chevron">›</span>
            <span
              className="state-pill"
              style={{
                color: STATE_COLOR[to_state] ?? 'var(--text)',
                borderColor: `${STATE_COLOR[to_state] ?? 'var(--border-md)'}55`,
              }}
            >
              {to_state}
            </span>
          </div>
          <div className="trace-event-detail">{reason}</div>
        </div>
      </div>
    )
  }

  if (item.kind === 'forecast') {
    const f = item.data
    return (
      <div className="trace-event trace-event-forecast">
        <div className="trace-event-time">{elapsedLabel}</div>
        <div className="trace-event-body">
          <div className="trace-event-header">
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--orange)', fontWeight: 700, letterSpacing: '0.06em' }}>
              ◆ PREDICTIVE TRIGGER · {f.trigger_type.toUpperCase()}
            </span>
            {f.projected_minutes_ahead !== null && (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700, color: 'var(--orange)' }}>
                T−{f.projected_minutes_ahead}min
              </span>
            )}
          </div>
          <div className="trace-event-detail">
            <strong>{f.metric}</strong> · {f.device} · {f.model} · {Math.round(f.confidence * 100)}% confidence
          </div>
          <div className="trace-event-detail" style={{ marginTop: 4 }}>{f.message}</div>
        </div>
      </div>
    )
  }

  if (item.kind === 'pre_triage') {
    const p = item.data
    return (
      <div className="trace-event trace-event-pretriage">
        <div className="trace-event-time">{elapsedLabel}</div>
        <div className="trace-event-body">
          <div className="trace-event-header">
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--teal)', fontWeight: 700, letterSpacing: '0.06em' }}>
              ◇ PRE-TRIAGE · {p.recommended_action.toUpperCase()}
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>0 tokens · &lt;1ms</span>
          </div>
          <div className="trace-event-detail">
            {p.alert_type} · signal_strength={p.signal_strength} · confidence={Math.round(p.confidence_score * 100)}% ({p.confidence_band})
          </div>
          <pre className="trace-json" style={{ marginTop: 6 }}>{p.scoring_rationale}</pre>
          {p.suppression_reason && (
            <pre className="trace-json" style={{ marginTop: 4 }}>{'SUPPRESSION: ' + p.suppression_reason}</pre>
          )}
        </div>
      </div>
    )
  }

  if (item.kind === 'rag') {
    const r = item.data
    const accent = r.layer === 'SPL' ? '#8B5CF6' : '#6366F1'
    return (
      <div className="trace-event trace-event-rag">
        <div className="trace-event-time">{elapsedLabel}</div>
        <div className="trace-event-body">
          <div className="trace-event-header">
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: accent, fontWeight: 700, letterSpacing: '0.06em' }}>
              ◈ RAG · {r.layer === 'SPL' ? 'SPL KNOWLEDGE' : 'INCIDENT MEMORY'} · {r.phase}
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>{r.hits.length} hits</span>
          </div>
          <div className="trace-event-detail" style={{ marginTop: 4 }}>Query: <em>{r.query}</em></div>
          <div style={{ marginTop: 6, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {r.hits.map((hit, i) => (
              <div key={hit.id} style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--muted)' }}>
                <span style={{ color: 'var(--subtle)' }}>{i + 1}.</span>{' '}
                <strong style={{ color: 'var(--text)' }}>{hit.title}</strong>
                {' · '}
                <span style={{ color: accent }}>{Math.round(hit.score * 100)}%</span>
                {hit.outcome && <span style={{ color: 'var(--subtle)' }}> · {hit.outcome}</span>}
                <div style={{ paddingLeft: 14, color: 'var(--muted)', fontFamily: 'var(--font-sans)', fontSize: 11, marginTop: 2 }}>
                  {hit.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // tool
  const t = item.data
  return (
    <div className="trace-event trace-event-tool">
      <div className="trace-event-time">{elapsedLabel}</div>
      <div className="trace-event-body">
        <div className="trace-event-header">
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text)', fontWeight: 700, letterSpacing: '0.04em' }}>
            ⚡ TOOL · {t.tool}
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>
            {t.duration_ms}ms{t.anomaly ? ' · ⚠ ANOMALY' : ''}
          </span>
        </div>
        {t.input_full && (
          <>
            <div className="trace-subhead">INPUT</div>
            <pre className="trace-json">{t.input_full}</pre>
          </>
        )}
        {t.result_full && (
          <>
            <div className="trace-subhead">OUTPUT</div>
            <pre className="trace-json">{t.result_full}</pre>
          </>
        )}
      </div>
    </div>
  )
}
