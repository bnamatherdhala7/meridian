import type { IncidentReport } from '../types'

interface Props {
  report: IncidentReport | null
}

function stateBadgeClass(state: string): string {
  if (state === 'ESCALATING') return 'report-state-badge escalating'
  if (state === 'REMEDIATING' || state === 'RESOLVED') return 'report-state-badge remediating'
  if (state === 'SUPPRESSED') return 'report-state-badge suppressed'
  return 'report-state-badge default'
}

function confidenceClass(v: number): string {
  if (v >= 0.75) return 'high'
  if (v >= 0.5) return 'mid'
  return 'low'
}

export default function ReportPanel({ report }: Props) {
  if (!report) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📋</div>
        <div className="empty-text">awaiting report</div>
      </div>
    )
  }

  const conf = report.confidence
  const pct = Math.round(conf * 100)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      <div className={stateBadgeClass(report.final_state)}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
        {report.final_state}
      </div>

      <div className="report-field">
        <div className="report-label">Hypothesis</div>
        <div className="report-value">{report.hypothesis}</div>
      </div>

      <div className="report-field">
        <div className="report-label">Recommended Action</div>
        <div className="report-value action">{report.recommended_action || '—'}</div>
      </div>

      <div className="report-field">
        <div className="report-label">Confidence</div>
        <div className="report-confidence">
          <div className="confidence-bar-track">
            <div
              className={`confidence-bar-fill ${confidenceClass(conf)}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="confidence-val">{pct}%</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <div className="report-field">
          <div className="report-label">Tool Calls</div>
          <div className="report-value mono">{report.tool_calls}</div>
        </div>
        <div className="report-field">
          <div className="report-label">Duration</div>
          <div className="report-value mono">{report.duration_secs}s</div>
        </div>
        <div className="report-field">
          <div className="report-label">Tokens</div>
          <div className="report-value mono">{report.total_tokens.toLocaleString()}</div>
        </div>
        <div className="report-field">
          <div className="report-label">Cost</div>
          <div
            className="report-value mono"
            title={report.cost_breakdown
              ? `Haiku $${report.cost_breakdown.haiku_input_usd.toFixed(4)}in + $${report.cost_breakdown.haiku_output_usd.toFixed(4)}out · Sonnet $${report.cost_breakdown.sonnet_input_usd.toFixed(4)}in + $${report.cost_breakdown.sonnet_output_usd.toFixed(4)}out · Cache write $${report.cost_breakdown.cache_write_usd.toFixed(4)} · Cache read $${report.cost_breakdown.cache_read_usd.toFixed(4)}`
              : 'Sonnet $3/MTok in · $15/MTok out'}
          >
            ${(report.cost_usd ?? ((report.input_tokens * 0.000003) + (report.output_tokens * 0.000015))).toFixed(4)}
            {report.cache_read_input_tokens && report.cache_read_input_tokens > 0 ? (
              <span style={{ marginLeft: 4, fontSize: 9, color: 'var(--green)' }} title="Cache hits reduced cost">↓</span>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
