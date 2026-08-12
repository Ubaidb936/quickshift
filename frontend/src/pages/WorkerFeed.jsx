import { useState, useEffect } from 'react'
import api from '../services/api'
import ShiftCard from '../components/ShiftCard'

export default function WorkerFeed() {
  const [shifts, setShifts] = useState([])
  const [applied, setApplied] = useState(new Set())
  const [toast, setToast] = useState('')

  useEffect(() => {
    api.get('/shifts').then(({ data }) => setShifts(data))
  }, [])

  const showInterest = async (shiftId) => {
    try {
      await api.post(`/matches/interest/${shiftId}`)
      setApplied(prev => new Set([...prev, shiftId]))
      setToast('Interest shown! The business will review your profile.')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Something went wrong')
    }
    setTimeout(() => setToast(''), 3000)
  }

  return (
    <div>
      <h2>Available Shifts</h2>
      {toast && <div className="toast">{toast}</div>}
      {shifts.length === 0 && <p className="empty">No shifts available right now. Check back soon.</p>}
      {shifts.map(shift => (
        <ShiftCard
          key={shift.id}
          shift={shift}
          applied={applied.has(shift.id)}
          onApply={() => showInterest(shift.id)}
        />
      ))}
    </div>
  )
}
