import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerBusiness, registerWorker, saveUser } from '../services/auth'

export default function Register() {
  const navigate = useNavigate()
  const [role, setRole] = useState('worker')
  const [form, setForm] = useState({ name: '', email: '', password: '', location: '', profession: '', working_hours: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const fn = role === 'business' ? registerBusiness : registerWorker
      const { data } = await fn(form)
      saveUser(data)
      navigate(role === 'business' ? '/dashboard' : '/feed')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className="auth-page">
      <h2>Create Account</h2>
      {error && <p className="error">{error}</p>}
      <div className="role-toggle">
        <button type="button" className={role === 'worker' ? 'active' : ''} onClick={() => setRole('worker')}>Worker</button>
        <button type="button" className={role === 'business' ? 'active' : ''} onClick={() => setRole('business')}>Business</button>
      </div>
      <form onSubmit={handleSubmit}>
        <input placeholder="Full Name" value={form.name} onChange={set('name')} required />
        <input type="email" placeholder="Email" value={form.email} onChange={set('email')} required />
        <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
        <input placeholder="Location (e.g. San Francisco, CA)" value={form.location} onChange={set('location')} />
        {role === 'worker'
          ? <input placeholder="Profession (e.g. Bartender, Forklift Operator)" value={form.profession} onChange={set('profession')} />
          : <input placeholder="Working Hours (e.g. 9am - 5pm)" value={form.working_hours} onChange={set('working_hours')} />
        }
        <button type="submit">Register as {role === 'worker' ? 'Worker' : 'Business'}</button>
      </form>
      <p>Have an account? <Link to="/login">Login</Link></p>
    </div>
  )
}
