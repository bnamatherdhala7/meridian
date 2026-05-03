import { useEffect, useRef } from 'react'
import type { ToolCall } from '../types'

interface Props {
  calls: ToolCall[]
}

const TOOL_BADGE: Record<string, string> = {
  run_spl_query: 'sp',
  search_indexes: 'sp',
  get_knowledge_objects: 'sp',
  generate_spl: 'generate',
  get_network_topology: 'ci',
  get_telemetry_metrics: 'ci',
}

const TOOL_LABEL: Record<string, string> = {
  run_spl_query: 'run_spl',
  search_indexes: 'search_idx',
  get_knowledge_objects: 'knowledge',
  generate_spl: 'gen_spl',
  get_network_topology: 'topology',
  get_telemetry_metrics: 'telemetry',
}

export default function ToolCallFeed({ calls }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [calls.length])

  if (calls.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">⚡</div>
        <div className="empty-text">awaiting tool calls</div>
      </div>
    )
  }

  return (
    <div className="tool-list">
      {calls.map((call, i) => (
        <div key={call.id} className="tool-item">
          <div className="tool-item-top">
            <span className={`tool-badge ${TOOL_BADGE[call.tool] ?? 'sp'}`}>
              {String(i + 1).padStart(2, '0')} {TOOL_LABEL[call.tool] ?? call.tool}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              {call.anomaly && <div className="tool-anomaly-dot" title="Anomaly detected" />}
              <span className="tool-timing">{call.duration_ms}ms</span>
            </div>
          </div>
          {call.result_preview && (
            <div className="tool-preview" title={call.result_preview}>
              {call.result_preview}
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
