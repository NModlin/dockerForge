/**
 * Vuex store module for security features
 * Manages security scans, vulnerability data, remediation plans, and security policies
 */
import axios from 'axios';

export const state = {
  loading: false,
  error: null,
  securityScore: 0,
  vulnerabilityCounts: {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    UNKNOWN: 0
  },
  complianceStats: {
    passed: 0,
    failed: 0
  },
  recentScans: [],
  recommendations: [],
  scans: [],
  currentScan: null,
  remediationPlan: null,
  // Policy management
  policies: [],
  currentPolicy: null,
  policyViolations: [],
  policyLoading: false,
  policyError: null,
  // Compliance reporting
  complianceLoading: false,
  complianceError: null,
  complianceData: null,
  complianceReports: [],
  currentReport: null,
  complianceHistory: [],
  complianceFilters: {
    timeRange: '30d',
    resourceTypes: ['image', 'container', 'volume', 'network'],
    policyIds: [],
    severityLevels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
  }
};

export const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_DASHBOARD_DATA(state, data) {
    state.securityScore = data.security_score;
    state.vulnerabilityCounts = data.vulnerability_counts;
    state.complianceStats = data.compliance_stats;
    state.recentScans = data.recent_scans;
    state.recommendations = data.recommendations;
  },
  SET_SCANS(state, scans) {
    state.scans = scans;
  },
  SET_CURRENT_SCAN(state, scan) {
    state.currentScan = scan;
  },
  ADD_SCAN(state, scan) {
    state.scans.unshift(scan);
  },
  UPDATE_SCAN(state, updatedScan) {
    const index = state.scans.findIndex(scan => scan.scan_id === updatedScan.scan_id);
    if (index !== -1) {
      state.scans.splice(index, 1, updatedScan);
    }
    if (state.currentScan && state.currentScan.scan_id === updatedScan.scan_id) {
      state.currentScan = updatedScan;
    }
  },
  SET_REMEDIATION_PLAN(state, plan) {
    state.remediationPlan = plan;
  },
  // Policy mutations
  SET_POLICY_LOADING(state, loading) {
    state.policyLoading = loading;
  },
  SET_POLICY_ERROR(state, error) {
    state.policyError = error;
  },
  SET_POLICIES(state, policies) {
    state.policies = policies;
  },
  SET_CURRENT_POLICY(state, policy) {
    state.currentPolicy = policy;
  },
  ADD_POLICY(state, policy) {
    state.policies.unshift(policy);
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
  SET_POLICY_VIOLATIONS(state, violations) {
    state.policyViolations = violations;
  },
  ADD_POLICY_VIOLATION(state, violation) {
    state.policyViolations.unshift(violation);
  },
  UPDATE_POLICY_VIOLATION(state, updatedViolation) {
    const index = state.policyViolations.findIndex(v => v.id === updatedViolation.id);
    if (index !== -1) {
      state.policyViolations.splice(index, 1, updatedViolation);
    }
  },
  // Compliance mutations
  SET_COMPLIANCE_LOADING(state, loading) {
    state.complianceLoading = loading;
  },
  SET_COMPLIANCE_ERROR(state, error) {
    state.complianceError = error;
  },
  SET_COMPLIANCE_DATA(state, data) {
    state.complianceData = data;
  },
  SET_COMPLIANCE_REPORTS(state, reports) {
    state.complianceReports = reports;
  },
  SET_CURRENT_REPORT(state, report) {
    state.currentReport = report;
  },
  ADD_COMPLIANCE_REPORT(state, report) {
    state.complianceReports.unshift(report);
  },
  UPDATE_COMPLIANCE_REPORT(state, updatedReport) {
    const index = state.complianceReports.findIndex(report => report.id === updatedReport.id);
    if (index !== -1) {
      state.complianceReports.splice(index, 1, updatedReport);
    }
    if (state.currentReport && state.currentReport.id === updatedReport.id) {
      state.currentReport = updatedReport;
    }
  },
  REMOVE_COMPLIANCE_REPORT(state, reportId) {
    state.complianceReports = state.complianceReports.filter(report => report.id !== reportId);
    if (state.currentReport && state.currentReport.id === reportId) {
      state.currentReport = null;
    }
  },
  SET_COMPLIANCE_HISTORY(state, history) {
    state.complianceHistory = history;
  },
  UPDATE_COMPLIANCE_FILTERS(state, filters) {
    state.complianceFilters = { ...state.complianceFilters, ...filters };
  }
};

export const actions = {
  async fetchDashboard({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.get('/api/security/dashboard');
      commit('SET_DASHBOARD_DATA', response.data);
    } catch (error) {
      console.error('Error fetching security dashboard:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch security dashboard');
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async fetchScans({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.get('/api/security/scans');
      commit('SET_SCANS', response.data);
    } catch (error) {
      console.error('Error fetching security scans:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch security scans');
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async fetchScan({ commit }, scanId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.get(`/api/security/scan/${scanId}`);
      commit('SET_CURRENT_SCAN', response.data);
    } catch (error) {
      console.error(`Error fetching scan ${scanId}:`, error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch scan details');
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async scanImage({ commit }, { imageName, severityFilter, ignoreUnfixed }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.post('/api/security/scan/image', {
        image_name: imageName,
        severity_filter: severityFilter,
        ignore_unfixed: ignoreUnfixed
      });

      // Response is just the scan ID
      const scanId = response.data;

      // Create a placeholder scan result
      const placeholderScan = {
        scan_id: scanId,
        scan_type: 'IMAGE',
        status: 'PENDING',
        target: imageName,
        started_at: new Date().toISOString(),
        vulnerability_counts: {
          CRITICAL: 0,
          HIGH: 0,
          MEDIUM: 0,
          LOW: 0,
          UNKNOWN: 0
        },
        total_vulnerabilities: 0
      };

      commit('ADD_SCAN', placeholderScan);
      return scanId;
    } catch (error) {
      console.error('Error scanning image:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to start image scan');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async scanContainer({ commit }, { containerId, containerName, severityFilter, ignoreUnfixed }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.post('/api/security/scan/container', {
        container_id: containerId,
        container_name: containerName,
        severity_filter: severityFilter,
        ignore_unfixed: ignoreUnfixed
      });

      // Response is just the scan ID
      const scanId = response.data;

      // Create a placeholder scan result
      const placeholderScan = {
        scan_id: scanId,
        scan_type: 'CONTAINER',
        status: 'PENDING',
        target: containerName || containerId,
        started_at: new Date().toISOString(),
        vulnerability_counts: {
          CRITICAL: 0,
          HIGH: 0,
          MEDIUM: 0,
          LOW: 0,
          UNKNOWN: 0
        },
        total_vulnerabilities: 0
      };

      commit('ADD_SCAN', placeholderScan);
      return scanId;
    } catch (error) {
      console.error('Error scanning container:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to start container scan');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async pollScanStatus({ commit, dispatch }, { scanId, interval = 2000, maxAttempts = 60 }) {
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await axios.get(`/api/security/scan/${scanId}`);
        const scan = response.data;

        commit('UPDATE_SCAN', scan);

        if (scan.status === 'COMPLETED' || scan.status === 'FAILED') {
          return scan;
        }

        if (++attempts >= maxAttempts) {
          throw new Error('Maximum polling attempts reached');
        }

        // Continue polling
        return new Promise(resolve => {
          setTimeout(() => resolve(poll()), interval);
        });
      } catch (error) {
        console.error(`Error polling scan status for ${scanId}:`, error);
        throw error;
      }
    };

    return poll();
  },

  async getRemediationPlan({ commit }, { scanId, vulnerabilityId }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);

    try {
      const response = await axios.get(`/api/security/remediation/${scanId}/${vulnerabilityId}`);
      commit('SET_REMEDIATION_PLAN', response.data);
      return response.data;
    } catch (error) {
      console.error('Error getting remediation plan:', error);
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to get remediation plan');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  // Policy management actions
  async fetchPolicies({ commit }) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.get('/api/policies');
      commit('SET_POLICIES', response.data);
    } catch (error) {
      console.error('Error fetching security policies:', error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to fetch security policies');
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async fetchPolicy({ commit }, policyId) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.get(`/api/policies/${policyId}`);
      commit('SET_CURRENT_POLICY', response.data);
    } catch (error) {
      console.error(`Error fetching policy ${policyId}:`, error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to fetch policy details');
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async createPolicy({ commit }, policyData) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.post('/api/policies', policyData);
      commit('ADD_POLICY', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating policy:', error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to create policy');
      throw error;
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async updatePolicy({ commit }, { policyId, policyData }) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.put(`/api/policies/${policyId}`, policyData);
      commit('UPDATE_POLICY', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error updating policy ${policyId}:`, error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to update policy');
      throw error;
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async deletePolicy({ commit }, policyId) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      await axios.delete(`/api/policies/${policyId}`);
      commit('REMOVE_POLICY', policyId);
    } catch (error) {
      console.error(`Error deleting policy ${policyId}:`, error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to delete policy');
      throw error;
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async fetchPolicyViolations({ commit }) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.get('/api/policies/violations');
      commit('SET_POLICY_VIOLATIONS', response.data);
    } catch (error) {
      console.error('Error fetching policy violations:', error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to fetch policy violations');
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async evaluateResource({ commit }, { resourceType, resourceId, scanId }) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const url = `/api/evaluate/${resourceType}/${resourceId}${scanId ? `?scan_id=${scanId}` : ''}`;
      const response = await axios.post(url);
      return response.data;
    } catch (error) {
      console.error(`Error evaluating ${resourceType} ${resourceId}:`, error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to evaluate resource');
      throw error;
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  async resolveViolation({ commit }, { violationId, resolutionNotes }) {
    commit('SET_POLICY_LOADING', true);
    commit('SET_POLICY_ERROR', null);

    try {
      const response = await axios.post(`/api/policies/violations/${violationId}/resolve`, {
        resolution_notes: resolutionNotes
      });
      commit('UPDATE_POLICY_VIOLATION', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error resolving violation ${violationId}:`, error);
      commit('SET_POLICY_ERROR', error.response?.data?.detail || 'Failed to resolve violation');
      throw error;
    } finally {
      commit('SET_POLICY_LOADING', false);
    }
  },

  // Compliance reporting actions
  async fetchComplianceData({ commit, state }) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const { timeRange, resourceTypes, policyIds, severityLevels } = state.complianceFilters;
      const response = await axios.get('/api/compliance/dashboard', {
        params: {
          time_range: timeRange,
          resource_types: resourceTypes.join(','),
          policy_ids: policyIds.join(','),
          severity_levels: severityLevels.join(',')
        }
      });
      commit('SET_COMPLIANCE_DATA', response.data);
    } catch (error) {
      console.error('Error fetching compliance data:', error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to fetch compliance data');
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  async fetchComplianceReports({ commit }) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const response = await axios.get('/api/compliance/reports');
      commit('SET_COMPLIANCE_REPORTS', response.data);
    } catch (error) {
      console.error('Error fetching compliance reports:', error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to fetch compliance reports');
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  async fetchComplianceReport({ commit }, reportId) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const response = await axios.get(`/api/compliance/reports/${reportId}`);
      commit('SET_CURRENT_REPORT', response.data);
    } catch (error) {
      console.error(`Error fetching compliance report ${reportId}:`, error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to fetch compliance report');
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  async generateComplianceReport({ commit, state }, reportConfig) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const response = await axios.post('/api/compliance/reports/generate', {
        ...reportConfig,
        filters: state.complianceFilters
      });
      commit('ADD_COMPLIANCE_REPORT', response.data);
      return response.data;
    } catch (error) {
      console.error('Error generating compliance report:', error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to generate compliance report');
      throw error;
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  async deleteComplianceReport({ commit }, reportId) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      await axios.delete(`/api/compliance/reports/${reportId}`);
      commit('REMOVE_COMPLIANCE_REPORT', reportId);
    } catch (error) {
      console.error(`Error deleting compliance report ${reportId}:`, error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to delete compliance report');
      throw error;
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  async fetchComplianceHistory({ commit, state }) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const { timeRange, resourceTypes, policyIds, severityLevels } = state.complianceFilters;
      const response = await axios.get('/api/compliance/history', {
        params: {
          time_range: timeRange,
          resource_types: resourceTypes.join(','),
          policy_ids: policyIds.join(','),
          severity_levels: severityLevels.join(',')
        }
      });
      commit('SET_COMPLIANCE_HISTORY', response.data);
    } catch (error) {
      console.error('Error fetching compliance history:', error);
      commit('SET_COMPLIANCE_ERROR', error.response?.data?.detail || 'Failed to fetch compliance history');
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  },

  updateComplianceFilters({ commit, dispatch }, filters) {
    commit('UPDATE_COMPLIANCE_FILTERS', filters);
    // Refresh data with new filters
    dispatch('fetchComplianceData');
    dispatch('fetchComplianceHistory');
  },

  async exportComplianceReport({ commit, state }, { reportId, format }) {
    commit('SET_COMPLIANCE_LOADING', true);
    commit('SET_COMPLIANCE_ERROR', null);

    try {
      const response = await axios.get(`/api/compliance/reports/${reportId}/export`, {
        params: { format },
        responseType: 'blob'
      });

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `compliance-report-${reportId}.${format.toLowerCase()}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      return true;
    } catch (error) {
      console.error(`Error exporting compliance report ${reportId}:`, error);
      commit('SET_COMPLIANCE_ERROR', 'Failed to export compliance report');
      throw error;
    } finally {
      commit('SET_COMPLIANCE_LOADING', false);
    }
  }
};

export const getters = {
  isLoading: state => state.loading,
  hasError: state => state.error !== null,
  errorMessage: state => state.error,
  securityScore: state => state.securityScore,
  vulnerabilityCounts: state => state.vulnerabilityCounts,
  totalVulnerabilities: state =>
    state.vulnerabilityCounts.CRITICAL +
    state.vulnerabilityCounts.HIGH +
    state.vulnerabilityCounts.MEDIUM +
    state.vulnerabilityCounts.LOW +
    state.vulnerabilityCounts.UNKNOWN,
  criticalVulnerabilities: state => state.vulnerabilityCounts.CRITICAL,
  highVulnerabilities: state => state.vulnerabilityCounts.HIGH,
  mediumVulnerabilities: state => state.vulnerabilityCounts.MEDIUM,
  lowVulnerabilities: state => state.vulnerabilityCounts.LOW,
  complianceStats: state => state.complianceStats,
  recentScans: state => state.recentScans,
  recommendations: state => state.recommendations,
  scans: state => state.scans,
  currentScan: state => state.currentScan,
  remediationPlan: state => state.remediationPlan,

  // Get scans filtered by type
  imageScans: state => state.scans.filter(scan => scan.scan_type === 'IMAGE'),
  containerScans: state => state.scans.filter(scan => scan.scan_type === 'CONTAINER'),

  // Get scans filtered by status
  pendingScans: state => state.scans.filter(scan => scan.status === 'PENDING' || scan.status === 'IN_PROGRESS'),
  completedScans: state => state.scans.filter(scan => scan.status === 'COMPLETED'),
  failedScans: state => state.scans.filter(scan => scan.status === 'FAILED'),

  // Policy getters
  isPolicyLoading: state => state.policyLoading,
  hasPolicyError: state => state.policyError !== null,
  policyErrorMessage: state => state.policyError,
  policies: state => state.policies,
  currentPolicy: state => state.currentPolicy,
  policyViolations: state => state.policyViolations,

  // Get enabled policies
  enabledPolicies: state => state.policies.filter(policy => policy.enabled),

  // Get policies by rule type
  severityPolicies: state => state.policies.filter(policy =>
    policy.rules.some(rule => rule.rule_type === 'SEVERITY')),
  cvePolicies: state => state.policies.filter(policy =>
    policy.rules.some(rule => rule.rule_type === 'CVE')),
  packagePolicies: state => state.policies.filter(policy =>
    policy.rules.some(rule => rule.rule_type === 'PACKAGE')),
  containerPolicies: state => state.policies.filter(policy =>
    policy.rules.some(rule => rule.rule_type === 'CONTAINER')),

  // Get violations by status
  unresolvedViolations: state => state.policyViolations.filter(violation => !violation.resolved),
  resolvedViolations: state => state.policyViolations.filter(violation => violation.resolved),

  // Get violations by severity
  criticalViolations: state => state.policyViolations.filter(violation => violation.severity === 'CRITICAL'),
  highViolations: state => state.policyViolations.filter(violation => violation.severity === 'HIGH'),
  mediumViolations: state => state.policyViolations.filter(violation => violation.severity === 'MEDIUM'),
  lowViolations: state => state.policyViolations.filter(violation => violation.severity === 'LOW'),

  // Compliance getters
  isComplianceLoading: state => state.complianceLoading,
  hasComplianceError: state => state.complianceError !== null,
  complianceErrorMessage: state => state.complianceError,
  complianceData: state => state.complianceData,
  complianceReports: state => state.complianceReports,
  currentReport: state => state.currentReport,
  complianceHistory: state => state.complianceHistory,
  complianceFilters: state => state.complianceFilters,

  // Get compliance statistics
  complianceScore: state => state.complianceData ? state.complianceData.compliance_score : 0,
  policyComplianceStats: state => state.complianceData ? state.complianceData.policy_compliance : [],
  resourceComplianceStats: state => state.complianceData ? state.complianceData.resource_compliance : [],
  complianceTrend: state => state.complianceHistory ? state.complianceHistory.trend : [],

  // Get reports by status
  recentReports: state => state.complianceReports.slice(0, 5),
  scheduledReports: state => state.complianceReports.filter(report => report.scheduled),

  // Get compliance by resource type
  imageCompliance: state => state.complianceData ?
    state.complianceData.resource_compliance.find(item => item.resource_type === 'image') : null,
  containerCompliance: state => state.complianceData ?
    state.complianceData.resource_compliance.find(item => item.resource_type === 'container') : null,
  volumeCompliance: state => state.complianceData ?
    state.complianceData.resource_compliance.find(item => item.resource_type === 'volume') : null,
  networkCompliance: state => state.complianceData ?
    state.complianceData.resource_compliance.find(item => item.resource_type === 'network') : null
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
