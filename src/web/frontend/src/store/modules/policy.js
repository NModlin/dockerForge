/**
 * Vuex store module for security policy management
 * Manages security policies, policy evaluation, and compliance status
 */
import axios from 'axios';

export const state = {
  loading: false,
  error: null,
  policies: [],
  currentPolicy: null,
  violations: [],
  complianceStatus: null,
  evaluationResults: []
};

export const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_POLICIES(state, policies) {
    state.policies = policies;
  },
  SET_CURRENT_POLICY(state, policy) {
    state.currentPolicy = policy;
  },
  SET_VIOLATIONS(state, violations) {
    state.violations = violations;
  },
  SET_COMPLIANCE_STATUS(state, status) {
    state.complianceStatus = status;
  },
  SET_EVALUATION_RESULTS(state, results) {
    state.evaluationResults = results;
  },
  ADD_POLICY(state, policy) {
    state.policies.push(policy);
  },
  UPDATE_POLICY(state, updatedPolicy) {
    const index = state.policies.findIndex(policy => policy.id === updatedPolicy.id);
    if (index !== -1) {
      state.policies.splice(index, 1, updatedPolicy);
    }
    if (state.currentPolicy && state.currentPolicy.id === updatedPolicy.id) {
      state.currentPolicy = updatedPolicy;
    }
  },
  REMOVE_POLICY(state, policyId) {
    state.policies = state.policies.filter(policy => policy.id !== policyId);
    if (state.currentPolicy && state.currentPolicy.id === policyId) {
      state.currentPolicy = null;
    }
  },
  UPDATE_VIOLATION(state, updatedViolation) {
    const index = state.violations.findIndex(violation => violation.id === updatedViolation.id);
    if (index !== -1) {
      state.violations.splice(index, 1, updatedViolation);
    }
  }
};

export const actions = {
  async fetchPolicies({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const response = await axios.get('/api/security/policy/policies');
      commit('SET_POLICIES', response.data);
    } catch (error) {
      console.error('Error fetching security policies:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch security policies');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchPolicy({ commit }, policyId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const response = await axios.get(`/api/security/policy/policies/${policyId}`);
      commit('SET_CURRENT_POLICY', response.data);
    } catch (error) {
      console.error(`Error fetching policy ${policyId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch policy details');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async createPolicy({ commit }, policyData) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const response = await axios.post('/api/security/policy/policies', policyData);
      commit('ADD_POLICY', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating policy:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to create policy');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async updatePolicy({ commit }, { policyId, policyData }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const response = await axios.put(`/api/security/policy/policies/${policyId}`, policyData);
      commit('UPDATE_POLICY', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error updating policy ${policyId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to update policy');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async deletePolicy({ commit }, policyId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      await axios.delete(`/api/security/policy/policies/${policyId}`);
      commit('REMOVE_POLICY', policyId);
      return true;
    } catch (error) {
      console.error(`Error deleting policy ${policyId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to delete policy');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchViolations({ commit }, { policyId, resourceType, resourceId, resolved }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      let url = '/api/security/policy/violations';
      const params = {};
      
      if (policyId) params.policy_id = policyId;
      if (resourceType) params.resource_type = resourceType;
      if (resourceId) params.resource_id = resourceId;
      if (resolved !== undefined) params.resolved = resolved;
      
      const response = await axios.get(url, { params });
      commit('SET_VIOLATIONS', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching policy violations:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch policy violations');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async resolveViolation({ commit }, { violationId, resolutionNotes }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const params = {};
      if (resolutionNotes) params.resolution_notes = resolutionNotes;
      
      const response = await axios.post(`/api/security/policy/violations/${violationId}/resolve`, null, { params });
      commit('UPDATE_VIOLATION', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error resolving violation ${violationId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to resolve violation');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchComplianceStatus({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      const response = await axios.get('/api/security/policy/compliance');
      commit('SET_COMPLIANCE_STATUS', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching compliance status:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch compliance status');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async evaluatePolicies({ commit }, { resourceType, resourceId, scanId }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    
    try {
      let url = `/api/security/policy/evaluate/${resourceType}/${resourceId}`;
      const params = {};
      
      if (scanId) params.scan_id = scanId;
      
      const response = await axios.post(url, null, { params });
      commit('SET_EVALUATION_RESULTS', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error evaluating policies for ${resourceType}/${resourceId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to evaluate policies');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

export const getters = {
  isLoading: state => state.loading,
  hasError: state => state.error !== null,
  errorMessage: state => state.error,
  policies: state => state.policies,
  currentPolicy: state => state.currentPolicy,
  violations: state => state.violations,
  complianceStatus: state => state.complianceStatus,
  evaluationResults: state => state.evaluationResults,
  
  // Get enabled policies
  enabledPolicies: state => state.policies.filter(policy => policy.enabled),
  
  // Get policies by type
  policiesByType: state => type => {
    return state.policies.filter(policy => {
      return policy.rules.some(rule => rule.rule_type === type);
    });
  },
  
  // Get violations by severity
  violationsBySeverity: state => severity => {
    return state.violations.filter(violation => violation.severity === severity);
  },
  
  // Get unresolved violations
  unresolvedViolations: state => state.violations.filter(violation => !violation.resolved),
  
  // Get resolved violations
  resolvedViolations: state => state.violations.filter(violation => violation.resolved),
  
  // Get blocking violations
  blockingViolations: state => state.violations.filter(violation => violation.action_taken === 'BLOCK' && !violation.resolved),
  
  // Get warning violations
  warningViolations: state => state.violations.filter(violation => violation.action_taken === 'WARN' && !violation.resolved),
  
  // Get compliance percentage
  compliancePercentage: state => {
    if (!state.complianceStatus) return 0;
    const { total_resources, compliant_resources } = state.complianceStatus;
    return total_resources > 0 ? Math.round((compliant_resources / total_resources) * 100) : 100;
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
