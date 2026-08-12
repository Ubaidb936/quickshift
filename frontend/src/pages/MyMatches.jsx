import { useState, useEffect } from 'react'
import api from '../services/api'

const STATUS_COLOR = {
  interested: '#f59e0b',
  accepted: '#10b981',
  declined: '#ef4444',
  unavailable: '#6b7280',
}

export default function MyMatches() {
  const [matches, setMatches] = useState([])

  useEffect(() => {
    api.get('/matches/my-matches').then(({ data }) => setMatches(data))
  }, [])

  const markUnavailable = async (matchId) => {
    await api.patch(`/matches/${matchId}/unavailable`)
    setMatches(matches.map(m => m.id === matchId ? { ...m, status: 'unavailable' } : m))
  }

  return (
    <div>
      <h2>My Applications</h2>
      {matches.length === 0 && <p className="empty">You haven't shown interest in any shifts yet.</p>}
      {matches.map(match => (
        <div key={match.id} className="shift-card">
          <div className="shift-header">
            <h3>{match.shift_position}</h3>
            <span className="pay">${match.shift_pay_rate}/hr</span>
          </div>
          <p style={{ color: STATUS_COLOR[match.status], fontWeight: 600 }}>
            {match.status.toUpperCase()}
          </p>
          {match.status === 'interested' && (
            <button onClick={() => markUnavailable(match.id)} style={{ marginTop: '0.75rem' }}>
              Mark Unavailable
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
