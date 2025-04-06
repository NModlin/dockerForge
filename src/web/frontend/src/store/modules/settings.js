/**
 * Vuex store module for application settings
 * Manages user preferences, theme settings, and application configuration
 */
import axios from 'axios';

// Initial state
export const state = {
  loading: false,
  error: null,
  // User preferences
  userPreferences: {
    theme: localStorage.getItem('theme') || 'light',
    language: localStorage.getItem('language') || 'en',
    dateFormat: localStorage.getItem('dateFormat') || 'MM/DD/YYYY',
    timeFormat: localStorage.getItem('timeFormat') || '24h',
    notifications: {
      enabled: localStorage.getItem('notifications_enabled') !== 'false',
      desktop: localStorage.getItem('notifications_desktop') !== 'false',
      email: localStorage.getItem('notifications_email') === 'true',
      emailAddress: localStorage.getItem('notifications_email_address') || '',
      events: JSON.parse(localStorage.getItem('notifications_events') || '["error", "security"]')
    },
    display: {
      compactView: localStorage.getItem('display_compact') === 'true',
      showSystemContainers: localStorage.getItem('display_system_containers') === 'true',
      refreshInterval: parseInt(localStorage.getItem('display_refresh_interval') || '30', 10),
      defaultPage: localStorage.getItem('display_default_page') || 'dashboard'
    },
    keyboard: {
      enableShortcuts: localStorage.getItem('keyboard_shortcuts') !== 'false',
      customShortcuts: JSON.parse(localStorage.getItem('keyboard_custom_shortcuts') || '{}')
    }
  },
  // Application settings
  appSettings: {
    darkMode: localStorage.getItem('darkMode') !== 'false',
    apiRateLimit: 60,
    sessionTimeout: 30,
    telemetryEnabled: localStorage.getItem('telemetry_enabled') !== 'false',
    debugMode: localStorage.getItem('debug_mode') === 'true',
    logLevel: localStorage.getItem('log_level') || 'info'
  }
};

// Getters
export const getters = {
  getUserPreferences: (state) => state.userPreferences,
  getTheme: (state) => state.userPreferences.theme,
  getLanguage: (state) => state.userPreferences.language,
  getDateFormat: (state) => state.userPreferences.dateFormat,
  getTimeFormat: (state) => state.userPreferences.timeFormat,
  getNotificationSettings: (state) => state.userPreferences.notifications,
  getDisplaySettings: (state) => state.userPreferences.display,
  getKeyboardSettings: (state) => state.userPreferences.keyboard,
  getAppSettings: (state) => state.appSettings,
  isDarkMode: (state) => state.appSettings.darkMode,
  isDebugMode: (state) => state.appSettings.debugMode,
  getLogLevel: (state) => state.appSettings.logLevel,
  isTelemetryEnabled: (state) => state.appSettings.telemetryEnabled
};

// Mutations
export const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_USER_PREFERENCES(state, preferences) {
    state.userPreferences = { ...state.userPreferences, ...preferences };

    // Store in localStorage for persistence
    if (preferences.theme) localStorage.setItem('theme', preferences.theme);
    if (preferences.language) localStorage.setItem('language', preferences.language);
    if (preferences.dateFormat) localStorage.setItem('dateFormat', preferences.dateFormat);
    if (preferences.timeFormat) localStorage.setItem('timeFormat', preferences.timeFormat);

    // Store notification settings
    if (preferences.notifications) {
      const { notifications } = preferences;
      if (notifications.enabled !== undefined) localStorage.setItem('notifications_enabled', notifications.enabled);
      if (notifications.desktop !== undefined) localStorage.setItem('notifications_desktop', notifications.desktop);
      if (notifications.email !== undefined) localStorage.setItem('notifications_email', notifications.email);
      if (notifications.emailAddress) localStorage.setItem('notifications_email_address', notifications.emailAddress);
      if (notifications.events) localStorage.setItem('notifications_events', JSON.stringify(notifications.events));
    }

    // Store display settings
    if (preferences.display) {
      const { display } = preferences;
      if (display.compactView !== undefined) localStorage.setItem('display_compact', display.compactView);
      if (display.showSystemContainers !== undefined) localStorage.setItem('display_system_containers', display.showSystemContainers);
      if (display.refreshInterval) localStorage.setItem('display_refresh_interval', display.refreshInterval);
      if (display.defaultPage) localStorage.setItem('display_default_page', display.defaultPage);
    }

    // Store keyboard settings
    if (preferences.keyboard) {
      const { keyboard } = preferences;
      if (keyboard.enableShortcuts !== undefined) localStorage.setItem('keyboard_shortcuts', keyboard.enableShortcuts);
      if (keyboard.customShortcuts) localStorage.setItem('keyboard_custom_shortcuts', JSON.stringify(keyboard.customShortcuts));
    }
  },
  UPDATE_NOTIFICATION_SETTINGS(state, settings) {
    state.userPreferences.notifications = { ...state.userPreferences.notifications, ...settings };

    // Store in localStorage
    if (settings.enabled !== undefined) localStorage.setItem('notifications_enabled', settings.enabled);
    if (settings.desktop !== undefined) localStorage.setItem('notifications_desktop', settings.desktop);
    if (settings.email !== undefined) localStorage.setItem('notifications_email', settings.email);
    if (settings.emailAddress) localStorage.setItem('notifications_email_address', settings.emailAddress);
    if (settings.events) localStorage.setItem('notifications_events', JSON.stringify(settings.events));
  },
  UPDATE_DISPLAY_SETTINGS(state, settings) {
    state.userPreferences.display = { ...state.userPreferences.display, ...settings };

    // Store in localStorage
    if (settings.compactView !== undefined) localStorage.setItem('display_compact', settings.compactView);
    if (settings.showSystemContainers !== undefined) localStorage.setItem('display_system_containers', settings.showSystemContainers);
    if (settings.refreshInterval) localStorage.setItem('display_refresh_interval', settings.refreshInterval);
    if (settings.defaultPage) localStorage.setItem('display_default_page', settings.defaultPage);
  },
  UPDATE_KEYBOARD_SETTINGS(state, settings) {
    state.userPreferences.keyboard = { ...state.userPreferences.keyboard, ...settings };

    // Store in localStorage
    if (settings.enableShortcuts !== undefined) localStorage.setItem('keyboard_shortcuts', settings.enableShortcuts);
    if (settings.customShortcuts) localStorage.setItem('keyboard_custom_shortcuts', JSON.stringify(settings.customShortcuts));
  },
  SET_APP_SETTINGS(state, settings) {
    state.appSettings = { ...state.appSettings, ...settings };

    // Store in localStorage
    if (settings.darkMode !== undefined) localStorage.setItem('darkMode', settings.darkMode);
    if (settings.telemetryEnabled !== undefined) localStorage.setItem('telemetry_enabled', settings.telemetryEnabled);
    if (settings.debugMode !== undefined) localStorage.setItem('debug_mode', settings.debugMode);
    if (settings.logLevel) localStorage.setItem('log_level', settings.logLevel);
  }
};

// Actions
export const actions = {
  async fetchUserPreferences({ commit }) {
    commit('SET_LOADING', true);

    try {
      const response = await axios.get('/api/user-preferences');
      commit('SET_USER_PREFERENCES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch user preferences');
      console.error('Error fetching user preferences:', error);
      // Fall back to localStorage values (already in state)
      return state.userPreferences;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async saveUserPreferences({ commit }, preferences) {
    commit('SET_LOADING', true);

    try {
      const response = await axios.put('/api/user-preferences', preferences);
      commit('SET_USER_PREFERENCES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to save user preferences');
      console.error('Error saving user preferences:', error);

      // Still update local state and localStorage for offline functionality
      commit('SET_USER_PREFERENCES', preferences);
      return preferences;
    } finally {
      commit('SET_LOADING', false);
    }
  },

  async updateNotificationSettings({ commit, dispatch }, settings) {
    commit('UPDATE_NOTIFICATION_SETTINGS', settings);

    try {
      // Update on the server
      await axios.put('/api/user-preferences', { notifications: settings });
    } catch (error) {
      console.error('Error updating notification settings:', error);
      // Continue with local update even if server update fails
    }
  },

  async updateDisplaySettings({ commit, dispatch }, settings) {
    commit('UPDATE_DISPLAY_SETTINGS', settings);

    try {
      // Update on the server
      await axios.put('/api/user-preferences', { display: settings });
    } catch (error) {
      console.error('Error updating display settings:', error);
      // Continue with local update even if server update fails
    }
  },

  async updateKeyboardSettings({ commit, dispatch }, settings) {
    commit('UPDATE_KEYBOARD_SETTINGS', settings);

    try {
      // Update on the server
      await axios.put('/api/user-preferences', { keyboard: settings });
    } catch (error) {
      console.error('Error updating keyboard settings:', error);
      // Continue with local update even if server update fails
    }
  },

  async saveAppSettings({ commit }, settings) {
    commit('SET_APP_SETTINGS', settings);

    // Sync dark mode with the root store
    if (settings.darkMode !== undefined) {
      commit('SET_DARK_MODE', settings.darkMode, { root: true });
    }

    // In a real implementation, this would also call the API
    // This is handled in the mutation for now
  },

  async resetUserPreferences({ commit }) {
    commit('SET_LOADING', true);

    try {
      // Reset preferences on the server
      const response = await axios.post('/api/user-preferences/reset');
      commit('SET_USER_PREFERENCES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to reset user preferences');
      console.error('Error resetting user preferences:', error);

      // Fall back to default preferences if server reset fails
      const defaultPreferences = {
        theme: 'light',
        language: 'en',
        dateFormat: 'MM/DD/YYYY',
        timeFormat: '24h',
        notifications: {
          enabled: true,
          desktop: true,
          email: false,
          emailAddress: '',
          events: ['error', 'security']
        },
        display: {
          compactView: false,
          showSystemContainers: false,
          refreshInterval: 30,
          defaultPage: 'dashboard'
        },
        keyboard: {
          enableShortcuts: true,
          customShortcuts: {}
        }
      };

      commit('SET_USER_PREFERENCES', defaultPreferences);
      return defaultPreferences;
    } finally {
      commit('SET_LOADING', false);
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
