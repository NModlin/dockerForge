/**
 * Vuex store module for Docker networks
 */
import axios from 'axios';

// Initial state
const state = {
  networks: [],
  network: null,
  loading: false,
  error: null,
  connectedContainers: [],
};

// Getters
const getters = {
  getNetworkById: (state) => (id) => {
    return state.networks.find(network => network.id === id);
  },
  getNetworkByName: (state) => (name) => {
    return state.networks.find(network => network.name === name);
  },
  bridgeNetworks: (state) => {
    return state.networks.filter(network => network.driver === 'bridge');
  },
  overlayNetworks: (state) => {
    return state.networks.filter(network => network.driver === 'overlay');
  },
  hostNetworks: (state) => {
    return state.networks.filter(network => network.driver === 'host');
  },
  macvlanNetworks: (state) => {
    return state.networks.filter(network => network.driver === 'macvlan');
  },
  ipvlanNetworks: (state) => {
    return state.networks.filter(network => network.driver === 'ipvlan');
  },
};

// Actions
const actions = {
  /**
   * Get all networks
   */
  async getNetworks({ commit }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/networks');
      commit('SET_NETWORKS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get a network by ID
   */
  async getNetwork({ commit }, networkId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/networks/${networkId}`);
      commit('SET_NETWORK', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Create a new network
   */
  async createNetwork({ commit }, networkData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/networks', networkData);
      commit('ADD_NETWORK', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Delete a network
   */
  async deleteNetwork({ commit }, networkId) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/networks/${networkId}`);
      commit('REMOVE_NETWORK', networkId);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Get containers connected to a network
   */
  async getConnectedContainers({ commit }, networkId) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/networks/${networkId}/containers`);
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
   * Connect a container to a network
   */
  async connectContainer({ commit }, { networkId, containerId, aliases }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/networks/${networkId}/connect`, {
        container_id: containerId,
        aliases: aliases || []
      });
      
      // Update connected containers
      await this.dispatch('networks/getConnectedContainers', networkId);
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || error.message);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  /**
   * Disconnect a container from a network
   */
  async disconnectContainer({ commit }, { networkId, containerId }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post(`/api/networks/${networkId}/disconnect`, {
        container_id: containerId
      });
      
      // Update connected containers
      await this.dispatch('networks/getConnectedContainers', networkId);
      
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
  SET_NETWORKS(state, networks) {
    state.networks = networks;
  },
  SET_NETWORK(state, network) {
    state.network = network;
  },
  ADD_NETWORK(state, network) {
    state.networks.push(network);
  },
  REMOVE_NETWORK(state, networkId) {
    state.networks = state.networks.filter(network => network.id !== networkId);
    if (state.network && state.network.id === networkId) {
      state.network = null;
    }
  },
  SET_CONNECTED_CONTAINERS(state, containers) {
    state.connectedContainers = containers;
  },
  UPDATE_NETWORK(state, updatedNetwork) {
    const index = state.networks.findIndex(network => network.id === updatedNetwork.id);
    if (index !== -1) {
      state.networks.splice(index, 1, updatedNetwork);
    }
    if (state.network && state.network.id === updatedNetwork.id) {
      state.network = updatedNetwork;
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
