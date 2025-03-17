import { createApp } from 'vue';
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';

import App from './App.vue';
import routes from './router';
import storeConfig from './store';

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

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Create store
const store = createStore(storeConfig);

// Create and mount app
const app = createApp(App);

app.use(router);
app.use(store);
app.use(vuetify);

app.mount('#app');
