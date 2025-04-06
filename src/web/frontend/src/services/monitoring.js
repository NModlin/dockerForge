/**
 * Monitoring service for the DockerForge Web UI.
 * 
 * This service provides functions for interacting with the monitoring API endpoints.
 */
import axios from 'axios';
import store from '@/store';

// API base URL
const API_URL = process.env.VUE_APP_API_URL || '/api';

/**
 * Get host metrics.
 * 
 * @returns {Promise<Object>} Host metrics
 */
export async function getHostMetrics() {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/host/metrics`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get host metrics history.
 * 
 * @param {string} metricType - Metric type (cpu, memory, disk, network)
 * @param {number} hours - Number of hours of history to retrieve
 * @returns {Promise<Array>} Metrics history
 */
export async function getHostMetricsHistory(metricType, hours = 1) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/host/metrics/history/${metricType}`, {
    params: { hours },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get system information.
 * 
 * @returns {Promise<Object>} System information
 */
export async function getSystemInfo() {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/host/system-info`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get resource stats summary.
 * 
 * @returns {Promise<Object>} Resource stats summary
 */
export async function getResourceStatsSummary() {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/host/stats-summary`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get container metrics.
 * 
 * @param {string} containerId - Container ID
 * @returns {Promise<Object>} Container metrics
 */
export async function getContainerMetrics(containerId) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/stats/${containerId}/current`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get container metrics history.
 * 
 * @param {string} containerId - Container ID
 * @param {string} metricType - Metric type (cpu, memory, network, disk)
 * @param {number} hours - Number of hours of history to retrieve
 * @returns {Promise<Array>} Metrics history
 */
export async function getContainerMetricsHistory(containerId, metricType, hours = 1) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/stats/${containerId}/history`, {
    params: { metric_type: metricType, hours },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Create WebSocket connection for container stats.
 * 
 * @param {string} containerId - Container ID
 * @param {Function} onMessage - Message handler
 * @param {Function} onError - Error handler
 * @param {Function} onClose - Close handler
 * @returns {WebSocket} WebSocket connection
 */
export function createContainerStatsWebSocket(containerId, onMessage, onError, onClose) {
  const token = store.getters['auth/token'];
  const userId = store.getters['auth/userId'] || 'anonymous';
  
  // Create WebSocket URL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = process.env.VUE_APP_API_HOST || window.location.host;
  const wsUrl = `${protocol}//${host}/api/stats/ws/${containerId}?user_id=${userId}&token=${token}`;
  
  // Create WebSocket
  const ws = new WebSocket(wsUrl);
  
  // Set up event handlers
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) {
      onError(error);
    }
  };
  
  ws.onclose = (event) => {
    console.log('WebSocket closed:', event);
    if (onClose) {
      onClose(event);
    }
  };
  
  return ws;
}

export default {
  getHostMetrics,
  getHostMetricsHistory,
  getSystemInfo,
  getResourceStatsSummary,
  getContainerMetrics,
  getContainerMetricsHistory,
  createContainerStatsWebSocket
};
