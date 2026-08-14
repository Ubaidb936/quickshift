import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="landing">

      <div className="hero">
        <div className="hero-badge">Now hiring across 50+ cities</div>
        <h1>Fill shifts.<br />Get hired.<br /><span>Instantly.</span></h1>
        <p>QuickShift connects businesses with reliable workers — in minutes, not days.</p>
        <div className="hero-actions">
          <button className="btn-primary btn-lg" onClick={() => navigate('/register/business')}>
            Hire Workers
          </button>
          <button className="btn-outline btn-lg" onClick={() => navigate('/register/worker')}>
            Find Shifts
          </button>
        </div>
      </div>

      <div className="landing-stats">
        <div className="stat"><strong>10k+</strong><span>Shifts filled</span></div>
        <div className="stat"><strong>3 min</strong><span>Avg time to match</span></div>
        <div className="stat"><strong>500+</strong><span>Businesses</span></div>
      </div>

      <div className="landing-cards">
        <div className="landing-card" onClick={() => navigate('/register/business')}>
          <div className="landing-icon">🏢</div>
          <h2>For Businesses</h2>
          <p>Post a shift in 60 seconds. Get matched with reliable workers who show up.</p>
          <ul>
            <li>✓ Post shifts instantly</li>
            <li>✓ Review applicants</li>
            <li>✓ Accept or decline with one click</li>
          </ul>
          <button className="btn-primary">Get Started →</button>
        </div>
        <div className="landing-card" onClick={() => navigate('/register/worker')}>
          <div className="landing-icon">👷</div>
          <h2>For Workers</h2>
          <p>Browse local shifts that match your skills. Work when you want.</p>
          <ul>
            <li>✓ Browse available shifts</li>
            <li>✓ Set your availability</li>
            <li>✓ Get hired fast</li>
          </ul>
          <button className="btn-primary">Find Shifts →</button>
        </div>
      </div>

      <p className="landing-login">
        Already have an account?{' '}
        <span onClick={() => navigate('/login')}>Sign in</span>
      </p>

    </div>
  )
}
