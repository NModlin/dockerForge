/**
 * Vuex store module for API key management
 * Manages API keys for programmatic access to the API
 */
import axios from 'axios';

// Initial state
export const state = {
  loading: false,
  error: null,
  apiKeys: [],
  currentKey: null,
  keyUsage: null,
  keyUsageStats: null,
  usageLoading: false
};

// Getters
export const getters = {
  getApiKeys: (state) => state.apiKeys,
  getCurrentKey: (state) => state.currentKey,
  isLoading: (state) => state.loading,
  getError: (state) => state.error,
  getKeyUsage: (state) => state.keyUsage,
  getKeyUsageStats: (state) => state.keyUsageStats,
  isUsageLoading: (state) => state.usageLoading
};

// Mutations
export const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_API_KEYS(state, apiKeys) {
    state.apiKeys = apiKeys;
  },
  SET_CURRENT_KEY(state, key) {
    state.currentKey = key;
  },
  ADD_API_KEY(state, key) {
    state.apiKeys.unshift(key);
  },
  UPDATE_API_KEY(state, updatedKey) {
    const index = state.apiKeys.findIndex(key => key.id === updatedKey.id);
    if (index !== -1) {
      state.apiKeys.splice(index, 1, updatedKey);
    }
  },
  REMOVE_API_KEY(state, keyId) {
    state.apiKeys = state.apiKeys.filter(key => key.id !== keyId);
  },
  SET_KEY_USAGE(state, usage) {
    state.keyUsage = usage;
  },
  SET_KEY_USAGE_STATS(state, stats) {
    state.keyUsageStats = stats;
  },
  SET_USAGE_LOADING(state, loading) {
    state.usageLoading = loading;
  }
};

// Actions
export const actions = {
  async fetchApiKeys({ commit }) {
    commit('SET_LOADING', true);

    try {
      const response = await axios.get('/api/api-keys');
      commit('SET_API_KEYS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch API keys');
      console.error('Error fetching API keys:', error);
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async createApiKey({ commit }, keyData) {
    commit('SET_LOADING', true);

    try {
      const response = await axios.post('/api/api-keys', keyData);
      commit('ADD_API_KEY', response.data);
      commit('SET_CURRENT_KEY', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create API key');
      console.error('Error creating API key:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async updateApiKey({ commit }, { keyId, keyData }) {
    commit('SET_LOADING', true);

    try {
      const response = await axios.put(`/api/api-keys/${keyId}`, keyData);
      commit('UPDATE_API_KEY', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update API key');
      console.error('Error updating API key:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async deleteApiKey({ commit }, keyId) {
    commit('SET_LOADING', true);

    try {
      await axios.delete(`/api/api-keys/${keyId}`);
      commit('REMOVE_API_KEY', keyId);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete API key');
      console.error('Error deleting API key:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  clearCurrentKey({ commit }) {
    commit('SET_CURRENT_KEY', null);
  },

  async fetchKeyUsage({ commit }, { keyId, params = {} }) {
    commit('SET_USAGE_LOADING', true);

    try {
      const response = await axios.get(`/api/settings/api-keys/${keyId}/usage`, { params });
      commit('SET_KEY_USAGE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch API key usage');
      console.error('Error fetching API key usage:', error);
      return [];
    } finally {
      commit('SET_USAGE_LOADING', false);
    }
  },

  async fetchKeyUsageStats({ commit }, keyId) {
    commit('SET_USAGE_LOADING', true);

    try {
      const response = await axios.get(`/api/settings/api-keys/${keyId}/stats`);
      commit('SET_KEY_USAGE_STATS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch API key usage statistics');
      console.error('Error fetching API key usage statistics:', error);
      return null;
    } finally {
      commit('SET_USAGE_LOADING', false);
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
};
