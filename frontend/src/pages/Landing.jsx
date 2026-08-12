import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="landing">
      <h1>Welcome to Instawork</h1>
      <p>Are you a business looking for workers, or a worker looking for shifts?</p>
      <div className="landing-cards">
        <div className="landing-card" onClick={() => navigate('/register/business')}>
          <div className="landing-icon">🏢</div>
          <h2>I'm a Business</h2>
          <p>Post shifts and find reliable workers fast</p>
          <button className="btn-primary">Register as Business</button>
        </div>
        <div className="landing-card" onClick={() => navigate('/register/worker')}>
          <div className="landing-icon">👷</div>
          <h2>I'm a Worker</h2>
          <p>Browse shifts and get hired by top businesses</p>
          <button className="btn-primary">Register as Worker</button>
        </div>
      </div>
      <p className="landing-login">Already have an account? <span onClick={() => navigate('/login')}>Login</span></p>
    </div>
  )
}
