import { createRouter, createWebHistory } from 'vue-router'

// Views
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import PatientAppointments from '../views/PatientAppointments.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import AdminView from '../views/AdminDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

// Helpers
function isAuthenticated() {
  return !!localStorage.getItem('auth-token')
}

function getUserRoles() {
  const roles = localStorage.getItem('roles')
  return roles ? JSON.parse(roles) : []
}

const routes = [
  // Public
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },

  // Patient
  {
    path: '/patient',
    component: PatientDashboard,
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/appointments',
    component: PatientAppointments,
    meta: { requiresAuth: true, roles: ['patient'] }
  },

  // Doctor
  {
    path: '/doctor',
    component: DoctorDashboard,
    meta: { requiresAuth: true, roles: ['doctor'] }
  },

  // Admin
  {
    path: '/admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['admin'] }
  },

  // Fallback
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/* ------------------ ROUTE GUARD ------------------ */

router.beforeEach((to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next()
  }

  if (!isAuthenticated()) {
    return next('/login')
  }

  if (to.meta.roles) {
    const userRoles = getUserRoles()
    const allowed = to.meta.roles.some(role =>
      userRoles.includes(role)
    )

    if (!allowed) {
      return next('/')
    }
  }

  next()
})

export default router