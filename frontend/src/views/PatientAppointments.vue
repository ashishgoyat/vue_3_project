<template>
  <div class="container mt-4">
    <h3>Book Appointment</h3>

    <div v-if="loading">Loading doctors...</div>
    <div v-if="error" class="text-danger">{{ error }}</div>

    <!-- Doctors -->
    <div class="row">
      <div
        class="col-md-4 mb-3"
        v-for="doctor in doctors"
        :key="doctor.id"
      >
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ doctor.name }}</h5>
            <p class="card-text">
              <strong>Specialization:</strong> {{ doctor.specialization }}<br />
              <strong>Experience:</strong> {{ doctor.years_of_experience }} years
            </p>

            <button
              class="btn btn-primary btn-sm"
              @click="selectDoctor(doctor)"
            >
              Book Appointment
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Doctor -->
    <div v-if="selectedDoctor" class="mt-4">
      <h4>Selected Doctor: {{ selectedDoctor.name }}</h4>
      <p>{{ selectedDoctor.specialization }}</p>

      <button
        class="btn btn-secondary"
        @click="resetSelection"
      >
        Cancel
      </button>
    </div>

    <!-- Availability -->
    <div v-if="availability.length" class="mt-4">
      <h5>Available Slots</h5>

      <div
        v-for="slot in availability"
        :key="slot.id"
        class="border p-2 mb-2"
      >
        <strong>{{ slot.day_of_week }}</strong><br />
        {{ slot.start_time }} - {{ slot.end_time }}

        <button
          class="btn btn-sm btn-outline-primary float-end"
          @click="selectSlot(slot)"
        >
          Select
        </button>
      </div>
    </div>

    <!-- Selected Slot -->
    <div v-if="selectedSlot" class="alert alert-success mt-3">
      <strong>Selected Slot:</strong>
      {{ selectedSlot.day_of_week }}
      ({{ selectedSlot.start_time }} - {{ selectedSlot.end_time }})
    </div>

    <!-- Auto-selected Date -->
    <div v-if="appointmentDate" class="alert alert-info mt-2">
      Appointment Date: <strong>{{ appointmentDate }}</strong>
    </div>

    <!-- Confirm -->
    <button
      v-if="selectedSlot && appointmentDate"
      class="btn btn-success mt-3"
      @click="confirmBooking"
    >
      Confirm Appointment
    </button>

    <div v-if="success" class="alert alert-success mt-3">
      {{ success }}
    </div>

    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>


<script>
import {
  getDoctors,
  getDoctorAvailability,
  bookAppointment
} from '../services/api'

export default {
  data() {
    return {
      doctors: [],
      selectedDoctor: null,
      availability: [],
      selectedSlot: null,
      appointmentDate: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  async mounted() {
    const res = await getDoctors()
    this.doctors = res.doctor || []
  },
  methods: {
    async selectDoctor(doctor) {
      this.selectedDoctor = doctor
      this.selectedSlot = null
      this.appointmentDate = ''
      this.success = ''
      this.error = ''

      const res = await getDoctorAvailability(doctor.id)
      this.availability = res.availability || []
    },
    selectSlot(slot) {
    this.selectedSlot = slot
    this.appointmentDate = this.getNextDateForDay(slot.day_of_week)
    },
    async confirmBooking() {
      try {
        await bookAppointment({
          doctor_id: this.selectedDoctor.id,
          appointment_date: this.appointmentDate,
          appointment_time: this.selectedSlot.start_time
        })
        this.success = 'Appointment booked successfully'
      } catch (err) {
        this.error = err.message || 'Booking failed'
      }
    },
    getNextDateForDay(dayName) {
    const days = [
        'sunday',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday'
    ]

    const today = new Date()
    const todayDay = today.getDay()
    const targetDay = days.indexOf(dayName.toLowerCase())

    let diff = targetDay - todayDay
    if (diff < 0) diff += 7
    if (diff === 0) diff = 7 // always next occurrence

    const result = new Date(today)
    result.setDate(today.getDate() + diff)

    return result.toISOString().split('T')[0] // YYYY-MM-DD
    },
    resetSelection() {
        this.selectedDoctor = null
        this.availability = []
        this.selectedSlot = null
        this.appointmentDate = ''
        this.success = ''
        this.error = ''
    }
  }
}
</script>