import { useState, useEffect } from 'react'
import api from '../services/api'
import ShiftCard from '../components/ShiftCard'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'

export default function WorkerFeed() {
  const [shifts, setShifts] = useState([])
  const [applied, setApplied] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState({ message: '', type: 'success' })

  useEffect(() => {
    api.get('/shifts')
      .then(({ data }) => setShifts(data))
      .finally(() => setLoading(false))
  }, [])

  const showInterest = async (shiftId) => {
    try {
      await api.post(`/matches/interest/${shiftId}`)
      setApplied(prev => new Set([...prev, shiftId]))
      setToast({ message: 'Interest shown! The business will review your profile.', type: 'success' })
    } catch (err) {
      setToast({ message: err.response?.data?.detail || 'Something went wrong', type: 'error' })
    }
  }

  if (loading) return <Spinner text="Loading shifts..." />

  return (
    <div>
      <h2 className="page-title">Available Shifts</h2>
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '' })} />
      {shifts.length === 0
        ? <EmptyState icon="📋" title="No shifts available" description="Check back soon — new shifts are posted daily." />
        : shifts.map(shift => (
            <ShiftCard
              key={shift.id}
              shift={shift}
              applied={applied.has(shift.id)}
              onApply={() => showInterest(shift.id)}
            />
          ))
      }
    </div>
  )
}
