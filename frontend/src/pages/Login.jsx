import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login, saveUser } from '../services/auth'

export default function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', role: 'worker' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await login(form.email, form.password, form.role)
      saveUser(data)
      navigate(data.role === 'business' ? '/dashboard' : '/feed')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
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
        <h2>Welcome back</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required />
          <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
          <select value={form.role} onChange={set('role')}>
            <option value="worker">I am a Worker</option>
            <option value="business">I am a Business</option>
          </select>
          <button type="submit">Sign In</button>
        </form>
        <p>No account? <Link to="/register/worker">Register as Worker</Link> or <Link to="/register/business">Business</Link></p>
      </div>
    </div>
  )
}
