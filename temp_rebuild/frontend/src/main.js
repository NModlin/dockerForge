import { createApp } from 'vue';
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import axios from 'axios';

import App from './App.vue';
import routes from './router';
import storeConfig from './store';

// Configure axios
axios.defaults.baseURL = window.location.origin; // Use the same origin as the frontend
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

// Create Vuetify instance
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#007BFF',
          secondary: '#6C757D',
          accent: '#17A2B8',
          error: '#DC3545',
          warning: '#FFC107',
          info: '#17A2B8',
          success: '#28A745',
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#0D6EFD',
          secondary: '#6C757D',
          accent: '#0DCAF0',
          error: '#DC3545',
          warning: '#FFC107',
          info: '#0DCAF0',
          success: '#198754',
        },
      },
    },
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

app.mount('#app');
