import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { isAuthenticated, getUser } from './services/auth'
import Landing from './pages/Landing'
import Login from './pages/Login'
import RegisterBusiness from './pages/RegisterBusiness'
import RegisterWorker from './pages/RegisterWorker'
import BusinessDashboard from './pages/BusinessDashboard'
import WorkerFeed from './pages/WorkerFeed'
import PostShift from './pages/PostShift'
import ShiftApplicants from './pages/ShiftApplicants'
import MyMatches from './pages/MyMatches'
import Navbar from './components/Navbar'

function ProtectedRoute({ children, role }) {
  if (!isAuthenticated()) return <Navigate to="/" replace />
  if (role && getUser().role !== role) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={
          isAuthenticated()
            ? <Navigate to={getUser().role === 'business' ? '/dashboard' : '/feed'} replace />
            : <Landing />
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/register/business" element={<RegisterBusiness />} />
        <Route path="/register/worker" element={<RegisterWorker />} />

        <Route path="/dashboard" element={
          <ProtectedRoute role="business"><BusinessDashboard /></ProtectedRoute>
        } />
        <Route path="/shifts/create" element={
          <ProtectedRoute role="business"><PostShift /></ProtectedRoute>
        } />
        <Route path="/shifts/:shiftId/applicants" element={
          <ProtectedRoute role="business"><ShiftApplicants /></ProtectedRoute>
        } />

        <Route path="/feed" element={
          <ProtectedRoute role="worker"><WorkerFeed /></ProtectedRoute>
        } />
        <Route path="/my-matches" element={
          <ProtectedRoute role="worker"><MyMatches /></ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
