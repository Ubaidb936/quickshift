import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'

export default function ShiftApplicants() {
  const { shiftId } = useParams()
  const [matches, setMatches] = useState([])

  useEffect(() => {
    api.get(`/matches/interested/${shiftId}`).then(({ data }) => setMatches(data))
  }, [shiftId])

  const updateStatus = async (matchId, action) => {
    await api.patch(`/matches/${matchId}/${action}`)
    const newStatus = action === 'accept' ? 'accepted' : 'declined'
    setMatches(matches.map(m => m.id === matchId ? { ...m, status: newStatus } : m))
  }

  return (
    <div>
      <div className="dashboard-header">
        <h2>Applicants</h2>
        <Link to="/dashboard" className="btn-secondary">← Back</Link>
      </div>
      {matches.length === 0 && <p className="empty">No workers have shown interest yet.</p>}
      {matches.map(match => (
        <div key={match.id} className={`applicant-card status-${match.status}`}>
          <h3>{match.worker_name}</h3>
          <p>{match.worker_profession} · {match.worker_location}</p>
          <p>Status: <strong>{match.status}</strong></p>
          {match.status === 'interested' && (
            <div className="actions">
              <button className="btn-success" onClick={() => updateStatus(match.id, 'accept')}>Accept</button>
              <button className="btn-danger" onClick={() => updateStatus(match.id, 'decline')}>Decline</button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
