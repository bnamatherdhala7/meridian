import React from 'react'
import type { EvalResults } from '../types'

interface Props {
  results: EvalResults | null
  running: boolean
}

function PctCell({ value, colorClass }: { value: number; colorClass: string }) {
  const pct = Math.round(value * 100)
  return (
    <div className="eval-cell">
      <div className="bar-wrap">
        <span style={{ fontSize: 10, fontWeight: 600 }}>{pct}%</span>
        <div className="eval-bar-track">
          <div
            className={`eval-bar-fill ${colorClass}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  )
}

function pctClass(v: number): string {
  if (v >= 0.75) return 'pct-high'
  if (v >= 0.5) return 'pct-mid'
  return 'pct-low'
}

export default function EvaluatorPanel({ results, running }: Props) {
  if (!results) {
    return (
      <div className="eval-body">
        <div className="eval-waiting">
          {running ? 'Running evaluator — comparing generic vs constrained output...' : 'Waiting for investigation to complete'}
        </div>
      </div>
    )
  }

  const { investigation: inv, generic: gen, constrained: con, token_savings_pct } = results

  const rows: { label: string; inv: React.ReactNode; gen: React.ReactNode; con: React.ReactNode }[] = [
    {
      label: 'Tokens',
      inv: <div className="eval-cell"><span style={{ color: 'var(--teal)' }}>{inv.total_tokens.toLocaleString()}</span></div>,
      gen: <div className="eval-cell"><span style={{ color: 'var(--orange)' }}>{gen.total_tokens.toLocaleString()}</span></div>,
      con: <div className="eval-cell"><span style={{ color: 'var(--green)' }}>{con.total_tokens.toLocaleString()}</span></div>,
    },
    {
      label: 'Cost',
      inv: <div className="eval-cell" style={{ fontSize: 10 }}>${inv.cost_usd.toFixed(4)}</div>,
      gen: <div className="eval-cell" style={{ fontSize: 10 }}>${gen.cost_usd.toFixed(4)}</div>,
      con: <div className="eval-cell" style={{ fontSize: 10 }}>${con.cost_usd.toFixed(4)}</div>,
    },
    {
      label: 'Precision',
      inv: <PctCell value={inv.precision} colorClass={pctClass(inv.precision)} />,
      gen: <PctCell value={gen.precision} colorClass={pctClass(gen.precision)} />,
      con: <PctCell value={con.precision} colorClass={pctClass(con.precision)} />,
    },
    {
      label: 'Recall',
      inv: <PctCell value={inv.recall} colorClass={pctClass(inv.recall)} />,
      gen: <PctCell value={gen.recall} colorClass={pctClass(gen.recall)} />,
      con: <PctCell value={con.recall} colorClass={pctClass(con.recall)} />,
    },
  ]

  return (
    <div className="eval-body">
      {/* Column headers */}
      <div />
      <div className="eval-col-header investigation">Investigation</div>
      <div className="eval-col-header generic">Generic LLM</div>
      <div className="eval-col-header constrained" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
        Constrained
        <span className="savings-badge">-{token_savings_pct}% tokens</span>
      </div>

      {rows.map(({ label, inv: invCell, gen: genCell, con: conCell }) => (
        <React.Fragment key={label}>
          <div className="eval-row-label">{label}</div>
          <div>{invCell}</div>
          <div>{genCell}</div>
          <div>{conCell}</div>
        </React.Fragment>
      ))}
    </div>
  )
}
