/**
 * WebSocket service for real-time chat functionality
 */
import { io } from 'socket.io-client';
import store from '../store';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.reconnectionAttempts = 0;
    this.maxReconnectionAttempts = 5;
    this.userId = 'anonymous'; // Default user ID
    this.activeSubscriptions = new Set();
  }

  /**
   * Initialize the WebSocket connection
   * @param {string} userId - User ID for the connection
   */
  init(userId = 'anonymous') {
    if (this.socket) {
      this.disconnect();
    }

    this.userId = userId;

    // Determine the WebSocket URL based on the current environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${userId}`;

    // Create WebSocket connection
    this.socket = new WebSocket(wsUrl);

    // Set up event handlers
    this.socket.onopen = this.onOpen.bind(this);
    this.socket.onclose = this.onClose.bind(this);
    this.socket.onerror = this.onError.bind(this);
    this.socket.onmessage = this.onMessage.bind(this);

    console.log(`WebSocket connecting to ${wsUrl}`);
  }

  /**
   * Handle WebSocket open event
   */
  onOpen() {
    console.log('WebSocket connection established');
    this.connected = true;
    this.reconnectionAttempts = 0;

    // Resubscribe to any active sessions
    this.resubscribeToSessions();

    // Start ping interval to keep connection alive
    this.startPingInterval();
  }

  /**
   * Handle WebSocket close event
   * @param {Event} event - Close event
   */
  onClose(event) {
    console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
    this.connected = false;
    this.clearPingInterval();

    // Attempt to reconnect if not a normal closure
    if (event.code !== 1000 && this.reconnectionAttempts < this.maxReconnectionAttempts) {
      this.reconnectionAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectionAttempts), 30000);
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectionAttempts})`);
      
      setTimeout(() => {
        this.init(this.userId);
      }, delay);
    }
  }

  /**
   * Handle WebSocket error event
   * @param {Event} error - Error event
   */
  onError(error) {
    console.error('WebSocket error:', error);
  }

  /**
   * Handle WebSocket message event
   * @param {MessageEvent} event - Message event
   */
  onMessage(event) {
    try {
      const message = JSON.parse(event.data);
      console.log('WebSocket message received:', message);

      // Process different message types
      switch (message.type) {
        case 'connection_established':
          this.handleConnectionEstablished(message);
          break;
        case 'chat_message':
          this.handleChatMessage(message);
          break;
        case 'message_chunk':
          this.handleMessageChunk(message);
          break;
        case 'typing_status':
          this.handleTypingStatus(message);
          break;
        case 'read_receipt':
          this.handleReadReceipt(message);
          break;
        case 'task_update':
          this.handleTaskUpdate(message);
          break;
        case 'pong':
          // Pong response to our ping, nothing to do
          break;
        case 'error':
          console.error('WebSocket error from server:', message.error);
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Send a message through the WebSocket connection
   * @param {Object} data - Data to send
   * @returns {boolean} - Whether the message was sent
   */
  send(data) {
    if (!this.connected || !this.socket) {
      console.warn('Cannot send message: WebSocket not connected');
      return false;
    }

    try {
      this.socket.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Disconnect the WebSocket connection
   */
  disconnect() {
    if (this.socket) {
      this.clearPingInterval();
      this.socket.close();
      this.socket = null;
      this.connected = false;
      this.activeSubscriptions.clear();
    }
  }

  /**
   * Subscribe to a chat session
   * @param {number} sessionId - Session ID to subscribe to
   */
  subscribeToSession(sessionId) {
    if (!this.connected) {
      console.warn(`Cannot subscribe to session ${sessionId}: WebSocket not connected`);
      return false;
    }

    this.send({
      type: 'subscribe',
      session_id: sessionId
    });

    this.activeSubscriptions.add(sessionId);
    console.log(`Subscribed to session ${sessionId}`);
    return true;
  }

  /**
   * Unsubscribe from a chat session
   * @param {number} sessionId - Session ID to unsubscribe from
   */
  unsubscribeFromSession(sessionId) {
    if (!this.connected) {
      console.warn(`Cannot unsubscribe from session ${sessionId}: WebSocket not connected`);
      return false;
    }

    this.send({
      type: 'unsubscribe',
      session_id: sessionId
    });

    this.activeSubscriptions.delete(sessionId);
    console.log(`Unsubscribed from session ${sessionId}`);
    return true;
  }

  /**
   * Update typing status
   * @param {boolean} isTyping - Whether the user is typing
   * @param {number} sessionId - Session ID
   */
  updateTypingStatus(isTyping, sessionId) {
    this.send({
      type: 'typing',
      is_typing: isTyping,
      session_id: sessionId
    });
  }

  /**
   * Send a read receipt for a message
   * @param {number} messageId - Message ID that was read
   * @param {number} sessionId - Session ID
   */
  sendReadReceipt(messageId, sessionId) {
    this.send({
      type: 'read_receipt',
      message_id: messageId,
      session_id: sessionId
    });
  }

  /**
   * Resubscribe to active sessions after reconnection
   */
  resubscribeToSessions() {
    for (const sessionId of this.activeSubscriptions) {
      this.subscribeToSession(sessionId);
    }
  }

  /**
   * Start ping interval to keep connection alive
   */
  startPingInterval() {
    this.pingInterval = setInterval(() => {
      if (this.connected) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Clear ping interval
   */
  clearPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Handle connection established message
   * @param {Object} message - Connection established message
   */
  handleConnectionEstablished(message) {
    // If we have a current session in the store, subscribe to it
    const currentSession = store.getters['chat/currentSession'];
    if (currentSession) {
      this.subscribeToSession(currentSession.id);
    }
  }

  /**
   * Handle chat message
   * @param {Object} message - Chat message
   */
  handleChatMessage(message) {
    // Add the message to the store if it's for the current session
    const currentSession = store.getters['chat/currentSession'];
    if (currentSession && message.session_id === currentSession.id) {
      // Check if this message is already in the store to avoid duplicates
      const existingMessage = store.getters['chat/messages'].find(
        m => m.id === message.message.id
      );
      
      if (!existingMessage) {
        store.commit('chat/ADD_MESSAGE', message.message);
      }
    }
  }

  /**
   * Handle message chunk (for streaming responses)
   * @param {Object} message - Message chunk
   */
  handleMessageChunk(message) {
    // Dispatch to store to handle streaming
    store.dispatch('chat/handleMessageChunk', message);
  }

  /**
   * Handle typing status update
   * @param {Object} message - Typing status message
   */
  handleTypingStatus(message) {
    // Update typing status in the store
    store.commit('chat/SET_TYPING_STATUS', {
      userId: message.user_id,
      isTyping: message.is_typing,
      sessionId: message.session_id
    });
  }

  /**
   * Handle read receipt
   * @param {Object} message - Read receipt message
   */
  handleReadReceipt(message) {
    // Update read status in the store
    store.commit('chat/SET_MESSAGE_READ', {
      messageId: message.message_id,
      userId: message.user_id,
      timestamp: message.timestamp
    });
  }

  /**
   * Handle task update
   * @param {Object} message - Task update message
   */
  handleTaskUpdate(message) {
    // Update task status in the store
    store.dispatch('chat/updateTaskStatus', message);
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
