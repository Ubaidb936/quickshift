import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerWorker, saveUser } from '../services/auth'

export default function RegisterWorker() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', location: '', profession: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await registerWorker(form)
      saveUser(data)
      navigate('/feed')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className="auth-wrapper">
      <div className="auth-page">
        <div className="auth-logo">
          <Link to="/">
            <span className="brand-icon">⚡</span>Quick<span>Shift</span>
          </Link>
        </div>
        <div className="auth-role-badge worker">👷 Worker Account</div>
        <h2>Create Worker Account</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input placeholder="Full Name" value={form.name} onChange={set('name')} required />
          <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required />
          <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
          <input placeholder="Location (e.g. San Francisco, CA)" value={form.location} onChange={set('location')} />
          <input placeholder="Profession (e.g. Bartender, Forklift Operator)" value={form.profession} onChange={set('profession')} />
          <button type="submit">Create Worker Account</button>
        </form>
        <p>Already have an account? <Link to="/login">Sign in</Link></p>
        <p><Link to="/">← Back to home</Link></p>
      </div>
    </div>
  )
}
