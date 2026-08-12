import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function BusinessDashboard() {
  const [shifts, setShifts] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/shifts/my-shifts').then(({ data }) => setShifts(data))
  }, [])

  const pauseShift = async (id) => {
    const { data } = await api.patch(`/shifts/${id}/pause`)
    setShifts(shifts.map(s => s.id === id ? { ...s, status: data.status } : s))
  }

  const deleteShift = async (id) => {
    await api.delete(`/shifts/${id}`)
    setShifts(shifts.filter(s => s.id !== id))
  }

  return (
    <div>
      <div className="dashboard-header">
        <h2>My Shifts</h2>
        <Link to="/shifts/create" className="btn-primary">+ Post Shift</Link>
      </div>
      {shifts.length === 0 && <p className="empty">No shifts posted yet. Post your first shift to find workers.</p>}
      {shifts.map(shift => (
        <div key={shift.id} className={`shift-card status-${shift.status}`}>
          <div className="shift-header">
            <h3>{shift.position}</h3>
            <span className="pay">${shift.pay_rate}/hr</span>
          </div>
          <p>{shift.num_workers} worker{shift.num_workers > 1 ? 's' : ''} needed</p>
          <p>Status: <strong>{shift.status}</strong></p>
          {shift.duties && <p><strong>Duties:</strong> {shift.duties}</p>}
          <div className="actions">
            <button onClick={() => navigate(`/shifts/${shift.id}/applicants`)}>View Applicants</button>
            <button onClick={() => pauseShift(shift.id)}>
              {shift.status === 'active' ? 'Pause' : 'Resume'}
            </button>
            <button className="btn-danger" onClick={() => deleteShift(shift.id)}>Delete</button>
          </div>
        </div>
      ))}
    </div>
  )
}
