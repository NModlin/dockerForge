// Vuex store configuration for DockerForge Web UI

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
      } else {
        localStorage.removeItem('token');
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
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token);
      commit('SET_USER', user);
    },
    logout({ commit }) {
      commit('SET_TOKEN', null);
      commit('SET_USER', null);
    },
  },
  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    user: (state) => state.user,
    token: (state) => state.token,
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

// Import the images module
import images from './store/modules/images';

// Main store configuration
export default {
  modules: {
    auth,
    containers,
    images,
    // Additional modules will be added in Phase 2
  },
  state: {
    appName: 'DockerForge',
    version: '0.1.0',
    loading: false,
    error: null,
    darkMode: localStorage.getItem('darkMode') === 'true',
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
