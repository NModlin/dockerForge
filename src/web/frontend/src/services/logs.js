/**
 * Log service for the DockerForge Web UI.
 * 
 * This service provides functions for interacting with the log API endpoints.
 */
import axios from 'axios';
import store from '@/store';

// API base URL
const API_URL = process.env.VUE_APP_API_URL || '/api';

/**
 * Get logs with optional filtering.
 * 
 * @param {Object} options - Options for the request
 * @param {number} options.skip - Number of records to skip
 * @param {number} options.limit - Maximum number of records to return
 * @param {Array<string>} options.source - Filter by source
 * @param {Array<string>} options.sourceId - Filter by source ID
 * @param {Array<string>} options.sourceName - Filter by source name
 * @param {Array<string>} options.level - Filter by log level
 * @param {string} options.messageContains - Filter by message content
 * @param {string} options.messageRegex - Filter by message regex
 * @param {string} options.startTime - Filter by start time (ISO format)
 * @param {string} options.endTime - Filter by end time (ISO format)
 * @param {string} options.stream - Filter by stream (for containers)
 * @returns {Promise<Array>} Logs
 */
export async function getLogs(options = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs`, {
    params: {
      skip: options.skip || 0,
      limit: options.limit || 100,
      source: options.source,
      source_id: options.sourceId,
      source_name: options.sourceName,
      level: options.level,
      message_contains: options.messageContains,
      message_regex: options.messageRegex,
      start_time: options.startTime,
      end_time: options.endTime,
      stream: options.stream
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get logs for a specific container directly from Docker.
 * 
 * @param {string} containerId - Container ID
 * @param {Object} options - Options for the request
 * @param {number} options.tail - Number of lines to return from the end of the logs
 * @param {string} options.since - Only return logs since this timestamp (ISO format)
 * @param {string} options.until - Only return logs before this timestamp (ISO format)
 * @param {string} options.stream - Stream to filter by (stdout, stderr, or both)
 * @param {boolean} options.follow - Whether to follow the logs (stream updates)
 * @returns {Promise<Array>} Container logs
 */
export async function getContainerLogs(containerId, options = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs/containers/${containerId}`, {
    params: {
      tail: options.tail || 100,
      since: options.since,
      until: options.until,
      stream: options.stream,
      follow: options.follow || false
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get logs for multiple containers.
 * 
 * @param {Array<string>} containerIds - List of container IDs
 * @param {Object} options - Options for the request
 * @param {number} options.tail - Number of lines to return from the end of the logs
 * @param {string} options.since - Only return logs since this timestamp (ISO format)
 * @param {string} options.until - Only return logs before this timestamp (ISO format)
 * @param {string} options.stream - Stream to filter by (stdout, stderr, or both)
 * @param {string} options.messageContains - Only return logs containing this string
 * @param {string} options.messageRegex - Only return logs matching this regex
 * @returns {Promise<Array>} Container logs
 */
export async function getMultiContainerLogs(containerIds, options = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs/multi-container`, {
    params: {
      container_ids: containerIds,
      tail: options.tail || 100,
      since: options.since,
      until: options.until,
      stream: options.stream,
      message_contains: options.messageContains,
      message_regex: options.messageRegex
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Get log statistics.
 * 
 * @param {Object} options - Options for the request
 * @param {number} options.days - Number of days to include in statistics
 * @param {Array<string>} options.source - Filter by source
 * @param {Array<string>} options.sourceId - Filter by source ID
 * @param {Array<string>} options.sourceName - Filter by source name
 * @param {Array<string>} options.level - Filter by log level
 * @param {string} options.messageContains - Filter by message content
 * @param {string} options.messageRegex - Filter by message regex
 * @param {string} options.stream - Filter by stream (for containers)
 * @returns {Promise<Object>} Log statistics
 */
export async function getLogStatistics(options = {}) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs/statistics`, {
    params: {
      days: options.days || 7,
      source: options.source,
      source_id: options.sourceId,
      source_name: options.sourceName,
      level: options.level,
      message_contains: options.messageContains,
      message_regex: options.messageRegex,
      stream: options.stream
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Export logs in the specified format.
 * 
 * @param {Object} filter - Log filter parameters
 * @param {string} format - Export format (json, csv, text)
 * @returns {Promise<Blob>} Exported logs as a Blob
 */
export async function exportLogs(filter, format = 'json') {
  const token = store.getters['auth/token'];
  
  const response = await axios.post(`${API_URL}/monitoring/logs/export`, 
    {
      filter,
      format
    },
    {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'blob'
    }
  );
  
  return response.data;
}

/**
 * Get log aggregation settings.
 * 
 * @returns {Promise<Object>} Log aggregation settings
 */
export async function getLogAggregationSettings() {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs/settings`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Update log aggregation settings.
 * 
 * @param {Object} settings - Log aggregation settings
 * @returns {Promise<Object>} Updated log aggregation settings
 */
export async function updateLogAggregationSettings(settings) {
  const token = store.getters['auth/token'];
  
  const response = await axios.put(`${API_URL}/monitoring/logs/settings`, settings, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}

/**
 * Analyze logs for a container.
 * 
 * @param {string} containerId - Container ID
 * @param {number} hours - Number of hours to analyze
 * @param {boolean} includePatterns - Whether to include pattern matching
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeLogs(containerId, hours = 24, includePatterns = true) {
  const token = store.getters['auth/token'];
  
  const response = await axios.get(`${API_URL}/monitoring/logs/analyze/${containerId}`, {
    params: {
      hours,
      include_patterns: includePatterns
    },
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.data;
}
