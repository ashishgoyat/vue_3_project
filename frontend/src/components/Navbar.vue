<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">Hospital</router-link>

      <div class="navbar-nav">
        <router-link v-if="hasRole('patient')" class="nav-link" to="/patient">
          Patient
        </router-link>

        <router-link v-if="hasRole('doctor')" class="nav-link" to="/doctor">
          Doctor
        </router-link>

        <router-link v-if="hasRole('admin')" class="nav-link" to="/admin">
          Admin
        </router-link>

        <a v-if="isAuthenticated" class="nav-link" href="#" @click.prevent="doLogout">
          Logout
        </a>

        <router-link v-else class="nav-link" to="/login">
          Login
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script>
import { isAuthenticated, hasRole, logout } from '../services/auth'

export default {
  computed: {
    isAuthenticated() {
      return isAuthenticated()
    }
  },
  methods: {
    hasRole,
    doLogout() {
      logout()
      this.$router.push('/login')
    }
  }
}
</script>