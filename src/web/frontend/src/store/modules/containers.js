/**
 * Vuex store module for Docker containers
 */
import axios from 'axios';

// Initial state
const state = {
  containers: [],
  currentContainer: null,
  loading: false,
  error: null,
};

// Getters
const getters = {
  getContainerById: (state) => (id) => {
    return state.containers.find(container => container.id === id);
  },
  getContainerByName: (state) => (name) => {
    return state.containers.find(container => container.name === name);
  },
  runningContainers: (state) => {
    return state.containers.filter(container => container.status === 'running');
  },
  stoppedContainers: (state) => {
    return state.containers.filter(container => container.status === 'stopped');
  },
};

// Actions
const actions = {
  /**
   * Fetch all containers
   */
  async getContainers({ commit }, filters = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/containers', { params: filters });
      commit('SET_CONTAINERS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Fetch a single container by ID
   */
  async getContainer({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/containers/${id}`);
      commit('SET_CURRENT_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Create a new container
   */
  async createContainer({ commit }, containerData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/containers', containerData);
      commit('ADD_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Update a container
   */
  async updateContainer({ commit }, { id, containerData }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/api/containers/${id}`, containerData);
      commit('UPDATE_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Delete a container
   */
  async removeContainer({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/containers/${id}`);
      commit('REMOVE_CONTAINER', id);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Start a container
   */
  async startContainer({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/containers/${id}/start`);
      commit('UPDATE_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Stop a container
   */
  async stopContainer({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/containers/${id}/stop`);
      commit('UPDATE_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Restart a container
   */
  async restartContainer({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/containers/${id}/restart`);
      commit('UPDATE_CONTAINER', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get container logs
   */
  async getContainerLogs({ commit }, { id, tail = 100 }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/containers/${id}/logs`, {
        params: { tail }
      });
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get Docker system info
   */
  async getSystemInfo({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/containers/system/info');
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Clear current container
   */
  clearCurrentContainer({ commit }) {
    commit('SET_CURRENT_CONTAINER', null);
  },

  /**
   * Clear error
   */
  clearError({ commit }) {
    commit('SET_ERROR', null);
  },
};

// Mutations
const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_CONTAINERS(state, containers) {
    state.containers = containers;
  },
  SET_CURRENT_CONTAINER(state, container) {
    state.currentContainer = container;
  },
  ADD_CONTAINER(state, container) {
    // Check if the container already exists
    const index = state.containers.findIndex(c => c.id === container.id);
    if (index !== -1) {
      state.containers.splice(index, 1, container);
    } else {
      state.containers.push(container);
    }
  },
  UPDATE_CONTAINER(state, container) {
    // Update the container in the containers array if it exists
    const index = state.containers.findIndex(c => c.id === container.id);
    if (index !== -1) {
      state.containers.splice(index, 1, container);
    } else {
      state.containers.push(container);
    }
    
    // Update the current container if it's the same
    if (state.currentContainer && state.currentContainer.id === container.id) {
      state.currentContainer = container;
    }
  },
  REMOVE_CONTAINER(state, id) {
    state.containers = state.containers.filter(container => container.id !== id);
    if (state.currentContainer && state.currentContainer.id === id) {
      state.currentContainer = null;
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
