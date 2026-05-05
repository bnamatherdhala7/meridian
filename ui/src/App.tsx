import { useCallback, useReducer, useRef, useState } from 'react'
import type { AppStatus, EvalResults, FSMState, IncidentReport, MTTDData, PreTriageEntry, ScenarioMeta, SSEEvent, ToolCall } from './types'
import FSMDiagram from './components/FSMDiagram'
import ToolCallFeed from './components/ToolCallFeed'
import EvidencePanel from './components/EvidencePanel'
import ReportPanel from './components/ReportPanel'
import EvaluatorPanel from './components/EvaluatorPanel'

interface State {
  status: AppStatus
  fsmState: FSMState
  fsmHistory: FSMState[]
  toolCalls: ToolCall[]
  evidence: string[]
  totalTokens: number
  report: IncidentReport | null
  evalResults: EvalResults | null
  mttdData: MTTDData | null
  preTriageEntry: PreTriageEntry | null
  error: string | null
}

const INITIAL: State = {
  status: 'idle',
  fsmState: 'IDLE',
  fsmHistory: [],
  toolCalls: [],
  evidence: [],
  totalTokens: 0,
  report: null,
  evalResults: null,
  mttdData: null,
  preTriageEntry: null,
  error: null,
}

type Action =
  | { type: 'RESET' }
  | { type: 'STATE_CHANGE'; state: FSMState }
  | { type: 'TOOL_CALL'; call: ToolCall }
  | { type: 'PRE_TRIAGE'; entry: PreTriageEntry }
  | { type: 'REPORT'; report: IncidentReport }
  | { type: 'EVAL_RESULTS'; results: EvalResults }
  | { type: 'MTTD'; data: MTTDData }
  | { type: 'SET_STATUS'; status: AppStatus }
  | { type: 'ERROR'; message: string }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'RESET':
      return { ...INITIAL, status: 'running' }
    case 'STATE_CHANGE':
      return {
        ...state,
        fsmState: action.state,
        fsmHistory: state.fsmHistory.includes(action.state)
          ? state.fsmHistory
          : [...state.fsmHistory, action.state],
      }
    case 'TOOL_CALL':
      return { ...state, toolCalls: [...state.toolCalls, action.call] }
    case 'REPORT':
      return {
        ...state,
        report: action.report,
        evidence: action.report.evidence,
        totalTokens: action.report.total_tokens,
        status: 'evaluating',
      }
    case 'EVAL_RESULTS':
      return { ...state, evalResults: action.results, status: 'done' }
    case 'PRE_TRIAGE':
      return { ...state, preTriageEntry: action.entry }
    case 'MTTD':
      return { ...state, mttdData: action.data }
    case 'SET_STATUS':
      return { ...state, status: action.status }
    case 'ERROR':
      return { ...state, error: action.message, status: 'error' }
    default:
      return state
  }
}

const STATUS_LABEL: Record<AppStatus, string> = {
  idle: 'Ready',
  running: 'Investigating',
  evaluating: 'Evaluating',
  done: 'Complete',
  error: 'Error',
}

const SCENARIOS: ScenarioMeta[] = [
  {
    id: 'packet_loss',
    label: 'Packet Loss',
    incident_id: 'INC-20240214-001',
    severity: 'P2',
    site: 'San Jose',
    title: 'High packet loss on sj-catalyst-01 / GigE0/1',
    expected_path: 'ESCALATING',
  },
  {
    id: 'bgp_flap',
    label: 'BGP Flap',
    incident_id: 'INC-20240215-002',
    severity: 'P2',
    site: 'San Jose',
    title: 'BGP peer flapping on sj-edge-01 / GigE0/0',
    expected_path: 'REMEDIATING',
  },
  {
    id: 'cpu_spike',
    label: 'CPU Spike',
    incident_id: 'INC-20240215-003',
    severity: 'P1',
    site: 'San Jose',
    title: 'CPU 94% on sj-core-01, BGP/STP degraded',
    expected_path: 'ESCALATING',
  },
  {
    id: 'false_positive',
    label: 'False Positive',
    incident_id: 'INC-20240214-003',
    severity: 'P3',
    site: 'San Jose',
    title: 'CPU threshold_breach — 5 repeat fires, no corroboration',
    expected_path: 'SUPPRESSED',
  },
]

const PATH_COLOR: Record<string, string> = {
  ESCALATING: 'var(--orange)',
  REMEDIATING: 'var(--green)',
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, INITIAL)
  const [scenarioId, setScenarioId] = useState<string>('packet_loss')
  const esRef = useRef<EventSource | null>(null)

  const selectedScenario = SCENARIOS.find(s => s.id === scenarioId) ?? SCENARIOS[0]

  const startInvestigation = useCallback(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }

    dispatch({ type: 'RESET' })

    let toolCallSeq = 0
    const es = new EventSource(`/api/run?scenario=${scenarioId}`)
    esRef.current = es

    es.onmessage = (e: MessageEvent) => {
      const event = JSON.parse(e.data) as SSEEvent

      switch (event.type) {
        case 'state_change':
          if (event.state) dispatch({ type: 'STATE_CHANGE', state: event.state as FSMState })
          break
        case 'tool_call':
          dispatch({
            type: 'TOOL_CALL',
            call: {
              id: `tc-${++toolCallSeq}`,
              tool: event.tool,
              input_preview: event.input_preview,
              result_preview: event.result_preview,
              input_full: event.input_full,
              result_full: event.result_full,
              duration_ms: event.duration_ms,
              anomaly: event.anomaly,
              timestamp: Date.now(),
            },
          })
          break
        case 'report':
          dispatch({ type: 'REPORT', report: event.data })
          break
        case 'eval_results':
          dispatch({ type: 'EVAL_RESULTS', results: event.data })
          break
        case 'pre_triage':
          dispatch({
            type: 'PRE_TRIAGE',
            entry: {
              alert_id: event.alert_id,
              alert_type: event.alert_type,
              confidence_band: event.confidence_band as PreTriageEntry['confidence_band'],
              confidence_score: event.confidence_score,
              signal_strength: event.signal_strength,
              recommended_action: event.recommended_action as PreTriageEntry['recommended_action'],
              suppression_reason: event.suppression_reason,
              escalate_immediately: event.escalate_immediately,
              scoring_rationale: event.scoring_rationale,
              tokens_used: 0,
            },
          })
          break
        case 'mttd':
          dispatch({ type: 'MTTD', data: event.data })
          break
        case 'error':
          dispatch({ type: 'ERROR', message: event.message })
          es.close()
          break
        case 'done':
          es.close()
          esRef.current = null
          break
      }
    }

    es.onerror = () => {
      dispatch({ type: 'ERROR', message: 'Connection lost. Is the API server running?' })
      es.close()
      esRef.current = null
    }
  }, [scenarioId])

  const handleScenarioChange = useCallback((id: string) => {
    if (state.status === 'running' || state.status === 'evaluating') return
    setScenarioId(id)
    dispatch({ type: 'RESET' })
    dispatch({ type: 'SET_STATUS', status: 'idle' })
  }, [state.status])

  const { status, fsmState, fsmHistory, toolCalls, evidence, totalTokens, report, evalResults, mttdData, preTriageEntry, error } = state
  const busy = status === 'running' || status === 'evaluating'

  return (
    <>
      {/* Fixed header */}
      <header className="app-header">
        <span className="wordmark">VIGIL</span>
        <div className="header-divider" />

        {/* Scenario selector */}
        <div className="scenario-tabs">
          {SCENARIOS.map(s => (
            <button
              key={s.id}
              className={`scenario-tab${scenarioId === s.id ? ' active' : ''}`}
              onClick={() => handleScenarioChange(s.id)}
              disabled={busy}
              title={s.title}
            >
              <span className={`scenario-tab-severity sev-${s.severity.toLowerCase()}`}>{s.severity}</span>
              {s.label}
              <span
                className="scenario-tab-path"
                style={{ color: PATH_COLOR[s.expected_path] ?? 'var(--subtle)' }}
              >
                → {s.expected_path}
              </span>
            </button>
          ))}
        </div>

        <div className="header-divider" />

        <div className="header-incident">
          <span className="header-incident-id">
            {selectedScenario.incident_id} · {selectedScenario.severity} · {selectedScenario.site}
          </span>
          <span className="header-incident-title">{selectedScenario.title}</span>
        </div>

        <div className="header-right">
          {totalTokens > 0 && (
            <span className="header-tokens">
              <span>{totalTokens.toLocaleString()}</span> tokens
            </span>
          )}
          {mttdData && (
            <span className="header-mttd" title={mttdData.headline}>
              <span className="header-mttd-value">{mttdData.mttr_speedup_pct.toFixed(0)}%</span>
              {' '}faster · {Math.round(mttdData.mttr_vigil_s)}s vs {Math.round(mttdData.mttr_baseline_s / 60)}min
            </span>
          )}
          <span className={`status-pill ${status}`}>{STATUS_LABEL[status]}</span>
          <button
            className="btn-run"
            onClick={startInvestigation}
            disabled={busy}
            aria-label="Run investigation"
          >
            {busy ? 'Running…' : 'Run Investigation'}
          </button>
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div className="error-banner">
          <span className="error-banner-icon">⚠</span>
          <span>{error}</span>
          {error.toLowerCase().includes('api') || error.toLowerCase().includes('auth') ? (
            <span className="error-banner-hint"> — check that ANTHROPIC_API_KEY is set</span>
          ) : null}
        </div>
      )}

      {/* Main content */}
      <main className={`app-main${error ? ' app-main--has-banner' : ''}`}>
        {/* FSM diagram */}
        <div className="card fsm-card">
          <div className="card-header">
            <span className="card-title">FSM State Machine</span>
            <span className="card-count" style={{ fontFamily: 'var(--font-mono)', fontSize: 9 }}>
              {fsmState}
            </span>
          </div>
          <FSMDiagram currentState={fsmState} history={fsmHistory} />
        </div>

        {/* Three-column middle */}
        <div className="middle-row">
          {/* Tool Calls */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <div className="card-header">
              <span className="card-title">Tool Calls</span>
              {toolCalls.length > 0 && (
                <span className="card-count">{toolCalls.length}</span>
              )}
            </div>
            <div className="card-body">
              <ToolCallFeed calls={toolCalls} preTriageEntry={preTriageEntry} />
            </div>
          </div>

          {/* Evidence */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <div className="card-header">
              <span className="card-title">Evidence</span>
              {evidence.length > 0 && (
                <span className="card-count">{evidence.length}</span>
              )}
            </div>
            <div className="card-body">
              <EvidencePanel evidence={evidence} />
            </div>
          </div>

          {/* Report */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <div className="card-header">
              <span className="card-title">Incident Report</span>
            </div>
            <div className="card-body">
              <ReportPanel report={report} />
            </div>
          </div>
        </div>

        {/* Evaluator */}
        <div className="card eval-card">
          <div className="card-header">
            <span className="card-title">Phase 3 — Evaluator</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--muted)' }}>
              Generic vs Constrained · Precision · Recall · Token Cost
            </span>
          </div>
          <EvaluatorPanel results={evalResults} running={status === 'evaluating'} />
        </div>
      </main>
    </>
  )
}
