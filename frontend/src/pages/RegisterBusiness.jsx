import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerBusiness, saveUser } from '../services/auth'

const INDUSTRIES = ['Restaurant', 'Retail', 'Events', 'Healthcare', 'Warehouse', 'Hospitality', 'Other']
const TEAM_SIZES = ['Small (1–10)', 'Medium (11–50)', 'Large (50+)']
const VIBE_OPTIONS = ['Fast-paced', 'Relaxed', 'Upscale', 'Casual', 'Outdoor', 'Physical', 'Customer-facing', 'Indoor']

export default function RegisterBusiness() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', email: '', password: '', location: '', working_hours: '',
    phone: '', logo_url: '', industry: '', description: '', vibe: '', team_size: ''
  })
  const [selectedVibes, setSelectedVibes] = useState([])
  const [error, setError] = useState('')
  const [step, setStep] = useState(1)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await registerBusiness({ ...form, vibe: selectedVibes.join(',') })
      saveUser(data)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const toggleVibe = (v) => {
    setSelectedVibes(prev =>
      prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v]
    )
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-page auth-page--wide">
        <div className="auth-logo">
          <Link to="/">
            <span className="brand-icon">⚡</span>Quick<span>Shift</span>
          </Link>
        </div>
        <div className="auth-role-badge business">🏢 Business Account</div>
        <h2>Create Business Account</h2>
        <div className="step-indicator">
          <div className={`step-dot ${step >= 1 ? 'active' : ''}`} />
          <div className="step-line" />
          <div className={`step-dot ${step >= 2 ? 'active' : ''}`} />
        </div>
        {error && <p className="error">{error}</p>}

        <form onSubmit={handleSubmit}>
          {step === 1 && (
            <>
              <div className="form-section-label">Basic Info</div>
              <input placeholder="Business Name" value={form.name} onChange={set('name')} required />
              <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required />
              <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
              <input placeholder="Phone number" value={form.phone} onChange={set('phone')} />
              <input placeholder="Location (e.g. San Francisco, CA)" value={form.location} onChange={set('location')} />
              <input placeholder="Working Hours (e.g. 9am – 5pm)" value={form.working_hours} onChange={set('working_hours')} />
              <input placeholder="Logo URL (optional)" value={form.logo_url} onChange={set('logo_url')} />
              <button type="button" onClick={() => setStep(2)}>Next →</button>
            </>
          )}

          {step === 2 && (
            <>
              <div className="form-section-label">About Your Business</div>
              <select value={form.industry} onChange={set('industry')}>
                <option value="">Select industry</option>
                {INDUSTRIES.map(i => <option key={i} value={i.toLowerCase()}>{i}</option>)}
              </select>

              <select value={form.team_size} onChange={set('team_size')}>
                <option value="">Select team size</option>
                {TEAM_SIZES.map(t => <option key={t} value={t.split(' ')[0].toLowerCase()}>{t}</option>)}
              </select>

              <textarea
                placeholder="Describe your business — environment, culture, what it's like to work here..."
                value={form.description}
                onChange={set('description')}
                rows={4}
              />

              <div className="form-section-label">Vibe <span className="form-hint">Select all that apply</span></div>
              <div className="vibe-tags">
                {VIBE_OPTIONS.map(v => (
                  <button
                    key={v}
                    type="button"
                    className={`vibe-tag ${selectedVibes.includes(v) ? 'vibe-tag--active' : ''}`}
                    onClick={() => toggleVibe(v)}
                  >
                    {v}
                  </button>
                ))}
              </div>

              <div className="step-actions">
                <button type="button" className="btn-back" onClick={() => setStep(1)}>← Back</button>
                <button type="submit">Create Account</button>
              </div>
            </>
          )}
        </form>
        <p>Already have an account? <Link to="/login">Sign in</Link></p>
        <p><Link to="/">← Back to home</Link></p>
      </div>
    </div>
  )
}