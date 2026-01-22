<template>
  <div class="container mt-5">
    <h2>Admin Dashboard</h2>
    <button class="btn btn-danger mt-3" @click="doLogout">Logout</button>
  </div>
</template>

<script>
import { logout } from '../services/auth'

export default {
  methods: {
    doLogout() {
      logout()
      this.$router.push('/login')
    }
  }
}
</script>