import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, getRoles } from '../services/auth'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import PatientAppointments from '../views/PatientAppointments.vue'
import PatientMyAppointments from '../views/PatientMyAppointments.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/', component: HomeView },
  { path: '/admin', component: AdminDashboard, meta: {requiresAuth: true, roles: ['admin']}},
  { path: '/doctor', component: DoctorDashboard, meta: {requiresAuth: true, roles: ['doctor']}},
  { path: '/patient', component: PatientDashboard, meta: {requiresAuth: true, roles: ['patient']}},
  { path: '/patient/appointments', component: PatientAppointments, meta: {requiresAuth: true, roles: ['patient']}},
  { path: '/patient/my-appointments', component: PatientMyAppointments, meta: {requiresAuth: true, roles: ['patient']}}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
    return
  }

  if (to.meta.roles) {
    const userRoles = getRoles()
    const allowed = to.meta.roles.some(role => userRoles.includes(role))
    if (!allowed) {
      next('/login')
      return
    }
  }

  next()
})

export default router
