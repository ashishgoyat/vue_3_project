const API_BASE = 'http://localhost:5000'

// -------------------- TOKEN HELPERS --------------------

function getToken() {
  return localStorage.getItem('auth-token')
}

async function request(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json'
  }

  const token = getToken()
  if (token) {
    headers['Authentication-Token'] = token
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers
  })

  // Handle non-JSON (like HTML error pages)
  const contentType = response.headers.get('content-type')
  let data = null

  if (contentType && contentType.includes('application/json')) {
    data = await response.json()
  }

  if (!response.ok) {
    throw data || { message: 'API Error' }
  }

  return data
}

// -------------------- AUTH --------------------

export function login(payload) {
  return request('/api/login', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function register(payload) {
  return request('/api/register', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function logout() {
  localStorage.removeItem('auth-token')
  localStorage.removeItem('roles')
}

// -------------------- COMMON --------------------

export function getHome() {
  return request('/api/home')
}

// -------------------- PATIENT --------------------

export function getDoctors() {
  return request('/api/doctors')
}

export function getDoctorAvailability(doctorId) {
  return request(`/api/doctor_availability/${doctorId}`)
}

export function bookAppointment(payload) {
  return request('/api/appointments', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function getMyAppointments() {
  return request('/api/appointments')
}

export function getPatientDashboard() {
  return request('/api/patient_dashboard')
}

// -------------------- DOCTOR --------------------

export function getDoctorDashboard() {
  return request('/api/doctor_dashboard')
}

export function getTreatments() {
  return request('/api/treatments')
}

// -------------------- ADMIN --------------------

export function getAdminDashboard() {
  return request('/api/admin')
}

export function toggleUserActive(userId) {
  return request(`/api/toggle_user_active/${userId}`, {
    method: 'PUT'
  })
}