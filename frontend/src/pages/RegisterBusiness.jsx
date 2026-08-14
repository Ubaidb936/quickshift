import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerBusiness, saveUser } from '../services/auth'

export default function RegisterBusiness() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', location: '', working_hours: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await registerBusiness(form)
      saveUser(data)
      navigate('/dashboard')
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
        <div className="auth-role-badge business">🏢 Business Account</div>
        <h2>Create Business Account</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input placeholder="Business Name" value={form.name} onChange={set('name')} required />
          <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required />
          <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
          <input placeholder="Location (e.g. San Francisco, CA)" value={form.location} onChange={set('location')} />
          <input placeholder="Working Hours (e.g. 9am – 5pm)" value={form.working_hours} onChange={set('working_hours')} />
          <button type="submit">Create Business Account</button>
        </form>
        <p>Already have an account? <Link to="/login">Sign in</Link></p>
        <p><Link to="/">← Back to home</Link></p>
      </div>
    </div>
  )
}
