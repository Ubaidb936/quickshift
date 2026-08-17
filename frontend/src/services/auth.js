import api from './api'

export const registerBusiness = (data) => api.post('/auth/register/business', data)
export const registerWorker = (data) => api.post('/auth/register/worker', data)
export const login = (email, password, role) => api.post('/auth/login', { email, password, role })

export const logout = async () => {
  try { await api.post('/auth/logout') } catch (_) {}
  localStorage.clear()
  window.location.href = '/'
}

export const saveUser = ({ access_token, role, user_id, name }) => {
  localStorage.setItem('token', access_token)
  localStorage.setItem('role', role)
  localStorage.setItem('userId', user_id)
  localStorage.setItem('name', name)
}

export const getUser = () => ({
  token: localStorage.getItem('token'),
  role: localStorage.getItem('role'),
  userId: localStorage.getItem('userId'),
  name: localStorage.getItem('name'),
})

export const isAuthenticated = () => !!localStorage.getItem('token')
