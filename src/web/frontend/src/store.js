// Vuex store configuration for DockerForge Web UI

// Import axios for API calls
import axios from 'axios';

// Define store modules
const auth = {
  namespaced: true,
  state: {
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    isAuthenticated: !!localStorage.getItem('token'),
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
      state.isAuthenticated = !!token;
      if (token) {
        localStorage.setItem('token', token);
        // Set the token in axios default headers for all future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        localStorage.removeItem('token');
        // Remove the token from axios default headers
        delete axios.defaults.headers.common['Authorization'];
      }
    },
    SET_USER(state, user) {
      state.user = user;
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        localStorage.removeItem('user');
      }
    },
    SET_PASSWORD_CHANGED(state) {
      if (state.user) {
        state.user.password_change_required = false;
        localStorage.setItem('user', JSON.stringify(state.user));
      }
    },
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token);
      commit('SET_USER', user);
    },
    async logout({ commit }) {
      try {
        // Call the logout API endpoint
        await axios.post('/api/auth/logout');
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        // Clear token and user data regardless of API call success
        commit('SET_TOKEN', null);
        commit('SET_USER', null);
      }
    },
    // Initialize auth state from localStorage
    init({ commit }) {
      const token = localStorage.getItem('token');
      if (token) {
        commit('SET_TOKEN', token);
        // Set the token in axios default headers
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      const user = localStorage.getItem('user');
      if (user) {
        commit('SET_USER', JSON.parse(user));
      }
    },
  },
  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    user: (state) => state.user,
    token: (state) => state.token,
    passwordChangeRequired: (state) => state.user?.password_change_required || false,
  },
};

const containers = {
  namespaced: true,
  state: {
    containers: [],
    loading: false,
    error: null,
    currentContainer: null,
  },
  mutations: {
    SET_CONTAINERS(state, containers) {
      state.containers = containers;
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_CURRENT_CONTAINER(state, container) {
      state.currentContainer = container;
    },
  },
  actions: {
    // Container actions will be implemented in Phase 2
  },
  getters: {
    allContainers: (state) => state.containers,
    runningContainers: (state) => state.containers.filter((c) => c.state === 'running'),
    currentContainer: (state) => state.currentContainer,
  },
};

// Import modules
import images from './store/modules/images';
import chat from './store/modules/chat';
import help from './store/modules/help';

// Main store configuration
export default {
  modules: {
    auth,
    containers,
    images,
    chat,
    help,
  },
  state: {
    appName: 'DockerForge',
    version: '0.1.0',
    loading: false,
    error: null,
    darkMode: localStorage.getItem('darkMode') !== 'false',
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_DARK_MODE(state, darkMode) {
      state.darkMode = darkMode;
      localStorage.setItem('darkMode', darkMode);
    },
  },
  actions: {
    toggleDarkMode({ commit, state }) {
      commit('SET_DARK_MODE', !state.darkMode);
    },
  },
  getters: {
    appName: (state) => state.appName,
    version: (state) => state.version,
    isLoading: (state) => state.loading,
    error: (state) => state.error,
    darkMode: (state) => state.darkMode,
  },
};
