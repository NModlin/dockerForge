// Chat store module for DockerForge AI Assistant
import axios from 'axios';
import websocketService from '@/services/websocketService';

export default {
  namespaced: true,
  state: {
    messages: [
      // Default welcome message
      {
        type: 'ai',
        text: 'Hello! I\'m your DockerForge AI assistant. How can I help you with your Docker containers today?',
        timestamp: new Date().toISOString()
      }
    ],
    isActive: false,
    loading: false,
    error: null,
    // Context stores information about the current user context (which page they're on, what container they're looking at, etc.)
    context: {
      currentPage: null,
      currentContainerId: null,
      currentImageId: null
    },
    // Chat session management
    currentSession: null,
    sessions: [],
    suggestions: [],
    
    // Phase 7: User preferences
    userPreferences: {
      response_style: 'balanced',
      auto_suggestions: true,
      preferred_topics: [],
      avoided_topics: []
    },
    
    // Phase 7: Feedback tracking
    messageFeedback: {}, // Map of message_id -> feedback object
    
    // Phase 7: Command shortcuts
    commandShortcuts: [], // List of command shortcuts
    
    // Phase 7: Conversation memory tracking
    relevantMemories: [], // Recent relevant memories for current conversation
    
    // Phase 8: WebSocket related state
    typingStatus: {}, // Map of userId -> boolean indicating typing status
    streamingMessages: {}, // Map of messageId -> streaming message state
    messageReadStatus: {}, // Map of messageId -> array of userIds who read it
    activeTasks: {}, // Map of taskId -> task status information
    websocketConnected: false // Whether the WebSocket connection is established
  },

  mutations: {
    ADD_MESSAGE(state, message) {
      state.messages.push(message);
      // Save to localStorage for persistence
      localStorage.setItem('chatMessages', JSON.stringify(state.messages));
    },

    SET_MESSAGES(state, messages) {
      state.messages = messages;
      // Save to localStorage for persistence
      localStorage.setItem('chatMessages', JSON.stringify(state.messages));
    },

    CLEAR_MESSAGES(state) {
      // Keep the welcome message
      state.messages = [
        {
          type: 'ai',
          text: 'Hello! I\'m your DockerForge AI assistant. How can I help you with your Docker containers today?',
          timestamp: new Date().toISOString()
        }
      ];
      localStorage.setItem('chatMessages', JSON.stringify(state.messages));
    },

    SET_ACTIVE(state, isActive) {
      state.isActive = isActive;
      localStorage.setItem('chatSidebarOpen', isActive ? 'true' : 'false');
    },

    SET_LOADING(state, loading) {
      state.loading = loading;
    },

    SET_ERROR(state, error) {
      state.error = error;
    },

    UPDATE_CONTEXT(state, contextData) {
      state.context = { ...state.context, ...contextData };
    },

    SET_CURRENT_SESSION(state, session) {
      state.currentSession = session;
      localStorage.setItem('currentChatSession', JSON.stringify(session));
    },

    SET_SESSIONS(state, sessions) {
      state.sessions = sessions;
    },

    SET_SUGGESTIONS(state, suggestions) {
      state.suggestions = suggestions;
    },
    
    // Phase 7: New mutations
    SET_USER_PREFERENCES(state, preferences) {
      state.userPreferences = preferences;
      localStorage.setItem('chatUserPreferences', JSON.stringify(preferences));
    },
    
    UPDATE_USER_PREFERENCES(state, preferencesData) {
      state.userPreferences = { ...state.userPreferences, ...preferencesData };
      localStorage.setItem('chatUserPreferences', JSON.stringify(state.userPreferences));
    },
    
    SET_MESSAGE_FEEDBACK(state, { messageId, feedback }) {
      state.messageFeedback = { 
        ...state.messageFeedback, 
        [messageId]: feedback 
      };
    },
    
    SET_COMMAND_SHORTCUTS(state, shortcuts) {
      state.commandShortcuts = shortcuts;
    },
    
    ADD_COMMAND_SHORTCUT(state, shortcut) {
      state.commandShortcuts.push(shortcut);
    },
    
    REMOVE_COMMAND_SHORTCUT(state, shortcutId) {
      state.commandShortcuts = state.commandShortcuts.filter(
        shortcut => shortcut.id !== shortcutId
      );
    },
    
    SET_RELEVANT_MEMORIES(state, memories) {
      state.relevantMemories = memories;
    },
    
    // Phase 8: WebSocket related mutations
    SET_WEBSOCKET_CONNECTED(state, isConnected) {
      state.websocketConnected = isConnected;
    },
    
    SET_TYPING_STATUS(state, { userId, isTyping, sessionId }) {
      state.typingStatus = { 
        ...state.typingStatus,
        [userId]: { isTyping, sessionId, timestamp: new Date().toISOString() }
      };
    },
    
    INIT_STREAMING_MESSAGE(state, { messageId, initialText }) {
      state.streamingMessages = {
        ...state.streamingMessages,
        [messageId]: {
          text: initialText || '',
          isComplete: false,
          chunks: [],
          startTime: new Date().toISOString()
        }
      };
    },
    
    ADD_MESSAGE_CHUNK(state, { messageId, chunk, isLast }) {
      if (!state.streamingMessages[messageId]) {
        // Initialize if not exists
        state.streamingMessages[messageId] = {
          text: '',
          isComplete: false,
          chunks: [],
          startTime: new Date().toISOString()
        };
      }
      
      // Add chunk to message
      const streamingMessage = state.streamingMessages[messageId];
      streamingMessage.chunks.push(chunk);
      streamingMessage.text += chunk;
      
      // If this is the last chunk, mark as complete
      if (isLast) {
        streamingMessage.isComplete = true;
        streamingMessage.endTime = new Date().toISOString();
        
        // Update the corresponding message in the messages array
        const messageIndex = state.messages.findIndex(m => m.id === messageId);
        if (messageIndex >= 0) {
          state.messages[messageIndex].text = streamingMessage.text;
        }
      }
    },
    
    SET_MESSAGE_READ(state, { messageId, userId, timestamp }) {
      // Initialize if needed
      if (!state.messageReadStatus[messageId]) {
        state.messageReadStatus[messageId] = [];
      }
      
      // Add user to read status if not already there
      if (!state.messageReadStatus[messageId].some(read => read.userId === userId)) {
        state.messageReadStatus[messageId].push({
          userId,
          timestamp
        });
      }
    },
    
    SET_TASK_STATUS(state, { taskId, status, progress, message, data }) {
      state.activeTasks = {
        ...state.activeTasks,
        [taskId]: {
          status,
          progress,
          message,
          data: data || {},
          updatedAt: new Date().toISOString()
        }
      };
      
      // Remove completed tasks after a delay
      if (status === 'complete' || status === 'failed') {
        setTimeout(() => {
          state.activeTasks = Object.entries(state.activeTasks)
            .filter(([id]) => id !== taskId)
            .reduce((obj, [id, value]) => {
              obj[id] = value;
              return obj;
            }, {});
        }, 30000); // Remove after 30 seconds
      }
    }
  },

  actions: {
    // Initialize the chat module from localStorage
    init({ commit, dispatch }) {
      // Restore chat messages from localStorage for backwards compatibility
      const savedMessages = localStorage.getItem('chatMessages');
      if (savedMessages) {
        commit('SET_MESSAGES', JSON.parse(savedMessages));
      }

      // Restore chat sidebar state
      const sidebarOpen = localStorage.getItem('chatSidebarOpen');
      if (sidebarOpen === 'true') {
        commit('SET_ACTIVE', true);
      }

      // Try to restore current session
      const savedSession = localStorage.getItem('currentChatSession');
      if (savedSession) {
        try {
          const session = JSON.parse(savedSession);
          commit('SET_CURRENT_SESSION', session);
          
          // Load the messages for this session from the API
          dispatch('loadSession', session.id);
        } catch (e) {
          console.error('Error restoring chat session:', e);
        }
      }
      
      // Load available sessions
      dispatch('loadSessions');
      
      // Phase 7: Load user preferences
      dispatch('loadUserPreferences');
      
      // Phase 7: Load command shortcuts
      dispatch('loadCommandShortcuts');
    },

    // Load chat sessions
    async loadSessions({ commit }) {
      try {
        const response = await axios.get('/api/chat/sessions');
        commit('SET_SESSIONS', response.data.sessions);
      } catch (error) {
        console.error('Error loading chat sessions:', error);
      }
    },

    // Load a specific chat session
    async loadSession({ commit }, sessionId) {
      try {
        const response = await axios.get(`/api/chat/sessions/${sessionId}`);
        commit('SET_CURRENT_SESSION', response.data);
        commit('SET_MESSAGES', response.data.messages);
      } catch (error) {
        console.error(`Error loading chat session ${sessionId}:`, error);
      }
    },

    // Create a new chat session
    async createSession({ commit }) {
      try {
        const response = await axios.post('/api/chat/sessions', {
          title: `Chat ${new Date().toLocaleDateString()}`
        });
        commit('SET_CURRENT_SESSION', response.data);
        commit('SET_MESSAGES', response.data.messages);
        return response.data;
      } catch (error) {
        console.error('Error creating chat session:', error);
        throw error;
      }
    },

    // Add a new user message and get AI response
    async sendMessage({ commit, state, dispatch }, messageText) {
      // Check if we have a current session
      if (!state.currentSession) {
        try {
          // Create a new session first
          await dispatch('createSession');
        } catch (error) {
          console.error('Failed to create a new chat session:', error);
          commit('SET_ERROR', 'Failed to start a new chat session.');
          return;
        }
      }
      
      // Create user message for UI display
      const userMessage = {
        type: 'user',
        text: messageText,
        timestamp: new Date().toISOString(),
        session_id: state.currentSession.id
      };
      
      // Add user message to state
      commit('ADD_MESSAGE', userMessage);
      
      // Set loading state
      commit('SET_LOADING', true);
      
      try {
        // Convert context to the format expected by the API
        const contextData = {
          current_page: state.context.currentPage,
          current_container_id: state.context.currentContainerId,
          current_image_id: state.context.currentImageId
        };
        
        // Send message to API
        const response = await axios.post('/api/chat/messages', {
          text: messageText,
          session_id: state.currentSession.id,
          context: contextData
        });
        
        // Extract the AI response
        const aiResponse = response.data.message;
        
        // Add AI response to the UI state
        commit('ADD_MESSAGE', {
          id: aiResponse.id,
          type: aiResponse.type,
          text: aiResponse.text,
          timestamp: aiResponse.timestamp,
          session_id: aiResponse.session_id
        });
        
        // Store suggestions if available
        if (response.data.suggestions && response.data.suggestions.length > 0) {
          commit('SET_SUGGESTIONS', response.data.suggestions);
        }
        
        // Phase 7: Process enhanced response data
        if (response.data.user_preferences) {
          commit('SET_USER_PREFERENCES', response.data.user_preferences);
        }
        
        if (response.data.command_shortcuts) {
          commit('SET_COMMAND_SHORTCUTS', response.data.command_shortcuts);
        }
        
        // Phase 7: Get relevant memories for the current conversation
        dispatch('getRelevantMemories', messageText);
      } catch (error) {
        console.error('Error sending message to API:', error);
        commit('SET_ERROR', 'Failed to get a response. Please try again.');
        
        // Add error message
        commit('ADD_MESSAGE', {
          type: 'system',
          text: 'Sorry, I encountered an error while processing your message. The chat service might be unavailable.',
          timestamp: new Date().toISOString()
        });
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // Toggle the chat sidebar
    toggleChat({ commit, state }) {
      commit('SET_ACTIVE', !state.isActive);
    },

    // Update the current user context
    updateContext({ commit }, contextData) {
      commit('UPDATE_CONTEXT', contextData);
    },

    // Clear all messages and start a new session
    async clearChat({ commit, dispatch }) {
      // Reset UI state first
      commit('CLEAR_MESSAGES');
      commit('SET_SUGGESTIONS', []);
      
      try {
        // Create a new session
        await dispatch('createSession');
      } catch (error) {
        console.error('Failed to create a new chat session after clear:', error);
      }
    },
    
    // Switch to a different chat session
    async switchSession({ commit, dispatch }, sessionId) {
      try {
        await dispatch('loadSession', sessionId);
      } catch (error) {
        console.error(`Error switching to session ${sessionId}:`, error);
        commit('SET_ERROR', 'Failed to switch chat sessions.');
      }
    },
    
    // Delete a chat session
    async deleteSession({ commit, dispatch, state }, sessionId) {
      try {
        await axios.delete(`/api/chat/sessions/${sessionId}`);
        
        // If we deleted the current session, create a new one
        if (state.currentSession && state.currentSession.id === sessionId) {
          await dispatch('createSession');
        }
        
        // Refresh the sessions list
        dispatch('loadSessions');
      } catch (error) {
        console.error(`Error deleting session ${sessionId}:`, error);
        commit('SET_ERROR', 'Failed to delete chat session.');
      }
    },
    
    // Phase 7: Load user preferences
    async loadUserPreferences({ commit }) {
      try {
        // First, try to load from localStorage for faster startup
        const savedPreferences = localStorage.getItem('chatUserPreferences');
        if (savedPreferences) {
          commit('SET_USER_PREFERENCES', JSON.parse(savedPreferences));
        }
        
        // Then, fetch from API to get the latest
        const response = await axios.get('/api/chat/preferences');
        commit('SET_USER_PREFERENCES', response.data);
      } catch (error) {
        console.error('Error loading user preferences:', error);
      }
    },
    
    // Phase 7: Update user preferences
    async updateUserPreferences({ commit }, preferencesData) {
      try {
        const response = await axios.put('/api/chat/preferences', preferencesData);
        commit('SET_USER_PREFERENCES', response.data);
        return response.data;
      } catch (error) {
        console.error('Error updating user preferences:', error);
        throw error;
      }
    },
    
    // Phase 7: Submit message feedback
    async submitMessageFeedback({ commit }, { messageId, rating, feedbackText }) {
      try {
        const response = await axios.post('/api/chat/feedback', {
          message_id: messageId,
          rating,
          feedback_text: feedbackText
        });
        
        commit('SET_MESSAGE_FEEDBACK', {
          messageId,
          feedback: {
            id: response.data.id,
            rating,
            feedback_text: feedbackText,
            created_at: response.data.created_at
          }
        });
        
        return response.data;
      } catch (error) {
        console.error('Error submitting feedback:', error);
        throw error;
      }
    },
    
    // Phase 7: Update message feedback (for component updates)
    updateMessageFeedback({ commit }, { messageId, feedback }) {
      commit('SET_MESSAGE_FEEDBACK', { messageId, feedback });
    },
    
    // Phase 7: Load command shortcuts
    async loadCommandShortcuts({ commit }) {
      try {
        const response = await axios.get('/api/chat/shortcuts');
        commit('SET_COMMAND_SHORTCUTS', response.data.shortcuts);
      } catch (error) {
        console.error('Error loading command shortcuts:', error);
      }
    },
    
    // Phase 7: Create command shortcut
    async createCommandShortcut({ commit }, shortcutData) {
      try {
        const response = await axios.post('/api/chat/shortcuts', shortcutData);
        commit('ADD_COMMAND_SHORTCUT', response.data);
        return response.data;
      } catch (error) {
        console.error('Error creating command shortcut:', error);
        throw error;
      }
    },
    
    // Phase 7: Delete command shortcut
    async deleteCommandShortcut({ commit }, shortcutId) {
      try {
        await axios.delete(`/api/chat/shortcuts/${shortcutId}`);
        commit('REMOVE_COMMAND_SHORTCUT', shortcutId);
      } catch (error) {
        console.error(`Error deleting shortcut ${shortcutId}:`, error);
        throw error;
      }
    },
    
    // Phase 7: Use command shortcut
    async useCommandShortcut({ commit }, command) {
      try {
        const response = await axios.post('/api/chat/shortcuts/use', { command });
        return response.data.shortcut;
      } catch (error) {
        console.error('Error using command shortcut:', error);
        throw error;
      }
    },
    
    // Phase 7: Get relevant memories for the current conversation
    async getRelevantMemories({ commit, state }, query) {
      try {
        // Only proceed if we have a query
        if (!query) return;
        
        // Convert context to JSON string
        const contextStr = JSON.stringify({
          current_page: state.context.currentPage,
          current_container_id: state.context.currentContainerId,
          current_image_id: state.context.currentImageId
        });
        
        const response = await axios.get('/api/chat/memory', {
          params: {
            query,
            context: contextStr,
            limit: 5
          }
        });
        
        commit('SET_RELEVANT_MEMORIES', response.data);
      } catch (error) {
        console.error('Error fetching relevant memories:', error);
      }
    },
    
    // Phase 8: WebSocket-related actions
    
    // Initialize WebSocket connection
    initWebSocket({ commit, state, dispatch }) {
      try {
        // Get user ID (use 'anonymous' if not available)
        const userId = state.currentSession?.user_id || 'anonymous';
        
        // Initialize WebSocket connection
        websocketService.init(userId);
        
        // Subscribe to current session if available
        if (state.currentSession) {
          websocketService.subscribeToSession(state.currentSession.id);
        }
        
        commit('SET_WEBSOCKET_CONNECTED', true);
      } catch (error) {
        console.error('Error initializing WebSocket:', error);
        commit('SET_WEBSOCKET_CONNECTED', false);
      }
    },
    
    // Close WebSocket connection
    closeWebSocket({ commit }) {
      try {
        websocketService.disconnect();
        commit('SET_WEBSOCKET_CONNECTED', false);
      } catch (error) {
        console.error('Error closing WebSocket:', error);
      }
    },
    
    // Subscribe to a chat session
    subscribeToSession({ state }, sessionId) {
      if (state.websocketConnected) {
        websocketService.subscribeToSession(sessionId);
      }
    },
    
    // Unsubscribe from a chat session
    unsubscribeFromSession({ state }, sessionId) {
      if (state.websocketConnected) {
        websocketService.unsubscribeFromSession(sessionId);
      }
    },
    
    // Set typing status
    setTypingStatus({ state }, { isTyping, sessionId }) {
      if (state.websocketConnected && sessionId) {
        websocketService.updateTypingStatus(isTyping, sessionId);
      }
    },
    
    // Send read receipt for a message
    sendReadReceipt({ state }, { messageId, sessionId }) {
      if (state.websocketConnected && messageId && sessionId) {
        websocketService.sendReadReceipt(messageId, sessionId);
      }
    },
    
    // Handle message chunk from WebSocket
    handleMessageChunk({ commit, state }, message) {
      // Extract message data
      const { message_id, chunk, is_first, is_last } = message;
      
      // Initialize streaming message if this is the first chunk
      if (is_first) {
        commit('INIT_STREAMING_MESSAGE', { 
          messageId: message_id,
          initialText: chunk
        });
      }
      
      // Add chunk to message
      commit('ADD_MESSAGE_CHUNK', {
        messageId: message_id,
        chunk,
        isLast: is_last
      });
    },
    
    // Update task status
    updateTaskStatus({ commit }, message) {
      commit('SET_TASK_STATUS', {
        taskId: message.task_id,
        status: message.status,
        progress: message.progress,
        message: message.message,
        data: message.data
      });
    }
  },

  getters: {
    messages: state => state.messages,
    isActive: state => state.isActive,
    isLoading: state => state.loading,
    error: state => state.error,
    context: state => state.context,
    currentSession: state => state.currentSession,
    sessions: state => state.sessions,
    suggestions: state => state.suggestions,
    
    // Phase 7: New getters
    userPreferences: state => state.userPreferences,
    messageFeedback: state => state.messageFeedback,
    getFeedbackForMessage: state => messageId => state.messageFeedback[messageId] || null,
    commandShortcuts: state => state.commandShortcuts,
    relevantMemories: state => state.relevantMemories,
    
    // Phase 8: WebSocket-related getters
    isWebSocketConnected: state => state.websocketConnected,
    
    // Get typing status for a specific user in a specific session
    getTypingStatus: state => (userId, sessionId) => {
      const status = state.typingStatus[userId];
      return status && status.sessionId === sessionId ? status.isTyping : false;
    },
    
    // Get all users typing in a specific session
    getUsersTypingInSession: state => sessionId => {
      return Object.entries(state.typingStatus)
        .filter(([, status]) => status.isTyping && status.sessionId === sessionId)
        .map(([userId]) => userId);
    },
    
    // Get streaming message data
    getStreamingMessage: state => messageId => state.streamingMessages[messageId] || null,
    
    // Check if a message is currently streaming
    isMessageStreaming: state => messageId => {
      const msg = state.streamingMessages[messageId];
      return msg && !msg.isComplete;
    },
    
    // Get read status for a message
    getMessageReadStatus: state => messageId => state.messageReadStatus[messageId] || [],
    
    // Get active tasks
    activeTasks: state => state.activeTasks,
    
    // Get task by ID
    getTaskById: state => taskId => state.activeTasks[taskId] || null
  }
};
