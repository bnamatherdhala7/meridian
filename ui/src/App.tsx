import { useCallback, useReducer, useRef } from 'react'
import type { AppStatus, EvalResults, FSMState, IncidentReport, SSEEvent, ToolCall } from './types'
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
  error: null,
}

type Action =
  | { type: 'RESET' }
  | { type: 'STATE_CHANGE'; state: FSMState }
  | { type: 'TOOL_CALL'; call: ToolCall }
  | { type: 'REPORT'; report: IncidentReport }
  | { type: 'EVAL_RESULTS'; results: EvalResults }
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

export default function App() {
  const [state, dispatch] = useReducer(reducer, INITIAL)
  const esRef = useRef<EventSource | null>(null)

  const startInvestigation = useCallback(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }

    dispatch({ type: 'RESET' })

    let toolCallSeq = 0
    const es = new EventSource('/api/run')
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
  }, [])

  const { status, fsmState, fsmHistory, toolCalls, evidence, totalTokens, report, evalResults, error } = state

  return (
    <>
      {/* Fixed header */}
      <header className="app-header">
        <span className="wordmark">VIGIL</span>
        <div className="header-divider" />
        <div className="header-incident">
          <span className="header-incident-id">INC-20240214-001 · P2 · San Jose</span>
          <span className="header-incident-title">
            High packet loss on Cisco Catalyst sj-catalyst-01 / GigE0/1
          </span>
        </div>
        <div className="header-right">
          {totalTokens > 0 && (
            <span className="header-tokens">
              <span>{totalTokens.toLocaleString()}</span> tokens
            </span>
          )}
          <span className={`status-pill ${status}`}>{STATUS_LABEL[status]}</span>
          <button
            className="btn-run"
            onClick={startInvestigation}
            disabled={status === 'running' || status === 'evaluating'}
            aria-label="Run investigation"
          >
            {status === 'running' || status === 'evaluating' ? 'Running…' : 'Run Investigation'}
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
              <ToolCallFeed calls={toolCalls} />
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
