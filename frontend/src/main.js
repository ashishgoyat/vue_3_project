import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css'

// Create and mount app
createApp(App)
  .use(router)
  .mount('#app')
