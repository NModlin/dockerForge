/**
 * Vuex store module for Docker Compose
 */
import axios from 'axios';

// Initial state
const state = {
  composeFiles: [],
  composeFile: null,
  loading: false,
  error: null,
  services: [],
};

// Getters
const getters = {
  getComposeFileById: (state) => (id) => {
    return state.composeFiles.find(file => file.id === id);
  },
  getComposeFileByName: (state) => (name) => {
    return state.composeFiles.find(file => file.name === name);
  },
  runningServices: (state) => {
    return state.services.filter(service => service.status === 'running');
  },
  stoppedServices: (state) => {
    return state.services.filter(service => service.status === 'stopped');
  },
};

// Actions
const actions = {
  /**
   * Get all compose files
   */
  async getComposeFiles({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/compose');
      commit('SET_COMPOSE_FILES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get a compose file by ID
   */
  async getComposeFile({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/compose/${fileId}`);
      commit('SET_COMPOSE_FILE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Create a new compose file
   */
  async createComposeFile({ commit }, fileData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/compose', fileData);
      commit('ADD_COMPOSE_FILE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Update a compose file
   */
  async updateComposeFile({ commit }, { fileId, fileData }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/api/compose/${fileId}`, fileData);
      commit('UPDATE_COMPOSE_FILE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Delete a compose file
   */
  async deleteComposeFile({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/compose/${fileId}`);
      commit('REMOVE_COMPOSE_FILE', fileId);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get services for a compose file
   */
  async getComposeServices({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/compose/${fileId}/services`);
      commit('SET_SERVICES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Start a compose project
   */
  async startComposeProject({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/compose/${fileId}/up`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Stop a compose project
   */
  async stopComposeProject({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/compose/${fileId}/down`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Restart a compose project
   */
  async restartComposeProject({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/compose/${fileId}/restart`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Pull images for a compose project
   */
  async pullComposeImages({ commit }, fileId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/compose/${fileId}/pull`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get logs for a compose project
   */
  async getComposeLogs({ commit }, { fileId, service, tail }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/compose/${fileId}/logs`, {
        params: {
          service,
          tail: tail || 100
        }
      });
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

// Mutations
const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_COMPOSE_FILES(state, files) {
    state.composeFiles = files;
  },
  SET_COMPOSE_FILE(state, file) {
    state.composeFile = file;
  },
  ADD_COMPOSE_FILE(state, file) {
    state.composeFiles.push(file);
  },
  UPDATE_COMPOSE_FILE(state, updatedFile) {
    const index = state.composeFiles.findIndex(file => file.id === updatedFile.id);
    if (index !== -1) {
      state.composeFiles.splice(index, 1, updatedFile);
    }
    if (state.composeFile && state.composeFile.id === updatedFile.id) {
      state.composeFile = updatedFile;
    }
  },
  REMOVE_COMPOSE_FILE(state, fileId) {
    state.composeFiles = state.composeFiles.filter(file => file.id !== fileId);
    if (state.composeFile && state.composeFile.id === fileId) {
      state.composeFile = null;
    }
  },
  SET_SERVICES(state, services) {
    state.services = services;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
