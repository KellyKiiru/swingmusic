import { createApp } from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import { createPinia } from 'pinia'


import "../src/assets/css/global.scss";

const app = createApp(App);
app.use(createPinia())
app.use(router);
app.mount('#app');