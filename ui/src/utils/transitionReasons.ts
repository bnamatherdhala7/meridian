import type { FSMState } from '../types'

// Default reasoning for each FSM transition — surfaced inline in the trace feed
// so the operator sees WHY the agent moved to the next state, not just THAT it did.
const REASONS: Record<string, string> = {
  'IDLE→PRE_TRIAGE':         'Investigation started',
  'PRE_TRIAGE→TRIAGE':       'Alert score above threshold — proceeding to investigation',
  'PRE_TRIAGE→SUPPRESSED':   'Confidence band low + no corroborating signals — suppressed at 0 tokens',
  'PRE_TRIAGE→ESCALATING':   'Confidence ≥ 0.95 + security signal type — escalate immediately',
  'TRIAGE→INVESTIGATING':    'Data sources confirmed, RAG SPL patterns retrieved — gathering telemetry',
  'INVESTIGATING→HYPOTHESIZING': 'Evidence collected, incident memory consulted — forming root cause',
  'HYPOTHESIZING→REMEDIATING':   'Incident memory match ≥ 0.75 with known safe fix — automating',
  'HYPOTHESIZING→ESCALATING':    'Threshold rule fired or blast radius too high — handing to human',
  'REMEDIATING→RESOLVED':    'Remediation applied — investigation closed',
  'ESCALATING→RESOLVED':     'Handed off to operator — investigation closed',
}

export function transitionReason(from: FSMState, to: FSMState): string {
  return REASONS[`${from}→${to}`] ?? `Transition: ${from} → ${to}`
}
