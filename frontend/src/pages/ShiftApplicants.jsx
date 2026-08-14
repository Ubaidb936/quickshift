import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ConfirmDialog from '../components/ConfirmDialog'

export default function ShiftApplicants() {
  const { shiftId } = useParams()
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState({ message: '', type: 'success' })
  const [confirm, setConfirm] = useState(null)

  useEffect(() => {
    api.get(`/matches/interested/${shiftId}`)
      .then(({ data }) => setMatches(data))
      .finally(() => setLoading(false))
  }, [shiftId])

  const updateStatus = async (matchId, action) => {
    await api.patch(`/matches/${matchId}/${action}`)
    const newStatus = action === 'accept' ? 'accepted' : 'declined'
    setMatches(matches.map(m => m.id === matchId ? { ...m, status: newStatus } : m))
    setToast({ message: `Worker ${newStatus}`, type: action === 'accept' ? 'success' : 'error' })
    setConfirm(null)
  }

  if (loading) return <div className="container"><Spinner text="Loading applicants..." /></div>

  return (
    <div className="container">
      {confirm && (
        <ConfirmDialog
          message={`Are you sure you want to ${confirm.action} this worker?`}
          onConfirm={() => updateStatus(confirm.id, confirm.action)}
          onCancel={() => setConfirm(null)}
        />
      )}
      <div className="dashboard-header">
        <div>
          <h2 className="page-title">Applicants</h2>
          <p className="page-subtitle">{matches.length} worker{matches.length !== 1 ? 's' : ''} interested</p>
        </div>
        <Link to="/dashboard" className="btn-secondary">← Back to Dashboard</Link>
      </div>
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '' })} />
      {matches.length === 0
        ? <EmptyState icon="👥" title="No applicants yet" description="Workers who show interest in this shift will appear here." />
        : matches.map(match => (
            <div key={match.id} className={`applicant-card status-${match.status}`}>
              <div className="shift-header">
                <h3>{match.worker_name}</h3>
                <span className={`status-badge status-${match.status}`}>{match.status}</span>
              </div>
              <p className="business-name">{match.worker_profession} · {match.worker_location}</p>
              {match.status === 'interested' && (
                <div className="actions">
                  <button className="btn-success" onClick={() => setConfirm({ id: match.id, action: 'accept' })}>Accept</button>
                  <button className="btn-danger" onClick={() => setConfirm({ id: match.id, action: 'decline' })}>Decline</button>
                </div>
              )}
            </div>
          ))
      }
    </div>
  )
}
