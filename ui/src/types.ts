export type FSMState =
  | 'IDLE'
  | 'PRE_TRIAGE'
  | 'TRIAGE'
  | 'INVESTIGATING'
  | 'HYPOTHESIZING'
  | 'REMEDIATING'
  | 'ESCALATING'
  | 'RESOLVED'
  | 'SUPPRESSED'

export interface PreTriageEntry {
  alert_id: string
  alert_type: string
  confidence_band: 'high' | 'medium' | 'low'
  confidence_score: number
  signal_strength: number
  recommended_action: 'investigate' | 'monitor' | 'suppress'
  suppression_reason: string | null
  escalate_immediately: boolean
  scoring_rationale: string
  tokens_used: 0
}

export interface MTTDData {
  mttd_vigil_s: number
  mttr_vigil_s: number
  mttd_baseline_s: number
  mttr_baseline_s: number
  mttd_speedup_pct: number
  mttr_speedup_pct: number
  headline: string
}

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
  actionability: number
  composite: number
}

export interface EvalResults {
  incident_id: string
  investigation: EvalDimension & { tool_calls: number; duration_secs: number; final_state: string; tool_efficiency: number }
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
  | { type: 'pre_triage'; alert_id: string; alert_type: string; confidence_band: string; confidence_score: number; signal_strength: number; recommended_action: string; suppression_reason: string | null; escalate_immediately: boolean; scoring_rationale: string; tokens_used: 0 }
  | { type: 'mttd'; data: MTTDData }
  | { type: 'error'; message: string }
  | { type: 'done' }
