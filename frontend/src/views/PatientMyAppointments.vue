<template>
  <div class="container mt-4">
    <h3>My Appointments</h3>

    <div v-if="loading">Loading...</div>

    <div v-if="error" class="text-danger">{{ error }}</div>

    <table v-if="appointments.length" class="table table-bordered mt-3">
      <thead>
        <tr>
          <th>Doctor</th>
          <th>Date</th>
          <th>Time</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="a in appointments" :key="a.id">
          <td>{{ a.doctor }}</td>
          <td>{{ a.appointment_date }}</td>
          <td>{{ a.appointment_time }}</td>
          <td>{{ a.status }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading">
      No appointments found.
    </div>
  </div>
</template>

<script>
import { getMyAppointments } from '../services/api'

export default {
  data() {
    return {
      appointments: [],
      loading: false,
      error: ''
    }
  },
  async mounted() {
    this.loading = true
    try {
      const res = await getMyAppointments()
      this.appointments = res.appointments || []
    } catch (err) {
      this.error = err.message || 'Failed to load appointments'
    } finally {
      this.loading = false
    }
  }
}
</script>