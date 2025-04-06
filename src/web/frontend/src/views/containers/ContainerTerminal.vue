<template>
  <div class="container-terminal">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-console</v-icon>
              Terminal: {{ containerName }}
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="showCommandHistory"
                :disabled="!terminal || !terminal.connected"
              >
                <v-icon left>mdi-history</v-icon>
                Command History
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <div v-if="loading" class="d-flex justify-center align-center my-5">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
              </div>
              <div v-else-if="error" class="text-center red--text">
                {{ error }}
              </div>
              <div v-else class="terminal-wrapper">
                <Terminal
                  ref="terminal"
                  :container-id="containerId"
                  :title="`Terminal: ${containerName}`"
                  :auto-connect="true"
                  :user-id="userId"
                  @connected="onTerminalConnected"
                  @disconnected="onTerminalDisconnected"
                  @error="onTerminalError"
                ></Terminal>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Command History Dialog -->
    <v-dialog v-model="historyDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <v-icon left>mdi-history</v-icon>
          Command History
        </v-card-title>
        <v-card-text>
          <div v-if="loadingHistory" class="d-flex justify-center align-center my-5">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
          <div v-else-if="commandHistory.length === 0" class="text-center grey--text my-5">
            No command history available
          </div>
          <v-list v-else dense>
            <v-list-item
              v-for="(command, index) in commandHistory"
              :key="index"
              @click="executeCommand(command)"
            >
              <v-list-item-icon>
                <v-icon>mdi-console-line</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ command }}</v-list-item-title>
              </v-list-item-content>
              <v-list-item-action>
                <v-btn icon small @click.stop="executeCommand(command)">
                  <v-icon small>mdi-play</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="historyDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import Terminal from '@/components/terminal/Terminal.vue';
import axios from 'axios';

export default {
  name: 'ContainerTerminal',
  
  components: {
    Terminal
  },
  
  data() {
    return {
      loading: true,
      error: null,
      container: null,
      terminal: null,
      commandHistory: [],
      historyDialog: false,
      loadingHistory: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token'
    }),
    ...mapState({
      user: state => state.auth.user
    }),
    
    containerId() {
      return this.$route.params.id;
    },
    
    containerName() {
      return this.container ? this.container.name : this.containerId;
    },
    
    userId() {
      return this.user ? this.user.id : 'anonymous';
    }
  },
  
  created() {
    this.fetchContainer();
  },
  
  methods: {
    async fetchContainer() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/api/containers/${this.containerId}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        
        this.container = response.data;
        
        // Check if container is running
        if (this.container.status !== 'running') {
          this.error = `Container ${this.container.name} is not running. Terminal requires a running container.`;
        }
      } catch (error) {
        this.error = `Failed to load container: ${error.response?.data?.detail || error.message}`;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchCommandHistory() {
      this.loadingHistory = true;
      
      try {
        const response = await axios.get(`/api/terminal/history/${this.containerId}`, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        
        this.commandHistory = response.data;
      } catch (error) {
        this.showError(`Failed to load command history: ${error.response?.data?.detail || error.message}`);
      } finally {
        this.loadingHistory = false;
      }
    },
    
    showCommandHistory() {
      this.historyDialog = true;
      this.fetchCommandHistory();
    },
    
    executeCommand(command) {
      if (this.terminal && this.terminal.connected) {
        // Send command to terminal
        this.terminal.sendInput(command + '\n');
        this.historyDialog = false;
      } else {
        this.showError('Terminal is not connected');
      }
    },
    
    onTerminalConnected() {
      this.terminal = this.$refs.terminal;
      this.showSuccess('Terminal connected');
    },
    
    onTerminalDisconnected() {
      this.showError('Terminal disconnected');
    },
    
    onTerminalError(error) {
      this.showError(`Terminal error: ${error}`);
    },
    
    showSuccess(message) {
      this.snackbarText = message;
      this.snackbarColor = 'success';
      this.snackbar = true;
    },
    
    showError(message) {
      this.snackbarText = message;
      this.snackbarColor = 'error';
      this.snackbar = true;
    }
  }
};
</script>

<style scoped>
.container-terminal {
  height: 100%;
}

.terminal-wrapper {
  height: 70vh;
  min-height: 400px;
}
</style>
