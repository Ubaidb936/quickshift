import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerWorker, saveUser } from '../services/auth'

export default function RegisterWorker() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', email: '', password: '', location: '', profession: '',
    skills: '', experience_years: '', availability: '', bio: ''
  })
  const [selectedAvailability, setSelectedAvailability] = useState([])
  const [error, setError] = useState('')
  const [step, setStep] = useState(1)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await registerWorker({
        ...form,
        experience_years: form.experience_years ? parseInt(form.experience_years) : undefined,
        availability: selectedAvailability.join(',')
      })
      saveUser(data)
      navigate('/feed')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    }
  }

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const toggleAvailability = (v) => {
    setSelectedAvailability(prev =>
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
        <div className="auth-role-badge worker">👷 Worker Account</div>
        <h2>Create Worker Account</h2>
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
              <input placeholder="Full Name" value={form.name} onChange={set('name')} required />
              <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required />
              <input type="password" placeholder="Password" value={form.password} onChange={set('password')} required />
              <input placeholder="Location (e.g. San Francisco, CA)" value={form.location} onChange={set('location')} />
              <input placeholder="Profession (e.g. Bartender, Forklift Operator)" value={form.profession} onChange={set('profession')} />
              <button type="button" onClick={() => setStep(2)}>Next →</button>
            </>
          )}

          {step === 2 && (
            <>
              <div className="form-section-label">Your Experience</div>
              <input
                placeholder="Skills (e.g. Customer service, Forklift, POS systems)"
                value={form.skills}
                onChange={set('skills')}
              />
              <input
                type="number"
                placeholder="Years of experience"
                value={form.experience_years}
                onChange={set('experience_years')}
                min="0"
                max="50"
              />
              <textarea
                placeholder="Tell businesses about yourself — your work style, strengths, what you're looking for..."
                value={form.bio}
                onChange={set('bio')}
                rows={4}
              />

              <div className="form-section-label">Availability <span className="form-hint">Select all that apply</span></div>
              <div className="vibe-tags">
                {AVAILABILITY_OPTIONS.map(v => (
                  <button
                    key={v}
                    type="button"
                    className={`vibe-tag ${selectedAvailability.includes(v) ? 'vibe-tag--active' : ''}`}
                    onClick={() => toggleAvailability(v)}
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