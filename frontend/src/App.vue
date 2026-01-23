<template>
  <div>
    <!-- Top Navigation -->
    <Navbar />

    <!-- Page Content -->
    <main class="container mt-4">
      <router-view />
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  }
}
</script>

<style>
/* Optional global styles */
body {
  background-color: #f8f9fa;
}
</style>