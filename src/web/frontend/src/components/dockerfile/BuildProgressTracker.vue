<template>
  <div class="build-progress-tracker">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-progress-clock</v-icon>
        Build Progress
        <v-spacer></v-spacer>
        <v-btn
          v-if="logs.length > 0"
          text
          small
          color="primary"
          @click="downloadLogs"
        >
          <v-icon left small>mdi-download</v-icon>
          Download Logs
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <div v-if="!building && logs.length === 0" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-hammer-wrench</v-icon>
          <p class="text-body-2 mt-2 grey--text">No build in progress</p>
          <p class="text-caption grey--text">
            Start a build to see progress here
          </p>
        </div>
        
        <div v-else>
          <!-- Build Status -->
          <div class="px-4 pt-4 pb-2 d-flex align-center">
            <v-progress-circular
              v-if="building"
              indeterminate
              color="primary"
              size="24"
              width="2"
              class="mr-3"
            ></v-progress-circular>
            <v-icon
              v-else-if="buildStatus === 'success'"
              color="success"
              class="mr-3"
            >
              mdi-check-circle
            </v-icon>
            <v-icon
              v-else-if="buildStatus === 'error'"
              color="error"
              class="mr-3"
            >
              mdi-alert-circle
            </v-icon>
            <div>
              <div class="text-subtitle-2">
                {{ statusText }}
              </div>
              <div v-if="buildDuration" class="text-caption">
                Duration: {{ buildDuration }}
              </div>
            </div>
            <v-spacer></v-spacer>
            <v-btn
              v-if="building"
              icon
              small
              color="error"
              @click="$emit('cancel')"
              title="Cancel build"
            >
              <v-icon small>mdi-close-circle</v-icon>
            </v-btn>
          </div>
          
          <!-- Build Steps Progress -->
          <v-divider></v-divider>
          <div class="px-4 py-2">
            <v-progress-linear
              v-if="building"
              :value="progressPercentage"
              height="20"
              color="primary"
              striped
            >
              <template v-slot:default>
                <span class="white--text">{{ progressPercentage }}%</span>
              </template>
            </v-progress-linear>
            
            <div v-else-if="buildStatus === 'success'" class="text-center py-2">
              <v-chip color="success" text-color="white">
                <v-icon left small>mdi-check</v-icon>
                Build Completed Successfully
              </v-chip>
            </div>
            
            <div v-else-if="buildStatus === 'error'" class="text-center py-2">
              <v-chip color="error" text-color="white">
                <v-icon left small>mdi-alert</v-icon>
                Build Failed
              </v-chip>
            </div>
          </div>
          
          <!-- Build Logs -->
          <v-divider></v-divider>
          <div class="build-logs-container">
            <div class="build-logs-header px-4 py-2 d-flex align-center">
              <div class="text-subtitle-2">Build Logs</div>
              <v-spacer></v-spacer>
              <v-btn
                icon
                x-small
                @click="autoScroll = !autoScroll"
                :color="autoScroll ? 'primary' : ''"
                title="Auto-scroll"
              >
                <v-icon x-small>mdi-arrow-down-box</v-icon>
              </v-btn>
              <v-btn
                icon
                x-small
                @click="expandLogs = !expandLogs"
                title="Expand logs"
              >
                <v-icon x-small>
                  {{ expandLogs ? 'mdi-arrow-collapse' : 'mdi-arrow-expand' }}
                </v-icon>
              </v-btn>
            </div>
            
            <div
              ref="logsContainer"
              class="build-logs-content pa-2"
              :class="{ 'expanded': expandLogs }"
            >
              <pre v-if="logs.length > 0" class="logs-text">{{ formattedLogs }}</pre>
              <div v-else class="text-center pa-4">
                <p class="text-body-2 grey--text">No logs available yet</p>
              </div>
            </div>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'BuildProgressTracker',
  
  props: {
    building: {
      type: Boolean,
      default: false
    },
    buildStatus: {
      type: String,
      default: null // null, 'success', 'error'
    },
    logs: {
      type: Array,
      default: () => []
    },
    startTime: {
      type: [Date, null],
      default: null
    },
    endTime: {
      type: [Date, null],
      default: null
    },
    totalSteps: {
      type: Number,
      default: 0
    },
    currentStep: {
      type: Number,
      default: 0
    }
  },
  
  data() {
    return {
      autoScroll: true,
      expandLogs: false
    };
  },
  
  computed: {
    statusText() {
      if (this.building) {
        return `Building image... (Step ${this.currentStep}/${this.totalSteps || '?'})`;
      } else if (this.buildStatus === 'success') {
        return 'Build completed successfully';
      } else if (this.buildStatus === 'error') {
        return 'Build failed';
      } else {
        return 'Ready to build';
      }
    },
    
    buildDuration() {
      if (!this.startTime) {
        return null;
      }
      
      const endTime = this.endTime || new Date();
      const durationMs = endTime - this.startTime;
      
      // Format duration
      if (durationMs < 1000) {
        return `${durationMs}ms`;
      } else if (durationMs < 60000) {
        return `${Math.floor(durationMs / 1000)}s`;
      } else {
        const minutes = Math.floor(durationMs / 60000);
        const seconds = Math.floor((durationMs % 60000) / 1000);
        return `${minutes}m ${seconds}s`;
      }
    },
    
    progressPercentage() {
      if (!this.totalSteps || this.totalSteps === 0) {
        return 0;
      }
      
      const percentage = (this.currentStep / this.totalSteps) * 100;
      return Math.min(Math.round(percentage), 100);
    },
    
    formattedLogs() {
      return this.logs.join('\n');
    }
  },
  
  watch: {
    logs() {
      this.$nextTick(() => {
        if (this.autoScroll) {
          this.scrollToBottom();
        }
      });
    }
  },
  
  methods: {
    scrollToBottom() {
      const container = this.$refs.logsContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    downloadLogs() {
      if (!this.logs.length) {
        return;
      }
      
      // Create a blob with the logs
      const blob = new Blob([this.formattedLogs], { type: 'text/plain' });
      
      // Create a download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      a.download = `build-logs-${timestamp}.txt`;
      
      // Trigger download
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    }
  }
};
</script>

<style scoped>
.build-progress-tracker {
  width: 100%;
}

.build-logs-container {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

.build-logs-header {
  background-color: #f5f5f5;
}

.build-logs-content {
  max-height: 300px;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #f0f0f0;
  transition: max-height 0.3s ease;
}

.build-logs-content.expanded {
  max-height: 600px;
}

.logs-text {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}
</style>
