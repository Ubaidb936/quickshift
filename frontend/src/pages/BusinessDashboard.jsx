import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import Spinner from '../components/Spinner'
import Toast from '../components/Toast'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'

const AGENT_URL = 'http://localhost:8000/agent/chat'

export default function BusinessDashboard() {
  const [shifts, setShifts] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState({ message: '', type: 'success' })
  const [confirmDelete, setConfirmDelete] = useState(null)

  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I can help you find workers. Tell me what you need — role, location, availability, anything.' }
  ])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef(null)

  const navigate = useNavigate()

  useEffect(() => {
    api.get('/shifts/my-shifts')
      .then(({ data }) => setShifts(data))
      .finally(() => setLoading(false))
  }, [])

  // scroll to bottom every time messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || streaming) return

    const userText = input.trim()
    // snapshot history BEFORE adding new messages — this is what the backend needs
    const historySnapshot = [...messages]
    setInput('')

    // add user bubble immediately
    setMessages(prev => [...prev, { role: 'user', content: userText }])
    // add empty assistant bubble that we'll fill as chunks arrive
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])
    setStreaming(true)

    try {
      const token = localStorage.getItem('token')
      const res = await fetch(AGENT_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userText, history: historySnapshot })
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        // \0 is the end-of-stream sentinel sent by the backend
        if (chunk.includes('\0')) break
        // append each chunk to the last (assistant) bubble
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + chunk
          }
          return updated
        })
      }
    } catch {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: 'Something went wrong. Please try again.' }
        return updated
      })
    } finally {
      setStreaming(false)
      // refresh shifts in case the agent just posted one
      api.get('/shifts/my-shifts').then(({ data }) => setShifts(data)).catch(() => {})
    }
  }

  const deleteShift = async (id) => {
    await api.delete(`/shifts/${id}`)
    setShifts(shifts.filter(s => s.id !== id))
    setConfirmDelete(null)
    setToast({ message: 'Shift deleted', type: 'success' })
  }

  if (loading) return <div className="container"><Spinner text="Loading your shifts..." /></div>

  return (
    <div className="container">
      {confirmDelete && (
        <ConfirmDialog
          message="Are you sure you want to delete this shift? This cannot be undone."
          onConfirm={() => deleteShift(confirmDelete)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '' })} />

      <div className="dashboard-layout">

        {/* ── left: shifts ── */}
        <div className="dashboard-main">
          <div className="dashboard-header">
            <div>
              <h2 className="page-title">My Shifts</h2>
              <p className="page-subtitle">{shifts.length} shift{shifts.length !== 1 ? 's' : ''} posted</p>
            </div>
            <Link to="/shifts/create" className="btn-primary">+ Post Shift</Link>
          </div>

          {shifts.length === 0
            ? <EmptyState icon="📬" title="No shifts yet" description="Post your first shift to start finding workers." action="Post a Shift" onAction={() => navigate('/shifts/create')} />
            : shifts.map(shift => (
                <div key={shift.id} className={`shift-card status-${shift.status}`}>
                  <div className="shift-header">
                    <h3>{shift.position}</h3>
                    <span className="pay">${shift.pay_rate}/hr</span>
                  </div>
                  <p>{shift.num_workers} worker{shift.num_workers > 1 ? 's' : ''} needed</p>
                  <p style={{ marginTop: '0.35rem' }}>
                    Status: <span className={`status-badge status-${shift.status}`}>{shift.status}</span>
                  </p>
                  {shift.duties && <p style={{ marginTop: '0.35rem' }}><strong>Duties:</strong> {shift.duties}</p>}
                  <div className="actions">
                    <button onClick={() => navigate(`/shifts/${shift.id}/applicants`)}>View Applicants</button>
                  </div>
                </div>
              ))
          }
        </div>

        {/* ── right: AI chat ── */}
        <div className="dashboard-chat">
          <div className="chat-header">
            <span className="chat-header__icon">✦</span>
            <span>AI Staffing Assistant</span>
          </div>

          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble chat-bubble--${m.role}`}>
                {m.content || <span className="chat-typing"><span/><span/><span/></span>}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-row">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Find me a bartender in SF this weekend..."
              disabled={streaming}
            />
            <button onClick={sendMessage} disabled={streaming}>
              {streaming ? '...' : '↑'}
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}