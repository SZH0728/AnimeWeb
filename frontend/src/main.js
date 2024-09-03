import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

const app = createApp(App)

app.use(router)
app.config.globalProperties.$BASE_API_URL = 'http://sunnyrain.top:60000'

app.mount('#app')
