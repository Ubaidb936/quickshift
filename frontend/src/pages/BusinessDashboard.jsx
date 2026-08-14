import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'

export default function BusinessDashboard() {
  const [shifts, setShifts] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState({ message: '', type: 'success' })
  const [confirmDelete, setConfirmDelete] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/shifts/my-shifts')
      .then(({ data }) => setShifts(data))
      .finally(() => setLoading(false))
  }, [])

  const pauseShift = async (id) => {
    const { data } = await api.patch(`/shifts/${id}/pause`)
    setShifts(shifts.map(s => s.id === id ? { ...s, status: data.status } : s))
    setToast({ message: `Shift ${data.status}`, type: 'success' })
  }

  const deleteShift = async (id) => {
    await api.delete(`/shifts/${id}`)
    setShifts(shifts.filter(s => s.id !== id))
    setConfirmDelete(null)
    setToast({ message: 'Shift deleted', type: 'success' })
  }

  if (loading) return <div className="container"><Spinner text="Loading your shifts..." /></div>

  return (
    <div className="container">
      {confirmDelete && (
        <ConfirmDialog
          message="Are you sure you want to delete this shift? This cannot be undone."
          onConfirm={() => deleteShift(confirmDelete)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
      <div className="dashboard-header">
        <div>
          <h2 className="page-title">My Shifts</h2>
          <p className="page-subtitle">{shifts.length} shift{shifts.length !== 1 ? 's' : ''} posted</p>
        </div>
        <Link to="/shifts/create" className="btn-primary">+ Post Shift</Link>
      </div>
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '' })} />
      {shifts.length === 0
        ? <EmptyState icon="📬" title="No shifts yet" description="Post your first shift to start finding workers." action="Post a Shift" onAction={() => navigate('/shifts/create')} />
        : shifts.map(shift => (
            <div key={shift.id} className={`shift-card status-${shift.status}`}>
              <div className="shift-header">
                <h3>{shift.position}</h3>
                <span className="pay">${shift.pay_rate}/hr</span>
              </div>
              <p>{shift.num_workers} worker{shift.num_workers > 1 ? 's' : ''} needed</p>
              <p style={{ marginTop: '0.35rem' }}>
                Status: <span className={`status-badge status-${shift.status}`}>{shift.status}</span>
              </p>
              {shift.duties && <p style={{ marginTop: '0.35rem' }}><strong>Duties:</strong> {shift.duties}</p>}
              <div className="actions">
                <button onClick={() => navigate(`/shifts/${shift.id}/applicants`)}>View Applicants</button>
                <button onClick={() => pauseShift(shift.id)}>
                  {shift.status === 'active' ? 'Pause' : 'Resume'}
                </button>
                <button className="btn-danger" onClick={() => setConfirmDelete(shift.id)}>Delete</button>
              </div>
            </div>
          ))
      }
    </div>
  )
}
