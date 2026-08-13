export default function EmptyState({ icon, title, description, action, onAction }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action && <button className="btn-primary" onClick={onAction}>{action}</button>}
    </div>
  )
}
