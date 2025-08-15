import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";


import App from './App.vue'
import router from './router'

const app = createApp(App)

const options = {
  position: "top-right",
  timeout: 2000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  draggable: true,
  draggablePercent: 60,
  showCloseButtonOnHover: true,
  closeButton: "button",
  icon: true,
  rtl: false,
};

app.use(Toast, options);
app.use(createPinia())
app.use(router)

app.mount('#app')
