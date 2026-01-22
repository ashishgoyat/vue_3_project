<template>
  <div class="container mt-5" style="max-width: 400px">
    <h3 class="mb-3">Login</h3>

    <div class="mb-3">
      <input
        v-model="email"
        type="email"
        class="form-control"
        placeholder="Email"
      />
    </div>

    <div class="mb-3">
      <input
        v-model="password"
        type="password"
        class="form-control"
        placeholder="Password"
      />
    </div>

    <button class="btn btn-primary w-100" @click="handleLogin">
      Login
    </button>

    <p v-if="error" class="text-danger mt-3">{{ error }}</p>
  </div>
</template>

<script>
import { login } from '../services/api'

export default {
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      try {
        const res = await login({
          email: this.email,
          password: this.password
        })

        // 🔐 STORE TOKEN
        localStorage.setItem('auth-token', res['auth-token'])
        localStorage.setItem('roles', JSON.stringify(res.roles))
        localStorage.setItem('user-id', res.id)

        // 🔁 REDIRECT BY ROLE
        if (res.roles.includes('admin')) {
          this.$router.push('/admin')
        } else if (res.roles.includes('doctor')) {
          this.$router.push('/doctor')
        } else {
          this.$router.push('/patient')
        }

      } catch (err) {
        this.error = err.message || 'Login failed'
      }
    }
  }
}
</script>