import type { FSMState } from '../types'

interface Props {
  currentState: FSMState
  history: FSMState[]
}

const STATE_ORDER: FSMState[] = [
  'IDLE', 'PRE_TRIAGE', 'TRIAGE', 'INVESTIGATING', 'HYPOTHESIZING',
]

// States that branch from HYPOTHESIZING → RESOLVED
const HYPOTHESIS_TERMINALS: FSMState[] = ['REMEDIATING', 'ESCALATING']

function nodeClass(state: FSMState, current: FSMState, history: FSMState[]): string {
  const base = 'fsm-node'
  const lower = state.toLowerCase().replace('_', '-')
  if (state === current) return `${base} active ${lower}`
  if (history.includes(state)) return `${base} visited`
  return base
}

function visited(state: FSMState, history: FSMState[]): boolean {
  return history.includes(state)
}

export default function FSMDiagram({ currentState, history }: Props) {
  const arrowColor = (fromState: FSMState): string => {
    if (history.includes(fromState)) return 'rgba(255,255,255,0.2)'
    return 'rgba(58,53,48,1)'
  }

  const suppressed = currentState === 'SUPPRESSED' || history.includes('SUPPRESSED')

  return (
    <div className="fsm-body">
      {/* Linear path */}
      {STATE_ORDER.map((state, i) => (
        <div key={state} style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
          <div className={nodeClass(state, currentState, history)}>{state}</div>
          {i < STATE_ORDER.length - 1 && (
            <div className="fsm-arrow" style={{ color: arrowColor(state) }}>›</div>
          )}
        </div>
      ))}

      {/* Branch: HYPOTHESIZING → REMEDIATING / ESCALATING, PRE_TRIAGE → SUPPRESSED */}
      <div className="fsm-branch-wrap">
        {/* Branch arrows SVG — 3 outputs */}
        <svg
          className="fsm-branch-svg"
          width="28"
          height="100"
          viewBox="0 0 28 100"
          fill="none"
        >
          {/* REMEDIATING branch (top) */}
          <path
            d="M4 50 C10 50, 18 14, 26 14"
            stroke={visited('HYPOTHESIZING', history) || visited('REMEDIATING', history) || currentState === 'HYPOTHESIZING'
              ? 'rgba(255,255,255,0.2)'
              : 'rgba(58,53,48,1)'}
            strokeWidth="1" fill="none"
          />
          <polygon
            points="26,11 30,14 26,17"
            fill={visited('REMEDIATING', history) ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
          {/* ESCALATING branch (middle) */}
          <path
            d="M4 50 C10 50, 18 50, 26 50"
            stroke={visited('HYPOTHESIZING', history) || visited('ESCALATING', history) || currentState === 'HYPOTHESIZING'
              ? 'rgba(255,255,255,0.2)'
              : 'rgba(58,53,48,1)'}
            strokeWidth="1" fill="none"
          />
          <polygon
            points="26,47 30,50 26,53"
            fill={visited('ESCALATING', history) ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
          {/* SUPPRESSED branch (bottom) — dashed, from PRE_TRIAGE conceptually */}
          <path
            d="M4 50 C10 50, 18 86, 26 86"
            stroke={suppressed ? 'rgba(167,139,250,0.35)' : 'rgba(58,53,48,0.6)'}
            strokeWidth="1" strokeDasharray="3 2" fill="none"
          />
          <polygon
            points="26,83 30,86 26,89"
            fill={suppressed ? 'rgba(167,139,250,0.35)' : 'rgba(58,53,48,0.6)'}
          />
        </svg>

        {/* Terminal state nodes */}
        <div className="fsm-terminals">
          {HYPOTHESIS_TERMINALS.map(state => (
            <div key={state} className={nodeClass(state, currentState, history)}>
              {state}
            </div>
          ))}
          {/* SUPPRESSED — PRE_TRIAGE short-circuit terminal */}
          <div
            className={nodeClass('SUPPRESSED', currentState, history)}
            style={{ opacity: suppressed ? 1 : 0.45 }}
          >
            SUPPRESSED
          </div>
        </div>

        {/* Merge arrows — only REMEDIATING + ESCALATING → RESOLVED */}
        <svg
          className="fsm-branch-svg"
          width="28"
          height="100"
          viewBox="0 0 28 100"
          fill="none"
        >
          <path
            d="M2 14 C10 14, 18 34, 24 34"
            stroke={visited('REMEDIATING', history) ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
            strokeWidth="1" fill="none"
          />
          <path
            d="M2 50 C10 50, 18 34, 24 34"
            stroke={visited('ESCALATING', history) ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
            strokeWidth="1" fill="none"
          />
          <polygon
            points="22,31 26,34 22,37"
            fill={visited('RESOLVED', history) ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
          {/* SUPPRESSED has no merge — it's final */}
        </svg>
      </div>

      {/* RESOLVED */}
      <div className={nodeClass('RESOLVED', currentState, history)}>RESOLVED</div>
    </div>
  )
}
