import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="landing">

      {/* Hero */}
      <div className="hero">
        <div className="hero-glow" />
        <div className="hero-glow hero-glow--2" />
        <div className="hero-content">
          <div className="hero-badge">AI-Powered Staffing</div>
          <h1>The smartest way<br />to <span>fill shifts.</span></h1>
          <p>QuickShift uses AI to match businesses with the right workers — not just by role, but by environment, vibe, and fit.</p>
          <div className="hero-actions">
            <button className="btn-primary btn-lg" onClick={() => navigate('/register/business')}>
              Hire Workers
            </button>
            <button className="btn-outline btn-lg" onClick={() => navigate('/register/worker')}>
              Find Shifts
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="landing-stats">
        <div className="stat"><strong>10k+</strong><span>Shifts filled</span></div>
        <div className="stat"><strong>3 min</strong><span>Avg time to match</span></div>
        <div className="stat"><strong>500+</strong><span>Businesses</span></div>
        <div className="stat"><strong>98%</strong><span>Fill rate</span></div>
      </div>

      {/* AI Feature */}
      <div className="ai-section">
        <div className="ai-section-inner">
          <div className="ai-tag">New</div>
          <h2>Meet your AI staffing agent</h2>
          <p>Just describe what you need. The agent finds workers that match your environment, not just your job title.</p>
          <div className="ai-chat-preview">
            <div className="chat-bubble chat-bubble--user">
              I need a relaxed, experienced barista for quiet morning shifts. Small team vibes.
            </div>
            <div className="chat-bubble chat-bubble--agent">
              Found 8 workers near you that match. Top match: Sarah K. — 4 years experience, prefers mornings, loves small teams.
            </div>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="how-it-works">
        <h2>How it works</h2>
        <div className="steps">
          <div className="step">
            <div className="step-number">01</div>
            <h3>Register your business</h3>
            <p>Tell us about your environment, industry, and team culture.</p>
          </div>
          <div className="step-divider" />
          <div className="step">
            <div className="step-number">02</div>
            <h3>Chat with the agent</h3>
            <p>Describe the worker you need. The AI searches by vibe, not just keywords.</p>
          </div>
          <div className="step-divider" />
          <div className="step">
            <div className="step-number">03</div>
            <h3>Hire in minutes</h3>
            <p>Review matched workers, accept with one click, shift is filled.</p>
          </div>
        </div>
      </div>

      {/* Cards */}
      <div className="landing-cards">
        <div className="landing-card" onClick={() => navigate('/register/business')}>
          <div className="landing-card-accent" />
          <div className="landing-icon">🏢</div>
          <h2>For Businesses</h2>
          <p>Post a shift in 60 seconds. Let the AI find workers that actually fit your environment.</p>
          <ul>
            <li>✓ AI-powered worker matching</li>
            <li>✓ Chat with your staffing agent</li>
            <li>✓ Accept or decline with one click</li>
          </ul>
          <button className="btn-primary">Get Started →</button>
        </div>
        <div className="landing-card" onClick={() => navigate('/register/worker')}>
          <div className="landing-card-accent landing-card-accent--green" />
          <div className="landing-icon">👷</div>
          <h2>For Workers</h2>
          <p>Browse shifts that match who you are — not just what you do.</p>
          <ul>
            <li>✓ Matched by environment fit</li>
            <li>✓ Set your availability once</li>
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