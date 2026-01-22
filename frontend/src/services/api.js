const API_BASE = ''

function getToken() {
  return localStorage.getItem('auth-token')
}

async function request(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(getToken() && { 'Authentication-Token': getToken() })
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    const error = await response.json()
    throw error
  }

  return response.json()
}

/* ---------- AUTH ---------- */

export function login(data) {
  return request('/api/login', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export function register(data) {
  return request('/api/register', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/* ---------- DASHBOARDS ---------- */

export function getHome() {
  return request('/api/home')
}

export function getAdminDashboard() {
  return request('/api/admin')
}

export function getDoctorDashboard() {
  return request('/api/doctor_dashboard')
}

export function getPatientDashboard() {
  return request('/api/patient_dashboard')
}

/* ---------- APPOINTMENTS ---------- */

export function getAppointments() {
  return request('/appointments')
}

export function createAppointment(data) {
  return request('/appointments', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}


/* ---------- DOCTORS ---------- */

export function getDoctors() {
  return request('/doctors')
}


/* ---------- DOCTOR AVAILABILITY ---------- */

export function getDoctorAvailability(doctorId) {
  return request(`/doctor_availability/${doctorId}`)
}


/* ---------- APPOINTMENTS ---------- */

export function getMyAppointments() {
  return request('/appointments')
}


/* ---------- BOOK APPOINTMENT ---------- */

export function bookAppointment(data) {
  return request('/appointments', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}