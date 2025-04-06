import { createApp } from 'vue';
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import './themes/theme.css';
import axios from 'axios';

import App from './App.vue';
import routes from './router.js';
import storeConfig from './store.js';
import i18n from './i18n';
import { themes, applyTheme } from './themes';

// Configure axios
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || '/api';
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

// Initialize auth token from localStorage if it exists
const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Get saved theme or default to light
const savedTheme = localStorage.getItem('theme') || 'light';

// Create Vuetify instance
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: savedTheme,
    themes,
  },
});

// Create store
const store = createStore(storeConfig);

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Add request interceptor to handle errors
axios.interceptors.response.use(
  response => response,
  error => {
    // Handle session expiration
    if (error.response && error.response.status === 401) {
      store.dispatch('auth/logout');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

// Create and mount app
const app = createApp(App);

app.use(router);
app.use(store);
app.use(vuetify);
app.use(i18n);

// Apply theme
applyTheme(savedTheme, vuetify);

// Listen for system theme changes if using system theme
if (savedTheme === 'system') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    applyTheme('system', vuetify);
  });
}

app.mount('#app');
