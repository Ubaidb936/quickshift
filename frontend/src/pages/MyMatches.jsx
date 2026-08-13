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

  if (loading) return <Spinner text="Loading applications..." />

  return (
    <div>
      <h2 className="page-title">My Applications</h2>
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
                <button onClick={() => markUnavailable(match.id)} style={{ marginTop: '0.75rem' }}>
                  Mark Unavailable
                </button>
              )}
            </div>
          ))
      }
    </div>
  )
}
