import type { ArchivedRun } from '../utils/runArchive'

interface Props {
  runs: ArchivedRun[]
  onSelect: (run: ArchivedRun) => void
  onClear: () => void
}

const STATE_COLOR: Record<string, string> = {
  REMEDIATING: 'var(--green)',
  RESOLVED:    'var(--green)',
  ESCALATING:  'var(--orange)',
  SUPPRESSED:  'var(--violet)',
}

function fmtAgo(ms: number): string {
  const diff = Date.now() - ms
  if (diff < 60_000) return `${Math.round(diff / 1000)}s ago`
  if (diff < 3_600_000) return `${Math.round(diff / 60_000)}m ago`
  if (diff < 86_400_000) return `${Math.round(diff / 3_600_000)}h ago`
  return `${Math.round(diff / 86_400_000)}d ago`
}

function fmtDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export default function RunHistoryPanel({ runs, onSelect, onClear }: Props) {
  if (runs.length === 0) {
    return (
      <div className="empty-state" style={{ minHeight: 80 }}>
        <div className="empty-text">no past runs</div>
      </div>
    )
  }

  return (
    <div className="run-history">
      <div className="run-history-header">
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)', letterSpacing: '0.06em' }}>
          {runs.length} RECENT RUN{runs.length === 1 ? '' : 'S'}
        </span>
        <button
          onClick={onClear}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--subtle)',
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            cursor: 'pointer',
            padding: 0,
            letterSpacing: '0.04em',
          }}
          title="Clear history"
        >
          CLEAR
        </button>
      </div>
      <div className="run-history-list">
        {runs.map(run => (
          <button
            key={run.id}
            className="run-history-item"
            onClick={() => onSelect(run)}
            title="View full trace"
          >
            <div className="run-history-item-top">
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text)', fontWeight: 600 }}>
                {run.scenarioMeta.label}
              </span>
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                  color: STATE_COLOR[run.finalState] ?? 'var(--muted)',
                  background: `${STATE_COLOR[run.finalState] ?? 'var(--muted)'}1a`,
                  border: `1px solid ${STATE_COLOR[run.finalState] ?? 'var(--border-md)'}40`,
                  borderRadius: 20,
                  padding: '1px 6px',
                }}
              >
                {run.finalState}
              </span>
            </div>
            <div className="run-history-item-meta">
              <span>{fmtDuration(run.durationMs)}</span>
              <span>·</span>
              <span>{run.totalTokens.toLocaleString()} tokens</span>
              <span>·</span>
              <span>{fmtAgo(run.startTimeMs)}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
