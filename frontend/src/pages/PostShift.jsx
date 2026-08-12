import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function PostShift() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    position: '', start_time: '', end_time: '',
    pay_rate: '', duties: '', attire: '', num_workers: 1,
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/shifts/', {
        ...form,
        pay_rate: parseFloat(form.pay_rate),
        num_workers: parseInt(form.num_workers),
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post shift')
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className="form-page">
      <h2>Post a Shift</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input placeholder="Position (e.g. Bartender, Forklift Operator)" value={form.position} onChange={set('position')} required />
        <label>Start Time</label>
        <input type="datetime-local" value={form.start_time} onChange={set('start_time')} required />
        <label>End Time</label>
        <input type="datetime-local" value={form.end_time} onChange={set('end_time')} required />
        <input type="number" placeholder="Pay Rate ($/hr)" value={form.pay_rate} onChange={set('pay_rate')} required min="0" step="0.50" />
        <textarea placeholder="Duties (what will the worker be doing?)" value={form.duties} onChange={set('duties')} rows={3} />
        <input placeholder="Attire (e.g. Black shirt, closed-toe shoes)" value={form.attire} onChange={set('attire')} />
        <input type="number" placeholder="Number of Workers Needed" value={form.num_workers} onChange={set('num_workers')} min="1" />
        <button type="submit">Post Shift</button>
        <button type="button" onClick={() => navigate('/dashboard')}>Cancel</button>
      </form>
    </div>
  )
}
