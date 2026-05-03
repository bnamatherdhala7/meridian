interface Props {
  evidence: string[]
}

export default function EvidencePanel({ evidence }: Props) {
  if (evidence.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🔍</div>
        <div className="empty-text">no evidence yet</div>
      </div>
    )
  }

  return (
    <div className="evidence-list">
      {evidence.map((item, i) => (
        <div key={i} className="evidence-item">
          <span className="evidence-bullet">◆</span>
          <span>{item}</span>
        </div>
      ))}
    </div>
  )
}
