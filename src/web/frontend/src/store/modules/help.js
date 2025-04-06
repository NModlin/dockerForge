/**
 * Vuex store module for the help system
 * Manages help content, tour state, and user preferences for the help system
 */

export const state = {
  helpCenterOpen: false,
  tourInProgress: false,
  tourStep: 0,
  tourCompleted: false,
  lastViewedHelpCategory: 'general',
  contextualHelpContent: {}, // Populated from API
  userHelpPreferences: {
    showHelpTips: true,
    showFeatureDiscovery: true,
    enableContextualHelp: true,
    showTourOnFirstVisit: true
  }
};

export const mutations = {
  SET_HELP_CENTER_OPEN(state, isOpen) {
    state.helpCenterOpen = isOpen;
  },
  SET_TOUR_IN_PROGRESS(state, inProgress) {
    state.tourInProgress = inProgress;
  },
  SET_TOUR_STEP(state, step) {
    state.tourStep = step;
  },
  SET_TOUR_COMPLETED(state, completed) {
    state.tourCompleted = completed;
  },
  SET_LAST_VIEWED_HELP_CATEGORY(state, category) {
    state.lastViewedHelpCategory = category;
  },
  UPDATE_CONTEXTUAL_HELP_CONTENT(state, { context, content }) {
    state.contextualHelpContent = {
      ...state.contextualHelpContent,
      [context]: content
    };
  },
  SET_USER_HELP_PREFERENCES(state, preferences) {
    state.userHelpPreferences = {
      ...state.userHelpPreferences,
      ...preferences
    };
  }
};

export const actions = {
  openHelpCenter({ commit }, category = null) {
    if (category) {
      commit('SET_LAST_VIEWED_HELP_CATEGORY', category);
    }
    commit('SET_HELP_CENTER_OPEN', true);
  },

  closeHelpCenter({ commit }) {
    commit('SET_HELP_CENTER_OPEN', false);
  },

  startTour({ commit }) {
    commit('SET_TOUR_IN_PROGRESS', true);
    commit('SET_TOUR_STEP', 0);
  },

  endTour({ commit }, { completed = false } = {}) {
    commit('SET_TOUR_IN_PROGRESS', false);
    if (completed) {
      commit('SET_TOUR_COMPLETED', true);
    }
  },

  setTourStep({ commit }, step) {
    commit('SET_TOUR_STEP', step);
  },

  async fetchContextualHelp({ commit }, context) {
    try {
      // In a real implementation, this would fetch from an API
      // For now, we'll use a dummy implementation

      // Simulated API delay
      await new Promise(resolve => setTimeout(resolve, 300));

      // Mock data for demonstration
      const mockContent = {
        title: `${context.charAt(0).toUpperCase() + context.slice(1)} Help`,
        content: `Help content for ${context}`,
        tips: [`Tip 1 for ${context}`, `Tip 2 for ${context}`],
        actions: []
      };

      commit('UPDATE_CONTEXTUAL_HELP_CONTENT', {
        context,
        content: mockContent
      });

      return mockContent;
    } catch (error) {
      console.error('Error fetching contextual help:', error);
      return null;
    }
  },

  updateHelpPreferences({ commit }, preferences) {
    // In a real app, we might persist these to the backend
    commit('SET_USER_HELP_PREFERENCES', preferences);

    // Store in localStorage for persistence
    try {
      localStorage.setItem('help_preferences', JSON.stringify(preferences));
    } catch (e) {
      console.error('Failed to store help preferences:', e);
    }
  },

  loadHelpPreferences({ commit }) {
    try {
      const storedPreferences = localStorage.getItem('help_preferences');
      if (storedPreferences) {
        commit('SET_USER_HELP_PREFERENCES', JSON.parse(storedPreferences));
      }
    } catch (e) {
      console.error('Failed to load help preferences:', e);
    }
  }
};

export const getters = {
  isHelpCenterOpen: state => state.helpCenterOpen,
  isTourInProgress: state => state.tourInProgress,
  currentTourStep: state => state.tourStep,
  isTourCompleted: state => state.tourCompleted,
  lastViewedHelpCategory: state => state.lastViewedHelpCategory,
  userHelpPreferences: state => state.userHelpPreferences,

  getContextualHelp: state => context => {
    return state.contextualHelpContent[context] || null;
  },

  shouldShowTourOnFirstVisit: state => {
    return state.userHelpPreferences.showTourOnFirstVisit && !state.tourCompleted;
  },

  showHelpTooltips: state => {
    return state.userHelpPreferences.showHelpTips;
  },

  showFeatureDiscovery: state => {
    return state.userHelpPreferences.showFeatureDiscovery;
  },

  enableContextualHelp: state => {
    return state.userHelpPreferences.enableContextualHelp;
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};
