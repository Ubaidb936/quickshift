import { Link } from 'react-router-dom'
import { getUser, logout, isAuthenticated } from '../services/auth'

export default function Navbar() {
  const { role, name } = getUser()
  const authenticated = isAuthenticated()

  return (
    <nav className="navbar">
      <Link to="/" className="brand">Instawork</Link>
      <div className="nav-links">
        {authenticated ? (
          <>
            <span className="greeting">Hi, {name}</span>
            {role === 'business' ? (
              <>
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/shifts/create">Post Shift</Link>
              </>
            ) : (
              <>
                <Link to="/feed">Browse Shifts</Link>
                <Link to="/my-matches">My Applications</Link>
              </>
            )}
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  )
}
