<template>
  <div class="container mt-4">
    <h3>Doctor Dashboard</h3>

    <div v-if="loading">Loading dashboard...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Upcoming Appointments -->
    <div class="mt-4">
      <h5>Upcoming Appointments</h5>

      <table
        v-if="appointments.length"
        class="table table-bordered mt-2"
      >
        <thead>
          <tr>
            <th>Patient</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td>{{ a.patient_name }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td>
              <span class="badge bg-warning">
                {{ a.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="text-muted">
        No upcoming appointments
      </div>
    </div>

    <!-- Assigned Patients -->
    <div class="mt-5">
      <h5>Assigned Patients</h5>

      <table
        v-if="patients.length"
        class="table table-striped mt-2"
      >
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in patients" :key="p.id">
            <td>{{ p.name }}</td>
            <td>{{ p.email }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="text-muted">
        No patients assigned yet
      </div>
    </div>
  </div>
</template>

<script>
import { getDoctorDashboard } from '../services/api'

export default {
  data() {
    return {
      loading: false,
      error: '',
      appointments: [],
      patients: []
    }
  },
  async mounted() {
    this.loading = true
    try {
      const res = await getDoctorDashboard()
      this.appointments = res.upcoming_appointments || []
      this.patients = res.assigned_patients || []
    } catch (err) {
      this.error = err.message || 'Failed to load dashboard'
    } finally {
      this.loading = false
    }
  }
}
</script>