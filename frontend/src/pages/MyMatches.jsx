import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import Spinner from '../components/Spinner'
import EmptyState from '../components/EmptyState'

export default function MyMatches() {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/matches/my-matches')
      .then(({ data }) => setMatches(data))
      .finally(() => setLoading(false))
  }, [])

  const markUnavailable = async (matchId) => {
    await api.patch(`/matches/${matchId}/unavailable`)
    setMatches(matches.map(m => m.id === matchId ? { ...m, status: 'unavailable' } : m))
  }

  if (loading) return <div className="container"><Spinner text="Loading applications..." /></div>

  return (
    <div className="container">
      <div className="feed-header">
        <h2 className="page-title">My Applications</h2>
        <p className="page-subtitle">{matches.length} application{matches.length !== 1 ? 's' : ''} submitted</p>
      </div>
      {matches.length === 0
        ? <EmptyState icon="📩" title="No applications yet" description="Browse available shifts and show interest to get started." action="Browse Shifts" onAction={() => navigate('/feed')} />
        : matches.map(match => (
            <div key={match.id} className="shift-card">
              <div className="shift-header">
                <h3>{match.shift_position}</h3>
                <span className="pay">${match.shift_pay_rate}/hr</span>
              </div>
              <span className={`status-badge status-${match.status}`}>{match.status}</span>
              {match.status === 'interested' && (
                <div className="actions" style={{ marginTop: '0.75rem' }}>
                  <button onClick={() => markUnavailable(match.id)}>Mark Unavailable</button>
                </div>
              )}
            </div>
          ))
      }
    </div>
  )
}
