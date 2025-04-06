/**
 * Vuex store module for Docker volumes
 */
import axios from 'axios';

// Initial state
const state = {
  volumes: [],
  volume: null,
  loading: false,
  error: null,
  connectedContainers: [],
};

// Getters
const getters = {
  getVolumeById: (state) => (id) => {
    return state.volumes.find(volume => volume.id === id);
  },
  getVolumeByName: (state) => (name) => {
    return state.volumes.find(volume => volume.name === name);
  },
  localVolumes: (state) => {
    return state.volumes.filter(volume => volume.driver === 'local');
  },
  bindMountVolumes: (state) => {
    return state.volumes.filter(volume => volume.type === 'bind');
  },
  tmpfsVolumes: (state) => {
    return state.volumes.filter(volume => volume.type === 'tmpfs');
  },
  namedVolumes: (state) => {
    return state.volumes.filter(volume => volume.type === 'volume');
  },
};

// Actions
const actions = {
  /**
   * Get all volumes
   */
  async getVolumes({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/volumes');
      commit('SET_VOLUMES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get a volume by ID
   */
  async getVolume({ commit }, volumeId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/volumes/${volumeId}`);
      commit('SET_VOLUME', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Create a new volume
   */
  async createVolume({ commit }, volumeData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/volumes', volumeData);
      commit('ADD_VOLUME', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Delete a volume
   */
  async deleteVolume({ commit }, volumeId) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/volumes/${volumeId}`);
      commit('REMOVE_VOLUME', volumeId);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get containers using a volume
   */
  async getConnectedContainers({ commit }, volumeId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/volumes/${volumeId}/containers`);
      commit('SET_CONNECTED_CONTAINERS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Prune unused volumes
   */
  async pruneVolumes({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/volumes/prune');
      
      // Refresh volumes list after pruning
      await this.dispatch('volumes/getVolumes');
      
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
  SET_VOLUMES(state, volumes) {
    state.volumes = volumes;
  },
  SET_VOLUME(state, volume) {
    state.volume = volume;
  },
  ADD_VOLUME(state, volume) {
    state.volumes.push(volume);
  },
  REMOVE_VOLUME(state, volumeId) {
    state.volumes = state.volumes.filter(volume => volume.id !== volumeId);
    if (state.volume && state.volume.id === volumeId) {
      state.volume = null;
    }
  },
  SET_CONNECTED_CONTAINERS(state, containers) {
    state.connectedContainers = containers;
  },
  UPDATE_VOLUME(state, updatedVolume) {
    const index = state.volumes.findIndex(volume => volume.id === updatedVolume.id);
    if (index !== -1) {
      state.volumes.splice(index, 1, updatedVolume);
    }
    if (state.volume && state.volume.id === updatedVolume.id) {
      state.volume = updatedVolume;
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
