<template>
  <div class="chat-input">
    <v-form @submit.prevent="sendMessage" ref="form">
      <v-text-field
        v-model="message"
        placeholder="Type a message..."
        outlined
        dense
        hide-details
        autocomplete="off"
        @keydown.enter.prevent="sendMessage"
        @keydown="handleKeyDown"
        class="chat-input-field"
        :disabled="loading"
        ref="inputField"
      >
        <template v-slot:prepend-inner>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                x-small
                v-bind="attrs"
                v-on="on"
                @click="showCommandsList = !showCommandsList"
                class="mt-1"
              >
                <v-icon small>mdi-slash-forward</v-icon>
              </v-btn>
            </template>
            <span>Command shortcuts</span>
          </v-tooltip>
        </template>
        
        <template v-slot:append>
          <v-btn
            icon
            color="primary"
            @click="sendMessage"
            :disabled="!message.trim() || loading"
            :loading="loading"
          >
            <v-icon>mdi-send</v-icon>
          </v-btn>
        </template>
      </v-text-field>
    </v-form>
    
    <!-- Command Shortcuts Menu -->
    <v-menu
      v-model="showCommandsList"
      :close-on-content-click="true"
      :nudge-width="200"
      offset-y
      content-class="command-shortcuts-menu"
    >
      <v-card>
        <v-list dense>
          <v-subheader>Command Shortcuts</v-subheader>
          <v-list-item
            v-for="shortcut in commandShortcuts"
            :key="shortcut.id"
            @click="useCommandShortcut(shortcut)"
            dense
          >
            <v-list-item-content>
              <v-list-item-title class="text-body-2">
                /{{ shortcut.command }}
              </v-list-item-title>
              <v-list-item-subtitle class="text-caption">
                {{ shortcut.description }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item v-if="!commandShortcuts || commandShortcuts.length === 0">
            <v-list-item-content>
              <v-list-item-subtitle class="text-center">
                No command shortcuts available
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: 'ChatInput',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    commandShortcuts: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      message: '',
      showCommandsList: false
    }
  },
  methods: {
    sendMessage() {
      if (this.loading) return;
      
      const trimmedMessage = this.message.trim();
      if (trimmedMessage) {
        this.$emit('send', {
          type: 'user',
          text: trimmedMessage,
          timestamp: new Date().toISOString()
        });
        this.message = '';
      }
    },
    
    // Phase 7: Set input text programmatically (for command shortcuts)
    setInputText(text) {
      this.message = text;
      // Focus the input field
      this.$nextTick(() => {
        if (this.$refs.inputField) {
          this.$refs.inputField.focus();
        }
      });
    },
    
    // Phase 7: Handle keyboard shortcuts and command expansion
    handleKeyDown(event) {
      // Check for slash command
      if (event.key === '/' && this.message === '') {
        this.showCommandsList = true;
      }
      
      // Check if we need to auto-expand a command
      const commandMatch = this.message.match(/^\/(\w+)$/);
      if (commandMatch && event.key === ' ') {
        const command = commandMatch[1];
        const shortcut = this.commandShortcuts.find(s => s.command === command);
        if (shortcut) {
          // Prevent space from being added
          event.preventDefault();
          
          // Expand command
          this.useCommandShortcut(shortcut);
        }
      }
    },
    
    // Phase 7: Use a command shortcut
    useCommandShortcut(shortcut) {
      // Replace input text with shortcut template
      this.setInputText(shortcut.template);
      
      // Close menu
      this.showCommandsList = false;
      
      // Emit event
      this.$emit('use-shortcut', shortcut);
    }
  }
}
</script>

<style scoped>
.chat-input {
  padding: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  background-color: #fff;
  position: relative;
}

.theme--dark .chat-input {
  background-color: #1e1e1e;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-input-field {
  border-radius: 20px;
}

/* Command shortcuts menu styling */
.command-shortcuts-menu {
  max-height: 300px;
  overflow-y: auto;
}
</style>
