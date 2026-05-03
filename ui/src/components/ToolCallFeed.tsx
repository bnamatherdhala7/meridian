import { useEffect, useRef, useState } from 'react'
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
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [calls.length])

  function toggle(id: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

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
      {calls.map((call, i) => {
        const isExpanded = expanded.has(call.id)
        return (
          <div key={call.id} className="tool-item">
            <div
              className="tool-item-top"
              onClick={() => toggle(call.id)}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              <span className={`tool-badge ${TOOL_BADGE[call.tool] ?? 'sp'}`}>
                {String(i + 1).padStart(2, '0')} {TOOL_LABEL[call.tool] ?? call.tool}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {call.anomaly && <div className="tool-anomaly-dot" title="Anomaly detected" />}
                <span className="tool-timing">{call.duration_ms}ms</span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  color: 'var(--subtle)',
                  lineHeight: 1,
                }}>
                  {isExpanded ? '▾' : '▸'}
                </span>
              </div>
            </div>
            {call.result_preview && (
              <div className="tool-preview" title={call.result_preview}>
                {call.result_preview}
              </div>
            )}
            {isExpanded && (
              <div className="tool-trace">
                <div className="tool-trace-section">
                  <div className="tool-trace-label">INPUT</div>
                  <pre className="tool-trace-body">{call.input_full || JSON.stringify({ note: 'no input captured' })}</pre>
                </div>
                <div className="tool-trace-section">
                  <div className="tool-trace-label">OUTPUT</div>
                  <pre className="tool-trace-body">{call.result_full || JSON.stringify({ note: 'no output captured' })}</pre>
                </div>
              </div>
            )}
          </div>
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}
