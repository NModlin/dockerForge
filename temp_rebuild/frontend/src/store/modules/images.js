/**
 * Vuex store module for Docker images
 */
import axios from 'axios';

// Initial state
const state = {
  images: [],
  image: null,
  scans: [],
  currentScan: null,
  loading: false,
  error: null,
};

// Getters
const getters = {
  getImageById: (state) => (id) => {
    return state.images.find(image => image.id === id);
  },
  getImageByName: (state) => (name, tag = 'latest') => {
    return state.images.find(image => {
      return image.tags && image.tags.some(t => {
        const [imageName, imageTag] = t.split(':');
        return imageName === name && (imageTag || 'latest') === tag;
      });
    });
  },
  getScansForImage: (state) => (imageId) => {
    return state.scans.filter(scan => scan.image_id === imageId);
  },
};

// Actions
const actions = {
  /**
   * Fetch all images
   */
  async getImages({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/images');
      commit('SET_IMAGES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Fetch a single image by ID
   */
  async getImage({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/images/${id}`);
      commit('SET_IMAGE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Pull a new image
   */
  async pullImage({ commit }, { name, tag = 'latest' }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/images', { name, tag });
      commit('ADD_IMAGE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Delete an image
   */
  async removeImage({ commit }, { id, force = false }) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/images/${id}?force=${force}`);
      commit('REMOVE_IMAGE', id);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Scan an image for vulnerabilities
   */
  async scanImageVulnerabilities({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/images/${id}/scan`, {
        scan_type: 'vulnerability',
      });
      commit('SET_CURRENT_SCAN', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get all scans for an image
   */
  async getImageScans({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/images/${id}/scans`);
      commit('SET_SCANS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get a specific scan for an image
   */
  async getImageScan({ commit }, { imageId, scanId }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/images/${imageId}/scans/${scanId}`);
      commit('SET_CURRENT_SCAN', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
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
  SET_IMAGES(state, images) {
    state.images = images;
  },
  SET_IMAGE(state, image) {
    state.image = image;
    // Update the image in the images array if it exists
    const index = state.images.findIndex(i => i.id === image.id);
    if (index !== -1) {
      state.images.splice(index, 1, image);
    } else {
      state.images.push(image);
    }
  },
  ADD_IMAGE(state, image) {
    // Check if the image already exists
    const index = state.images.findIndex(i => i.id === image.id);
    if (index !== -1) {
      state.images.splice(index, 1, image);
    } else {
      state.images.push(image);
    }
  },
  REMOVE_IMAGE(state, id) {
    state.images = state.images.filter(image => image.id !== id);
    if (state.image && state.image.id === id) {
      state.image = null;
    }
  },
  SET_SCANS(state, scans) {
    state.scans = scans;
  },
  SET_CURRENT_SCAN(state, scan) {
    state.currentScan = scan;
    // Update the scan in the scans array if it exists
    const index = state.scans.findIndex(s => s.id === scan.scan.id);
    if (index !== -1) {
      state.scans.splice(index, 1, scan.scan);
    } else {
      state.scans.push(scan.scan);
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
