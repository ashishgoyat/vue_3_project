export function isAuthenticated() {
  return !!localStorage.getItem('auth-token')
}

export function getRoles() {
  const roles = localStorage.getItem('roles')
  return roles ? JSON.parse(roles) : []
}

export function logout() {
  localStorage.removeItem('auth-token')
  localStorage.removeItem('roles')
  localStorage.removeItem('user-id')
}