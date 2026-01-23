// -------------------- TOKEN --------------------

export function getToken() {
  return localStorage.getItem('auth-token')
}

export function isAuthenticated() {
  return !!localStorage.getItem('auth-token')
}

// -------------------- ROLES --------------------

export function getRoles() {
  const roles = localStorage.getItem('roles')
  return roles ? JSON.parse(roles) : []
}

export function hasRole(role) {
  return getRoles().includes(role)
}

// -------------------- LOGIN / LOGOUT --------------------

export function saveAuth(authToken, roles) {
  localStorage.setItem('auth-token', authToken)
  localStorage.setItem('roles', JSON.stringify(roles))
}

export function logout() {
  localStorage.removeItem('auth-token')
  localStorage.removeItem('roles')
}

// -------------------- REDIRECT HELPERS --------------------

export function getDefaultRouteByRole() {
  const roles = getRoles()

  if (roles.includes('admin')) return '/admin'
  if (roles.includes('doctor')) return '/doctor'
  if (roles.includes('patient')) return '/patient'

  return '/login'
}