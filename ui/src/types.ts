export type FSMState =
  | 'IDLE'
  | 'TRIAGE'
  | 'INVESTIGATING'
  | 'HYPOTHESIZING'
  | 'REMEDIATING'
  | 'ESCALATING'
  | 'RESOLVED'

export interface ToolCall {
  id: string
  tool: string
  input_preview: string
  result_preview: string
  input_full: string
  result_full: string
  duration_ms: number
  anomaly: boolean
  timestamp: number
}

export interface IncidentReport {
  incident_id: string
  final_state: FSMState
  hypothesis: string
  evidence: string[]
  tool_calls: number
  recommended_action: string
  confidence: number
  total_tokens: number
  input_tokens: number
  output_tokens: number
  duration_secs: number
}

export interface EvalDimension {
  total_tokens: number
  cost_usd: number
  precision: number
  recall: number
}

export interface EvalResults {
  incident_id: string
  investigation: EvalDimension & { tool_calls: number; duration_secs: number; final_state: string }
  generic: EvalDimension
  constrained: EvalDimension & { output?: Record<string, unknown> }
  token_savings_pct: number
}

export interface ScenarioMeta {
  id: string
  label: string
  incident_id: string
  severity: string
  site: string
  title: string
  expected_path: string
}

export type AppStatus = 'idle' | 'running' | 'evaluating' | 'done' | 'error'

export type SSEEvent =
  | { type: 'state_change'; state: string; from_state?: string }
  | { type: 'tool_call'; tool: string; input_preview: string; result_preview: string; input_full: string; result_full: string; duration_ms: number; anomaly: boolean }
  | { type: 'report'; data: IncidentReport }
  | { type: 'eval_results'; data: EvalResults }
  | { type: 'error'; message: string }
  | { type: 'done' }
