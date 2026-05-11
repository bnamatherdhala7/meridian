import type { EvalResults, FeedItem, FSMState, IncidentReport, MTTDData, ScenarioMeta } from '../types'

export interface ArchivedRun {
  id: string
  scenarioMeta: ScenarioMeta
  startTimeMs: number
  endTimeMs: number
  durationMs: number
  finalState: FSMState
  fsmHistory: FSMState[]
  feedItems: FeedItem[]
  report: IncidentReport | null
  evalResults: EvalResults | null
  mttdData: MTTDData | null
  totalTokens: number
}

const KEY = 'vigil-run-history'
const MAX_RUNS = 10

export function getArchivedRuns(): ArchivedRun[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveArchivedRun(run: ArchivedRun): ArchivedRun[] {
  const existing = getArchivedRuns()
  const next = [run, ...existing].slice(0, MAX_RUNS)
  try {
    window.localStorage.setItem(KEY, JSON.stringify(next))
  } catch {
    // localStorage quota exceeded — drop oldest until it fits
    let trimmed = next.slice(0, Math.floor(next.length / 2))
    while (trimmed.length > 0) {
      try {
        window.localStorage.setItem(KEY, JSON.stringify(trimmed))
        return trimmed
      } catch {
        trimmed = trimmed.slice(0, Math.floor(trimmed.length / 2))
      }
    }
  }
  return next
}

export function clearArchivedRuns(): void {
  try {
    window.localStorage.removeItem(KEY)
  } catch {
    // ignore
  }
}

export function newRunId(): string {
  return `run-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}
