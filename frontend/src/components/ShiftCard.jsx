export default function ShiftCard({ shift, applied, onApply }) {
  const fmt = (dt) => dt ? new Date(dt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : 'TBD'

  return (
    <div className="shift-card">
      <div className="shift-header">
        <h3>{shift.position}</h3>
        <span className="pay">${shift.pay_rate}/hr</span>
      </div>
      <p className="business-name">{shift.business_name} · {shift.business_location}</p>
      <p>{fmt(shift.start_time)} → {fmt(shift.end_time)}</p>
      {shift.duties && <p><strong>Duties:</strong> {shift.duties}</p>}
      {shift.attire && <p><strong>Attire:</strong> {shift.attire}</p>}
      <p>{shift.num_workers} worker{shift.num_workers > 1 ? 's' : ''} needed</p>
      <button
        onClick={onApply}
        disabled={applied}
        className={applied ? 'btn-applied' : 'btn-primary'}
        style={{ marginTop: '0.75rem' }}
      >
        {applied ? 'Interest Shown ✓' : 'Show Interest'}
      </button>
    </div>
  )
}
