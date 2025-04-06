/**
 * Alert service for the DockerForge Web UI.
 * 
 * This service provides functions for interacting with the alert API endpoints.
 */
import axios from 'axios';
import store from '@/store';

// API base URL
const API_URL = process.env.VUE_APP_API_URL || '/api';

/**
 * Get all alert rules.
 * 
 * @param {Object} options - Options for the request
 * @param {number} options.skip - Number of records to skip
 * @param {number} options.limit - Maximum number of records to return
 * @param {boolean} options.enabledOnly - Whether to return only enabled rules
 * @returns {Promise<Array>} Alert rules
 */
export async function getAlertRules({ skip = 0, limit = 100, enabledOnly = false } = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/rules`, {
    params: {
      skip,
      limit,
      enabled_only: enabledOnly
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get an alert rule by ID.
 * 
 * @param {string} ruleId - Alert rule ID
 * @returns {Promise<Object>} Alert rule
 */
export async function getAlertRule(ruleId) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/rules/${ruleId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Create a new alert rule.
 * 
 * @param {Object} rule - Alert rule data
 * @returns {Promise<Object>} Created alert rule
 */
export async function createAlertRule(rule) {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/alerts/rules`, rule, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Update an alert rule.
 * 
 * @param {string} ruleId - Alert rule ID
 * @param {Object} rule - Alert rule update data
 * @returns {Promise<Object>} Updated alert rule
 */
export async function updateAlertRule(ruleId, rule) {
  const token = store.getters['auth/token'];
  
  const response = await axios.put(`${API_URL}/monitoring/alerts/rules/${ruleId}`, rule, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Delete an alert rule.
 * 
 * @param {string} ruleId - Alert rule ID
 * @returns {Promise<void>}
 */
export async function deleteAlertRule(ruleId) {
  const token = store.getters['auth/token'];
  
  await axios.delete(`${API_URL}/monitoring/alerts/rules/${ruleId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
}

/**
 * Get all notification channels.
 * 
 * @param {Object} options - Options for the request
 * @param {number} options.skip - Number of records to skip
 * @param {number} options.limit - Maximum number of records to return
 * @param {boolean} options.enabledOnly - Whether to return only enabled channels
 * @returns {Promise<Array>} Notification channels
 */
export async function getNotificationChannels({ skip = 0, limit = 100, enabledOnly = false } = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/channels`, {
    params: {
      skip,
      limit,
      enabled_only: enabledOnly
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get a notification channel by ID.
 * 
 * @param {string} channelId - Notification channel ID
 * @returns {Promise<Object>} Notification channel
 */
export async function getNotificationChannel(channelId) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/channels/${channelId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Create a new notification channel.
 * 
 * @param {Object} channel - Notification channel data
 * @returns {Promise<Object>} Created notification channel
 */
export async function createNotificationChannel(channel) {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/alerts/channels`, channel, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Update a notification channel.
 * 
 * @param {string} channelId - Notification channel ID
 * @param {Object} channel - Notification channel update data
 * @returns {Promise<Object>} Updated notification channel
 */
export async function updateNotificationChannel(channelId, channel) {
  const token = store.getters['auth/token'];
  
  const response = await axios.put(`${API_URL}/monitoring/alerts/channels/${channelId}`, channel, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Delete a notification channel.
 * 
 * @param {string} channelId - Notification channel ID
 * @returns {Promise<void>}
 */
export async function deleteNotificationChannel(channelId) {
  const token = store.getters['auth/token'];
  
  await axios.delete(`${API_URL}/monitoring/alerts/channels/${channelId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
}

/**
 * Get all alerts with optional filtering.
 * 
 * @param {Object} options - Options for the request
 * @param {number} options.skip - Number of records to skip
 * @param {number} options.limit - Maximum number of records to return
 * @param {Array<string>} options.severity - Filter by severity
 * @param {Array<string>} options.status - Filter by status
 * @param {Array<string>} options.source - Filter by source
 * @param {string} options.sourceId - Filter by source ID
 * @param {Array<string>} options.metricType - Filter by metric type
 * @param {string} options.startDate - Filter by start date (ISO format)
 * @param {string} options.endDate - Filter by end date (ISO format)
 * @param {string} options.ruleId - Filter by rule ID
 * @returns {Promise<Array>} Alerts
 */
export async function getAlerts(options = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts`, {
    params: {
      skip: options.skip || 0,
      limit: options.limit || 100,
      severity: options.severity,
      status: options.status,
      source: options.source,
      source_id: options.sourceId,
      metric_type: options.metricType,
      start_date: options.startDate,
      end_date: options.endDate,
      rule_id: options.ruleId
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get an alert by ID.
 * 
 * @param {string} alertId - Alert ID
 * @returns {Promise<Object>} Alert
 */
export async function getAlert(alertId) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/${alertId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Create a new alert.
 * 
 * @param {Object} alert - Alert data
 * @returns {Promise<Object>} Created alert
 */
export async function createAlert(alert) {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/alerts`, alert, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Update an alert.
 * 
 * @param {string} alertId - Alert ID
 * @param {Object} alert - Alert update data
 * @returns {Promise<Object>} Updated alert
 */
export async function updateAlert(alertId, alert) {
  const token = store.getters['auth/token'];
  
  const response = await axios.put(`${API_URL}/monitoring/alerts/${alertId}`, alert, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Acknowledge an alert.
 * 
 * @param {string} alertId - Alert ID
 * @returns {Promise<Object>} Updated alert
 */
export async function acknowledgeAlert(alertId) {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/alerts/${alertId}/acknowledge`, {}, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Resolve an alert.
 * 
 * @param {string} alertId - Alert ID
 * @param {string} resolutionNotes - Resolution notes
 * @returns {Promise<Object>} Updated alert
 */
export async function resolveAlert(alertId, resolutionNotes = null) {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/alerts/${alertId}/resolve`, 
    resolutionNotes ? { resolution_notes: resolutionNotes } : {}, 
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.data;
}

/**
 * Delete an alert.
 * 
 * @param {string} alertId - Alert ID
 * @returns {Promise<void>}
 */
export async function deleteAlert(alertId) {
  const token = store.getters['auth/token'];
  
  await axios.delete(`${API_URL}/monitoring/alerts/${alertId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
}

/**
 * Get alert statistics.
 * 
 * @param {number} days - Number of days to include in statistics
 * @returns {Promise<Object>} Alert statistics
 */
export async function getAlertStatistics(days = 7) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/alerts/statistics`, {
    params: {
      days
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}
