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

export interface RagHitItem {
  id: string
  title: string
  score: number
  text: string
  tags: string[]
  phase: string | null
  outcome: string | null
}

export interface RagEvent {
  layer: 'SPL' | 'Incident'
  phase: string
  query: string
  hits: RagHitItem[]
}

export interface StateTransitionEntry {
  from_state: FSMState
  to_state: FSMState
  reason: string
}

export interface ForecastTriggerEntry {
  metric: string
  device: string
  trigger_type: 'threshold' | 'trajectory' | 'uncertainty'
  severity: 'critical' | 'warning' | 'info'
  projected_minutes_ahead: number | null
  message: string
  confidence: number
  model: string
}

// Unified chronological feed item — timestamp_ms is epoch ms set at dispatch
export type FeedItem =
  | { kind: 'pre_triage'; id: string; timestamp_ms: number; data: PreTriageEntry }
  | { kind: 'rag';        id: string; timestamp_ms: number; data: RagEvent }
  | { kind: 'tool';       id: string; timestamp_ms: number; data: ToolCall }
  | { kind: 'state';      id: string; timestamp_ms: number; data: StateTransitionEntry }
  | { kind: 'forecast';   id: string; timestamp_ms: number; data: ForecastTriggerEntry }

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
  // Cost-reduction fields — present when the backend uses prompt caching + model tiering
  cache_creation_input_tokens?: number
  cache_read_input_tokens?: number
  haiku_input_tokens?: number
  haiku_output_tokens?: number
  sonnet_input_tokens?: number
  sonnet_output_tokens?: number
  cost_usd?: number
  cost_breakdown?: {
    haiku_input_usd: number
    haiku_output_usd: number
    sonnet_input_usd: number
    sonnet_output_usd: number
    cache_write_usd: number
    cache_read_usd: number
    total_usd: number
  }
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
  | { type: 'rag_hit'; layer: 'SPL' | 'Incident'; phase: string; query: string; hits: RagHitItem[] }
  | { type: 'error'; message: string }
  | { type: 'done' }
