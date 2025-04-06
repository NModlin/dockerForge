<template>
  <div class="terminal-container" ref="terminalContainer">
    <div class="terminal-header">
      <div class="terminal-title">
        <v-icon left>mdi-console</v-icon>
        {{ title || `Terminal: ${containerId}` }}
      </div>
      <div class="terminal-actions">
        <v-btn icon small @click="clearTerminal" title="Clear Terminal">
          <v-icon>mdi-eraser</v-icon>
        </v-btn>
        <v-btn icon small @click="reconnect" title="Reconnect" :disabled="connecting">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
        <v-btn icon small @click="$emit('close')" title="Close Terminal">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </div>
    <div class="terminal-wrapper" ref="terminalWrapper"></div>
    <div class="terminal-status-bar">
      <div class="terminal-status">
        <v-icon small :color="connected ? 'success' : 'error'" class="mr-1">
          {{ connected ? 'mdi-check-circle' : 'mdi-alert-circle' }}
        </v-icon>
        {{ statusMessage }}
      </div>
      <div class="terminal-info">
        <span v-if="commandHistory.length > 0">
          {{ commandHistory.length }} commands
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

export default {
  name: 'TerminalComponent',
  
  props: {
    containerId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    autoConnect: {
      type: Boolean,
      default: true
    },
    userId: {
      type: String,
      default: 'anonymous'
    }
  },
  
  data() {
    return {
      terminal: null,
      fitAddon: null,
      socket: null,
      connected: false,
      connecting: false,
      statusMessage: 'Disconnected',
      commandHistory: [],
      pingInterval: null,
      reconnectAttempts: 0,
      maxReconnectAttempts: 5
    };
  },
  
  mounted() {
    this.initTerminal();
    
    if (this.autoConnect) {
      this.connect();
    }
    
    // Add resize event listener
    window.addEventListener('resize', this.onResize);
  },
  
  beforeDestroy() {
    this.disconnect();
    
    // Clean up
    if (this.terminal) {
      this.terminal.dispose();
    }
    
    // Remove resize event listener
    window.removeEventListener('resize', this.onResize);
  },
  
  methods: {
    initTerminal() {
      // Create terminal
      this.terminal = new Terminal({
        cursorBlink: true,
        cursorStyle: 'bar',
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        fontSize: 14,
        lineHeight: 1.2,
        theme: {
          background: '#1e1e1e',
          foreground: '#f0f0f0',
          cursor: '#f0f0f0',
          selection: 'rgba(255, 255, 255, 0.3)',
          black: '#000000',
          red: '#e06c75',
          green: '#98c379',
          yellow: '#e5c07b',
          blue: '#61afef',
          magenta: '#c678dd',
          cyan: '#56b6c2',
          white: '#d0d0d0',
          brightBlack: '#808080',
          brightRed: '#e06c75',
          brightGreen: '#98c379',
          brightYellow: '#e5c07b',
          brightBlue: '#61afef',
          brightMagenta: '#c678dd',
          brightCyan: '#56b6c2',
          brightWhite: '#ffffff'
        }
      });
      
      // Create fit addon
      this.fitAddon = new FitAddon();
      this.terminal.loadAddon(this.fitAddon);
      
      // Create web links addon
      const webLinksAddon = new WebLinksAddon();
      this.terminal.loadAddon(webLinksAddon);
      
      // Open terminal
      this.terminal.open(this.$refs.terminalWrapper);
      
      // Fit terminal to container
      this.$nextTick(() => {
        this.fitAddon.fit();
      });
      
      // Handle terminal input
      this.terminal.onData(data => {
        if (this.connected) {
          this.sendInput(data);
        }
      });
      
      // Initial message
      this.terminal.writeln('DockerForge Terminal');
      this.terminal.writeln('------------------');
      this.terminal.writeln(`Container: ${this.containerId}`);
      this.terminal.writeln('');
      if (this.autoConnect) {
        this.terminal.writeln('Connecting...');
      } else {
        this.terminal.writeln('Press Connect to start the terminal session.');
      }
      this.terminal.writeln('');
    },
    
    connect() {
      if (this.connected || this.connecting) {
        return;
      }
      
      this.connecting = true;
      this.statusMessage = 'Connecting...';
      
      // Get terminal dimensions
      const dimensions = this.getTerminalDimensions();
      
      // Create WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/api/terminal/${this.containerId}?cols=${dimensions.cols}&rows=${dimensions.rows}&user_id=${this.userId}`;
      
      this.socket = new WebSocket(wsUrl);
      
      // Set up event handlers
      this.socket.onopen = this.onSocketOpen;
      this.socket.onclose = this.onSocketClose;
      this.socket.onerror = this.onSocketError;
      this.socket.onmessage = this.onSocketMessage;
      
      // Log connection attempt
      console.log(`Connecting to terminal WebSocket: ${wsUrl}`);
    },
    
    disconnect() {
      // Clear ping interval
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
      
      // Close WebSocket connection
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      
      // Update state
      this.connected = false;
      this.connecting = false;
      this.statusMessage = 'Disconnected';
    },
    
    reconnect() {
      this.disconnect();
      this.reconnectAttempts = 0;
      this.connect();
    },
    
    sendInput(data) {
      if (!this.connected || !this.socket) {
        return;
      }
      
      try {
        this.socket.send(JSON.stringify({
          type: 'input',
          data: data
        }));
      } catch (error) {
        console.error('Error sending terminal input:', error);
      }
    },
    
    clearTerminal() {
      if (this.terminal) {
        this.terminal.clear();
      }
    },
    
    onResize() {
      if (this.fitAddon) {
        this.fitAddon.fit();
        
        // Send resize event to server
        if (this.connected) {
          const dimensions = this.getTerminalDimensions();
          this.socket.send(JSON.stringify({
            type: 'resize',
            cols: dimensions.cols,
            rows: dimensions.rows
          }));
        }
      }
    },
    
    getTerminalDimensions() {
      return {
        cols: this.terminal ? this.terminal.cols : 80,
        rows: this.terminal ? this.terminal.rows : 24
      };
    },
    
    onSocketOpen() {
      this.connected = true;
      this.connecting = false;
      this.statusMessage = 'Connected';
      this.reconnectAttempts = 0;
      
      // Set up ping interval to keep connection alive
      this.pingInterval = setInterval(() => {
        if (this.connected && this.socket) {
          try {
            this.socket.send(JSON.stringify({
              type: 'ping',
              timestamp: Date.now()
            }));
          } catch (error) {
            console.error('Error sending ping:', error);
          }
        }
      }, 30000); // Send ping every 30 seconds
      
      // Emit connected event
      this.$emit('connected');
    },
    
    onSocketClose(event) {
      // Clear ping interval
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
      
      // Update state
      this.connected = false;
      this.connecting = false;
      
      // Handle close event
      if (event.wasClean) {
        this.statusMessage = `Disconnected: ${event.reason || 'Connection closed'}`;
        this.terminal.writeln(`\r\n\nConnection closed: ${event.reason || 'Connection closed'}`);
      } else {
        this.statusMessage = 'Connection lost';
        this.terminal.writeln('\r\n\nConnection lost. Attempting to reconnect...');
        
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
          
          this.statusMessage = `Reconnecting in ${delay / 1000} seconds...`;
          
          setTimeout(() => {
            if (!this.connected && !this.connecting) {
              this.connect();
            }
          }, delay);
        } else {
          this.statusMessage = 'Failed to reconnect';
          this.terminal.writeln('\r\n\nFailed to reconnect after multiple attempts. Please try again manually.');
        }
      }
      
      // Emit disconnected event
      this.$emit('disconnected', event);
    },
    
    onSocketError(error) {
      console.error('Terminal WebSocket error:', error);
      this.statusMessage = 'Connection error';
      this.terminal.writeln('\r\n\nConnection error. Please try again.');
      
      // Emit error event
      this.$emit('error', error);
    },
    
    onSocketMessage(event) {
      try {
        // Check if the message is a text message (JSON)
        if (typeof event.data === 'string') {
          const message = JSON.parse(event.data);
          
          // Handle different message types
          switch (message.type) {
            case 'session_created':
              this.terminal.writeln(`\r\nSession created: ${message.session_id}`);
              break;
              
            case 'error':
              this.terminal.writeln(`\r\nError: ${message.error}`);
              break;
              
            case 'pong':
              // Ping response, do nothing
              break;
              
            default:
              console.log('Unknown message type:', message.type);
          }
        }
        // Check if the message is binary data (terminal output)
        else if (event.data instanceof Blob) {
          const reader = new FileReader();
          
          reader.onload = () => {
            const data = new Uint8Array(reader.result);
            this.terminal.write(data);
          };
          
          reader.readAsArrayBuffer(event.data);
        }
      } catch (error) {
        console.error('Error processing terminal message:', error);
      }
    }
  }
};
</script>

<style scoped>
.terminal-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #444;
  border-radius: 4px;
  overflow: hidden;
  background-color: #1e1e1e;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #2d2d2d;
  border-bottom: 1px solid #444;
}

.terminal-title {
  font-size: 14px;
  font-weight: bold;
  color: #f0f0f0;
  display: flex;
  align-items: center;
}

.terminal-actions {
  display: flex;
  gap: 4px;
}

.terminal-wrapper {
  flex: 1;
  padding: 4px;
  overflow: hidden;
}

.terminal-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  background-color: #2d2d2d;
  border-top: 1px solid #444;
  font-size: 12px;
  color: #ccc;
}

.terminal-status {
  display: flex;
  align-items: center;
}

.terminal-info {
  font-size: 11px;
}
</style>
