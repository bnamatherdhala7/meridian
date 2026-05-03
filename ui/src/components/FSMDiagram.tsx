import type { FSMState } from '../types'

interface Props {
  currentState: FSMState
  history: FSMState[]
}

const STATE_ORDER: FSMState[] = [
  'IDLE', 'TRIAGE', 'INVESTIGATING', 'HYPOTHESIZING',
]
const TERMINAL_STATES: FSMState[] = ['REMEDIATING', 'ESCALATING']

function nodeClass(state: FSMState, current: FSMState, history: FSMState[]): string {
  const base = 'fsm-node'
  const lower = state.toLowerCase()
  if (state === current) return `${base} active ${lower}`
  if (history.includes(state)) return `${base} visited`
  return base
}

export default function FSMDiagram({ currentState, history }: Props) {
  const arrowColor = (fromState: FSMState): string => {
    if (history.includes(fromState)) return 'rgba(255,255,255,0.2)'
    return 'rgba(58,53,48,1)'
  }

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

      {/* Branch: HYPOTHESIZING → REMEDIATING / ESCALATING */}
      <div className="fsm-branch-wrap">
        {/* Branch arrows SVG */}
        <svg
          className="fsm-branch-svg"
          width="28"
          height="68"
          viewBox="0 0 28 68"
          fill="none"
        >
          {/* top branch to REMEDIATING */}
          <path
            d="M4 34 C10 34, 18 12, 26 12"
            stroke={history.includes('HYPOTHESIZING') || history.includes('REMEDIATING') || currentState === 'HYPOTHESIZING'
              ? 'rgba(255,255,255,0.2)'
              : 'rgba(58,53,48,1)'}
            strokeWidth="1"
            fill="none"
          />
          <polygon
            points="26,9 30,12 26,15"
            fill={history.includes('REMEDIATING') ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
          {/* bottom branch to ESCALATING */}
          <path
            d="M4 34 C10 34, 18 56, 26 56"
            stroke={history.includes('HYPOTHESIZING') || history.includes('ESCALATING') || currentState === 'HYPOTHESIZING'
              ? 'rgba(255,255,255,0.2)'
              : 'rgba(58,53,48,1)'}
            strokeWidth="1"
            fill="none"
          />
          <polygon
            points="26,53 30,56 26,59"
            fill={history.includes('ESCALATING') ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
        </svg>

        {/* Terminal state nodes */}
        <div className="fsm-terminals">
          {TERMINAL_STATES.map(state => (
            <div key={state} className={nodeClass(state, currentState, history)}>
              {state}
            </div>
          ))}
        </div>

        {/* Merge arrows SVG */}
        <svg
          className="fsm-branch-svg"
          width="28"
          height="68"
          viewBox="0 0 28 68"
          fill="none"
        >
          <path
            d="M2 12 C10 12, 18 34, 24 34"
            stroke={history.includes('REMEDIATING') ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
            strokeWidth="1"
            fill="none"
          />
          <path
            d="M2 56 C10 56, 18 34, 24 34"
            stroke={history.includes('ESCALATING') ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
            strokeWidth="1"
            fill="none"
          />
          <polygon
            points="22,31 26,34 22,37"
            fill={history.includes('RESOLVED') ? 'rgba(255,255,255,0.2)' : 'rgba(58,53,48,1)'}
          />
        </svg>
      </div>

      {/* RESOLVED */}
      <div className={nodeClass('RESOLVED', currentState, history)}>RESOLVED</div>
    </div>
  )
}
