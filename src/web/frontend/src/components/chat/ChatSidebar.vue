<template>
  <v-navigation-drawer
    v-model="localValue"
    app
    right
    width="350"
    class="chat-sidebar"
    temporary
  >
    <v-app-bar flat dark color="primary" class="chat-sidebar-header">
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            text
            v-bind="attrs"
            v-on="on"
            class="text-none px-1"
          >
            <span class="text-truncate" style="max-width: 180px">{{ sessionTitle }}</span>
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="newSession">
            <v-list-item-icon>
              <v-icon>mdi-plus</v-icon>
            </v-list-item-icon>
            <v-list-item-title>New Chat</v-list-item-title>
          </v-list-item>
          <v-divider v-if="sessions.length > 0"></v-divider>
          <v-list-item
            v-for="session in sessions"
            :key="session.id"
            @click="switchSession(session.id)"
          >
            <v-list-item-icon>
              <v-icon v-if="currentSession && session.id === currentSession.id">
                mdi-check
              </v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ session.title }}</v-list-item-title>
            <v-list-item-action v-if="sessions.length > 1">
              <v-btn
                icon
                small
                @click.stop="confirmDeleteSession(session)"
              >
                <v-icon small>mdi-delete-outline</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-menu>
      <v-spacer></v-spacer>
      <v-btn icon @click="clearChat">
        <v-icon>mdi-broom</v-icon>
      </v-btn>
      <v-btn icon @click="$emit('input', false)">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- Phase 7: Add tabs for conversation and settings -->
    <v-tabs
      v-model="activeTab"
      grow
      background-color="primary"
      dark
    >
      <v-tab>
        <v-icon small class="mr-1">mdi-chat</v-icon>
        Chat
      </v-tab>
      <v-tab>
        <v-icon small class="mr-1">mdi-lightning-bolt</v-icon>
        Commands
      </v-tab>
      <v-tab>
        <v-icon small class="mr-1">mdi-cog</v-icon>
        Preferences
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="activeTab" class="flex-grow-1 d-flex flex-column">
      <!-- Chat Tab -->
      <v-tab-item class="flex-grow-1 d-flex flex-column">
        <v-container fluid class="chat-messages-container pa-0 flex-grow-1">
          <div class="chat-messages" ref="chatMessages">
            <div v-if="messages.length === 0" class="chat-empty-state">
              <v-icon size="64" color="grey lighten-1">mdi-chat-outline</v-icon>
              <p class="text-center grey--text text--darken-1 mt-4">
                Ask me anything about Docker or your containers
              </p>
            </div>
            <chat-message
              v-for="(message, index) in messages"
              :key="index"
              :message="message"
              :existing-feedback="getFeedbackForMessage(message.id)"
              class="px-4"
              @feedback-submitted="handleFeedbackSubmitted"
            />
          </div>
        </v-container>
        
        <div v-if="suggestions.length > 0" class="suggestions-container px-2 py-2">
          <div class="d-flex flex-wrap">
            <v-chip
              v-for="(suggestion, i) in suggestions"
              :key="i"
              class="ma-1"
              outlined
              small
              @click="handleSuggestionClick(suggestion)"
            >
              {{ suggestion }}
            </v-chip>
          </div>
        </div>

        <div class="chat-input-container">
          <chat-input 
            @send="handleSendMessage" 
            :loading="isLoading" 
            :command-shortcuts="commandShortcuts"
          />
        </div>
      </v-tab-item>

      <!-- Commands Tab -->
      <v-tab-item>
        <v-container class="pa-4 overflow-y-auto" style="height: 100%">
          <chat-commands @use-shortcut="handleShortcutUse" @notification="showNotification" />
        </v-container>
      </v-tab-item>

      <!-- Preferences Tab -->
      <v-tab-item>
        <v-container class="pa-4 overflow-y-auto" style="height: 100%">
          <chat-preferences @notification="showNotification" />
        </v-container>
      </v-tab-item>
    </v-tabs-items>


    <!-- Delete session confirmation dialog -->
    <v-dialog v-model="deleteDialog" max-width="300">
      <v-card>
        <v-card-title class="headline">Delete Chat Session</v-card-title>
        <v-card-text>
          Are you sure you want to delete this chat session? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false">Cancel</v-btn>
          <v-btn 
            color="error" 
            text 
            @click="deleteSession(sessionToDelete.id)"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-navigation-drawer>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import ChatMessage from './ChatMessage.vue';
import ChatInput from './ChatInput.vue';
import ChatCommands from './ChatCommands.vue';
import ChatPreferences from './ChatPreferences.vue';

export default {
  name: 'ChatSidebar',
  components: {
    ChatMessage,
    ChatInput,
    ChatCommands,
    ChatPreferences
  },
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      deleteDialog: false,
      sessionToDelete: null,
      activeTab: 0,
      snackbar: {
        show: false,
        text: '',
        color: 'info'
      }
    }
  },
  computed: {
    ...mapGetters('chat', [
      'messages', 
      'isLoading', 
      'error', 
      'suggestions', 
      'currentSession',
      'sessions',
      'getFeedbackForMessage',
      'commandShortcuts'
    ]),
    localValue: {
      get() {
        return this.value || this.$store.getters['chat/isActive'];
      },
      set(value) {
        this.$emit('input', value);
        this.$store.commit('chat/SET_ACTIVE', value);
      }
    },
    sessionTitle() {
      return this.currentSession?.title || 'New Chat';
    }
  },
  methods: {
    ...mapActions('chat', [
      'sendMessage', 
      'clearChat', 
      'createSession', 
      'loadSession', 
      'loadSessions',
      'switchSession',
      'deleteSession',
      'submitMessageFeedback',
      'updateMessageFeedback',
      'useCommandShortcut'
    ]),
    handleSendMessage(message) {
      this.sendMessage(message.text);
      this.scrollToBottom();
    },
    handleSuggestionClick(suggestion) {
      this.sendMessage(suggestion);
      this.scrollToBottom();
    },
    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.chatMessages) {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
        }
      });
    },
    async newSession() {
      try {
        await this.createSession();
        await this.loadSessions();
        this.scrollToBottom();
      } catch (error) {
        console.error('Error creating new session:', error);
      }
    },
    confirmDeleteSession(session) {
      this.sessionToDelete = session;
      this.deleteDialog = true;
    },
    
    // Phase 7: Handle feedback submitted from ChatMessage component
    handleFeedbackSubmitted(feedbackData) {
      // Update store with feedback
      this.updateMessageFeedback({
        messageId: feedbackData.messageId,
        feedback: {
          id: feedbackData.feedbackId,
          rating: feedbackData.rating,
          feedback_text: feedbackData.feedbackText
        }
      });
      
      // Show notification
      this.showNotification({
        type: 'success',
        message: 'Thank you for your feedback!'
      });
    },
    
    // Phase 7: Handle shortcut use
    async handleShortcutUse(shortcut) {
      try {
        // Switch to chat tab
        this.activeTab = 0;
        
        // Get template from API
        const result = await this.useCommandShortcut(shortcut.command);
        
        // Insert template into input
        // Note: This will require adding a method to ChatInput component
        if (this.$refs.chatInput) {
          this.$refs.chatInput.setInputText(result.template);
        } else {
          // Fallback: Send message directly
          this.sendMessage(result.template);
        }
      } catch (error) {
        console.error('Error using command shortcut:', error);
        this.showNotification({
          type: 'error',
          message: 'Failed to use command shortcut'
        });
      }
    },
    
    // Phase 7: Show notification message
    showNotification({ type, message }) {
      this.snackbar = {
        show: true,
        text: message,
        color: type === 'error' ? 'error' : 'success'
      };
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        this.snackbar.show = false;
      }, 3000);
    }
  },
  watch: {
    messages() {
      this.scrollToBottom();
    },
    value(newValue) {
      if (newValue) {
        // When sidebar is opened, scroll to bottom of messages
        this.scrollToBottom();
      }
    }
  },
  mounted() {
    // Initialize the chat module
    this.$store.dispatch('chat/init');
    
    // When component is mounted, check if sidebar should be open
    if (this.$store.getters['chat/isActive']) {
      this.$emit('input', true);
    }
    
    this.scrollToBottom();
  }
};
</script>

<style scoped>
.chat-sidebar {
  display: flex;
  flex-direction: column;
}

.chat-messages-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.chat-messages {
  height: 100%;
  overflow-y: auto;
  padding-top: 16px;
  padding-bottom: 16px;
}

.chat-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 24px;
}

.suggestions-container {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  background-color: #f5f5f5;
}

.theme--dark .suggestions-container {
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  background-color: #424242;
}

.chat-input-container {
  position: relative;
  z-index: 1;
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.theme--dark .chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
