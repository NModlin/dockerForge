<template>
  <div class="contextual-help">
    <v-card v-if="helpContent" outlined>
      <v-card-title class="primary white--text">
        <v-icon left color="white">mdi-help-circle-outline</v-icon>
        {{ helpContent.title }}
        <v-spacer></v-spacer>
        <v-btn icon @click="$emit('close')" class="white--text">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pa-4">
        <div v-html="helpContent.content"></div>
        
        <div v-if="helpContent.tips && helpContent.tips.length" class="mt-4">
          <v-subheader>Tips & Tricks</v-subheader>
          <v-list dense>
            <v-list-item v-for="(tip, i) in helpContent.tips" :key="i">
              <v-list-item-icon>
                <v-icon color="info">mdi-lightbulb-on</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-subtitle v-html="tip"></v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </div>
        
        <div v-if="helpContent.actions && helpContent.actions.length" class="mt-3">
          <v-divider class="mb-3"></v-divider>
          <div class="d-flex flex-wrap">
            <v-btn
              v-for="(action, i) in helpContent.actions"
              :key="i"
              :color="action.color || 'primary'"
              class="mr-2 mb-2"
              small
              @click="handleAction(action)"
            >
              <v-icon left small v-if="action.icon">{{ action.icon }}</v-icon>
              {{ action.label }}
            </v-btn>
          </div>
        </div>
      </v-card-text>
      
      <v-card-actions>
        <v-btn text color="primary" @click="openHelpCenter">
          <v-icon left>mdi-lifebuoy</v-icon>
          Open Help Center
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn text @click="askInChat">
          <v-icon left>mdi-message-question</v-icon>
          Ask in Chat
        </v-btn>
      </v-card-actions>
    </v-card>
    
    <!-- Fallback when no contextual help is available -->
    <v-card v-else outlined>
      <v-card-title class="primary white--text">
        <v-icon left color="white">mdi-help-circle-outline</v-icon>
        Help
        <v-spacer></v-spacer>
        <v-btn icon @click="$emit('close')" class="white--text">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pa-4">
        <p>No specific help available for this page.</p>
        <p>You can:</p>
        <ul>
          <li>Visit the Help Center for comprehensive documentation</li>
          <li>Ask the AI Assistant for help with your current task</li>
          <li>Take the guided tour to learn about DockerForge</li>
        </ul>
      </v-card-text>
      
      <v-card-actions>
        <v-btn text color="primary" @click="openHelpCenter">
          <v-icon left>mdi-lifebuoy</v-icon>
          Open Help Center
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn text color="secondary" @click="startTour">
          <v-icon left>mdi-compass</v-icon>
          Start Tour
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import helpContentStore from '@/store/modules/help-content';

export default {
  name: 'ContextualHelp',
  props: {
    context: {
      type: String,
      default: null
    },
    pageIdentifier: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      helpContentMap: {
        // Dashboard
        'dashboard': {
          title: 'Dashboard Help',
          content: `
            <p>The Dashboard provides an overview of your Docker environment, including:</p>
            <ul>
              <li>Active containers and their status</li>
              <li>Resource utilization metrics</li>
              <li>Recent security alerts</li>
              <li>System notifications</li>
            </ul>
            <p>Use the quick action buttons to perform common tasks without navigating away.</p>
          `,
          tips: [
            'Click on container cards to view detailed information',
            'Use the refresh button to update stats and status information',
            'Hover over chart elements to see detailed metrics'
          ],
          actions: [
            { label: 'View All Containers', icon: 'mdi-docker', route: '/containers' },
            { label: 'Security Dashboard', icon: 'mdi-shield', route: '/security' },
            { label: 'Resource Monitor', icon: 'mdi-gauge', route: '/resources' }
          ]
        },
        
        // Containers
        'containers': {
          title: 'Container Management',
          content: `
            <p>This page allows you to manage all your Docker containers from a single interface.</p>
            <p>Key features:</p>
            <ul>
              <li>View all containers with real-time status updates</li>
              <li>Start, stop, restart, or remove containers</li>
              <li>Access container logs and resource statistics</li>
              <li>Connect to container shells</li>
              <li>Manage container configurations</li>
            </ul>
          `,
          tips: [
            'Use filters to quickly find specific containers',
            'Right-click on containers for additional actions',
            'Click the "View Logs" button to troubleshoot container issues',
            'Use batch actions to manage multiple containers at once'
          ],
          actions: [
            { label: 'Create Container', icon: 'mdi-plus', color: 'success', action: 'create-container' },
            { label: 'View Logs', icon: 'mdi-text-box-outline', action: 'view-logs' },
            { label: 'Troubleshoot', icon: 'mdi-wrench', action: 'troubleshoot-container' }
          ]
        },
        
        // Container Detail
        'container-detail': {
          title: 'Container Details',
          content: `
            <p>This page shows detailed information about a specific container, including:</p>
            <ul>
              <li>Container metadata and configuration</li>
              <li>Real-time resource utilization</li>
              <li>Environment variables and mounted volumes</li>
              <li>Network settings and exposed ports</li>
              <li>Container logs with filtering options</li>
            </ul>
          `,
          tips: [
            'Use the terminal tab to execute commands directly in the container',
            'Check the "Health" tab for container health check results',
            'View container events to troubleshoot lifecycle issues',
            'Click "Edit Configuration" to modify container settings'
          ],
          actions: [
            { label: 'Restart Container', icon: 'mdi-restart', color: 'warning', action: 'restart-container' },
            { label: 'Export Config', icon: 'mdi-download', action: 'export-config' },
            { label: 'Security Scan', icon: 'mdi-shield-search', action: 'scan-container' }
          ]
        },
        
        // Images
        'images': {
          title: 'Docker Images',
          content: `
            <p>This page allows you to manage Docker images in your local registry.</p>
            <p>Key features:</p>
            <ul>
              <li>View all available images with version information</li>
              <li>Pull new images from registries</li>
              <li>Build images from Dockerfiles</li>
              <li>Scan images for security vulnerabilities</li>
              <li>Clean up unused images to free space</li>
            </ul>
          `,
          tips: [
            'Use the tag field to specify a version when pulling images',
            'Click on image sizes to see layer details and optimize size',
            'Use image labels for better organization',
            'Regular security scanning helps maintain a secure environment'
          ],
          actions: [
            { label: 'Pull Image', icon: 'mdi-cloud-download', color: 'primary', action: 'pull-image' },
            { label: 'Build Image', icon: 'mdi-hammer', action: 'build-image' },
            { label: 'Clean Up', icon: 'mdi-broom', action: 'cleanup-images' }
          ]
        },
        
        // Security
        'security': {
          title: 'Security Dashboard',
          content: `
            <p>The Security Dashboard helps you identify and fix vulnerabilities in your Docker environment.</p>
            <p>Key features:</p>
            <ul>
              <li>Automated vulnerability scanning for containers and images</li>
              <li>CVE tracking and severity assessment</li>
              <li>One-click vulnerability remediation</li>
              <li>Security policy enforcement</li>
              <li>Security reports and compliance checks</li>
            </ul>
          `,
          tips: [
            'Schedule regular security scans to catch new vulnerabilities',
            'Focus on fixing high-severity issues first',
            'Use "Scan History" to track security posture over time',
            'Enable auto-remediation for non-critical vulnerabilities'
          ],
          actions: [
            { label: 'Scan All', icon: 'mdi-shield-search', color: 'primary', action: 'scan-all' },
            { label: 'Fix Vulnerabilities', icon: 'mdi-shield-check', color: 'success', action: 'fix-vulnerabilities' },
            { label: 'Security Report', icon: 'mdi-file-document', action: 'security-report' }
          ]
        },
        
        // Resources
        'resources': {
          title: 'Resource Monitoring',
          content: `
            <p>This page provides detailed resource utilization metrics for your Docker environment.</p>
            <p>Key features:</p>
            <ul>
              <li>Real-time CPU, memory, and network usage</li>
              <li>Disk space utilization and I/O metrics</li>
              <li>Resource usage trends and historical data</li>
              <li>Automatic anomaly detection</li>
              <li>Resource optimization recommendations</li>
            </ul>
          `,
          tips: [
            'Use the time range selector to analyze historical patterns',
            'Set up alerts for critical resource thresholds',
            'Compare resource usage across different containers',
            'Apply optimization suggestions to improve performance'
          ],
          actions: [
            { label: 'Optimize Resources', icon: 'mdi-tune', color: 'primary', action: 'optimize-resources' },
            { label: 'Export Metrics', icon: 'mdi-chart-line', action: 'export-metrics' },
            { label: 'Configure Alerts', icon: 'mdi-bell', action: 'configure-alerts' }
          ]
        },
        
        // Settings
        'settings': {
          title: 'Settings Help',
          content: `
            <p>The Settings page allows you to configure DockerForge according to your preferences.</p>
            <p>Key sections:</p>
            <ul>
              <li><strong>General:</strong> UI preferences, language, and theme</li>
              <li><strong>Security:</strong> Scanning frequency and security policies</li>
              <li><strong>Resources:</strong> Monitoring settings and alert thresholds</li>
              <li><strong>AI Assistant:</strong> Chat behavior and agent permissions</li>
              <li><strong>Advanced:</strong> Docker daemon settings and system configuration</li>
            </ul>
          `,
          tips: [
            'Use profiles to switch between different configuration sets',
            'Export settings to transfer configuration between installations',
            'Hover over setting labels for detailed explanations',
            'Some settings require a system restart to take effect'
          ],
          actions: [
            { label: 'Reset Defaults', icon: 'mdi-restore', color: 'warning', action: 'reset-defaults' },
            { label: 'Export Settings', icon: 'mdi-download', action: 'export-settings' },
            { label: 'Save Profile', icon: 'mdi-content-save', action: 'save-profile' }
          ]
        },
        
        // Chat
        'chat': {
          title: 'AI Chat Assistant Help',
          content: `
            <p>The AI Chat Assistant helps you interact with DockerForge using natural language.</p>
            <p>Key features:</p>
            <ul>
              <li>Ask questions about Docker in conversational language</li>
              <li>Get help troubleshooting container and image issues</li>
              <li>Execute commands and perform actions via chat</li>
              <li>Access documentation and contextual help</li>
              <li>Use specialized agents for complex tasks</li>
            </ul>
          `,
          tips: [
            'Start commands with "/" (e.g., /logs, /scan) for quick actions',
            'Be specific about container or image names in your questions',
            'Use "Chat about this" buttons throughout the UI for contextual assistance',
            'The assistant learns from your interactions and improves over time'
          ],
          actions: [
            { label: 'View Commands', icon: 'mdi-console', action: 'view-commands' },
            { label: 'Chat Preferences', icon: 'mdi-cog', action: 'chat-preferences' },
            { label: 'Clear History', icon: 'mdi-delete', color: 'error', action: 'clear-chat-history' }
          ]
        }
      }
    };
  },
  computed: {
    helpContent() {
      // First try to get content from Vuex store if implemented
      if (this.$store.hasModule('help')) {
        const storeContent = this.$store.getters['help/getContextualHelp'](this.pageIdentifier || this.context);
        if (storeContent) return storeContent;
      }
      
      // Fall back to local mapping
      return this.helpContentMap[this.pageIdentifier || this.context] || null;
    }
  },
  methods: {
    handleAction(action) {
      if (action.route) {
        this.$router.push(action.route);
      } else if (action.action) {
        this.$emit('action', action.action);
      } else if (action.url) {
        window.open(action.url, '_blank');
      }
    },
    openHelpCenter() {
      this.$emit('open-help-center');
    },
    askInChat() {
      const topic = this.helpContent ? this.helpContent.title : 'using this page';
      this.$emit('ask-in-chat', `Can you help me with ${topic}?`);
    },
    startTour() {
      this.$emit('start-tour');
    }
  }
};
</script>

<style scoped>
.contextual-help {
  max-width: 600px;
  margin: 0 auto;
}

:deep(ul) {
  padding-left: 1.5rem;
}
</style>
