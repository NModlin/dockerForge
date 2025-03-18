<template>
  <div class="settings">
    <h1 class="text-h4 mb-4">Settings</h1>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Settings Content -->
    <template v-else>
      <v-tabs v-model="activeTab" background-color="primary" dark>
        <v-tab>General</v-tab>
        <v-tab>Docker</v-tab>
        <v-tab>Security</v-tab>
        <v-tab>Monitoring</v-tab>
        <v-tab>Backup</v-tab>
        <v-tab>Notifications</v-tab>
        <v-tab>Advanced</v-tab>
      </v-tabs>

      <v-tabs-items v-model="activeTab">
        <!-- General Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">General Settings</h2>
              
              <v-form ref="generalForm" v-model="generalFormValid">
                <v-switch
                  v-model="settings.general.darkMode"
                  label="Dark Mode"
                  hint="Enable dark mode for the UI"
                  persistent-hint
                ></v-switch>
                
                <v-select
                  v-model="settings.general.language"
                  :items="languageOptions"
                  label="Language"
                  hint="Select your preferred language"
                  persistent-hint
                  class="mt-4"
                ></v-select>
                
                <v-select
                  v-model="settings.general.dateFormat"
                  :items="dateFormatOptions"
                  label="Date Format"
                  hint="Select your preferred date format"
                  persistent-hint
                  class="mt-4"
                ></v-select>
                
                <v-text-field
                  v-model="settings.general.refreshInterval"
                  label="Auto-refresh Interval (seconds)"
                  type="number"
                  hint="Set to 0 to disable auto-refresh"
                  persistent-hint
                  :rules="[v => v >= 0 || 'Interval must be non-negative']"
                  class="mt-4"
                ></v-text-field>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveGeneralSettings"
                  :disabled="!generalFormValid"
                >
                  Save General Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Docker Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Docker Settings</h2>
              
              <v-form ref="dockerForm" v-model="dockerFormValid">
                <v-text-field
                  v-model="settings.docker.socketPath"
                  label="Docker Socket Path"
                  hint="Path to the Docker socket"
                  persistent-hint
                  :rules="[v => !!v || 'Socket path is required']"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.docker.useTLS"
                  label="Use TLS"
                  hint="Enable TLS for Docker API communication"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-text-field
                  v-model="settings.docker.certPath"
                  label="Certificate Path"
                  hint="Path to TLS certificates"
                  persistent-hint
                  :disabled="!settings.docker.useTLS"
                  :rules="[v => !settings.docker.useTLS || !!v || 'Certificate path is required when TLS is enabled']"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.docker.registryUrl"
                  label="Default Registry URL"
                  hint="URL of the default Docker registry"
                  persistent-hint
                  class="mt-4"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.docker.pruneUnused"
                  label="Auto-prune Unused Resources"
                  hint="Automatically remove unused containers, networks, and images"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-select
                  v-model="settings.docker.pruneSchedule"
                  :items="pruneScheduleOptions"
                  label="Prune Schedule"
                  hint="When to automatically prune unused resources"
                  persistent-hint
                  :disabled="!settings.docker.pruneUnused"
                  class="mt-4"
                ></v-select>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveDockerSettings"
                  :disabled="!dockerFormValid"
                >
                  Save Docker Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Security Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Security Settings</h2>
              
              <v-form ref="securityForm" v-model="securityFormValid">
                <v-switch
                  v-model="settings.security.enableVulnerabilityScanning"
                  label="Enable Vulnerability Scanning"
                  hint="Automatically scan images for vulnerabilities"
                  persistent-hint
                ></v-switch>
                
                <v-select
                  v-model="settings.security.scanSchedule"
                  :items="scanScheduleOptions"
                  label="Scan Schedule"
                  hint="When to automatically scan images"
                  persistent-hint
                  :disabled="!settings.security.enableVulnerabilityScanning"
                  class="mt-4"
                ></v-select>
                
                <v-select
                  v-model="settings.security.vulnerabilitySeverity"
                  :items="severityOptions"
                  label="Minimum Vulnerability Severity"
                  hint="Minimum severity level to report"
                  persistent-hint
                  :disabled="!settings.security.enableVulnerabilityScanning"
                  class="mt-4"
                ></v-select>
                
                <v-switch
                  v-model="settings.security.enforceImageSigning"
                  label="Enforce Image Signing"
                  hint="Only allow signed images to be pulled"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-switch
                  v-model="settings.security.restrictPrivilegedContainers"
                  label="Restrict Privileged Containers"
                  hint="Prevent running containers in privileged mode"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveSecuritySettings"
                  :disabled="!securityFormValid"
                >
                  Save Security Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Monitoring Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Monitoring Settings</h2>
              
              <v-form ref="monitoringForm" v-model="monitoringFormValid">
                <v-switch
                  v-model="settings.monitoring.enableResourceMonitoring"
                  label="Enable Resource Monitoring"
                  hint="Monitor CPU, memory, and disk usage"
                  persistent-hint
                ></v-switch>
                
                <v-text-field
                  v-model="settings.monitoring.collectionInterval"
                  label="Collection Interval (seconds)"
                  type="number"
                  hint="How often to collect metrics"
                  persistent-hint
                  :rules="[v => v > 0 || 'Interval must be positive']"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.monitoring.retentionPeriod"
                  label="Data Retention Period (days)"
                  type="number"
                  hint="How long to keep monitoring data"
                  persistent-hint
                  :rules="[v => v > 0 || 'Retention period must be positive']"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.monitoring.enableAnomalyDetection"
                  label="Enable Anomaly Detection"
                  hint="Detect unusual resource usage patterns"
                  persistent-hint
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-switch>
                
                <v-text-field
                  v-model="settings.monitoring.cpuThreshold"
                  label="CPU Alert Threshold (%)"
                  type="number"
                  hint="Alert when CPU usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.monitoring.memoryThreshold"
                  label="Memory Alert Threshold (%)"
                  type="number"
                  hint="Alert when memory usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.monitoring.diskThreshold"
                  label="Disk Alert Threshold (%)"
                  type="number"
                  hint="Alert when disk usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveMonitoringSettings"
                  :disabled="!monitoringFormValid"
                >
                  Save Monitoring Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Backup Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Backup Settings</h2>
              
              <v-form ref="backupForm" v-model="backupFormValid">
                <v-switch
                  v-model="settings.backup.enableAutoBackup"
                  label="Enable Automatic Backups"
                  hint="Automatically backup Docker resources"
                  persistent-hint
                ></v-switch>
                
                <v-select
                  v-model="settings.backup.backupSchedule"
                  :items="backupScheduleOptions"
                  label="Backup Schedule"
                  hint="When to automatically create backups"
                  persistent-hint
                  :disabled="!settings.backup.enableAutoBackup"
                  class="mt-4"
                ></v-select>
                
                <v-text-field
                  v-model="settings.backup.backupLocation"
                  label="Backup Storage Location"
                  hint="Path where backups will be stored"
                  persistent-hint
                  :rules="[v => !!v || 'Backup location is required']"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.backup.retentionCount"
                  label="Backup Retention Count"
                  type="number"
                  hint="Number of backups to keep"
                  persistent-hint
                  :rules="[v => v > 0 || 'Retention count must be positive']"
                  class="mt-4"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.backup.compressBackups"
                  label="Compress Backups"
                  hint="Compress backup files to save space"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-switch
                  v-model="settings.backup.includeVolumes"
                  label="Include Volumes in Backups"
                  hint="Include volume data in backups"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveBackupSettings"
                  :disabled="!backupFormValid"
                >
                  Save Backup Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Notification Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Notification Settings</h2>
              
              <v-form ref="notificationForm" v-model="notificationFormValid">
                <v-switch
                  v-model="settings.notifications.enableEmailNotifications"
                  label="Enable Email Notifications"
                  hint="Send notifications via email"
                  persistent-hint
                ></v-switch>
                
                <v-text-field
                  v-model="settings.notifications.emailRecipients"
                  label="Email Recipients"
                  hint="Comma-separated list of email addresses"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'Email recipients are required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.notifications.smtpServer"
                  label="SMTP Server"
                  hint="SMTP server address"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'SMTP server is required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.notifications.smtpPort"
                  label="SMTP Port"
                  type="number"
                  hint="SMTP server port"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'SMTP port is required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.notifications.enableSlackNotifications"
                  label="Enable Slack Notifications"
                  hint="Send notifications to Slack"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-text-field
                  v-model="settings.notifications.slackWebhookUrl"
                  label="Slack Webhook URL"
                  hint="Webhook URL for Slack integration"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableSlackNotifications || !!v || 'Webhook URL is required'
                  ]"
                  :disabled="!settings.notifications.enableSlackNotifications"
                  class="mt-4"
                ></v-text-field>
                
                <v-select
                  v-model="settings.notifications.notificationEvents"
                  :items="notificationEventOptions"
                  label="Events to Notify"
                  hint="Select which events trigger notifications"
                  persistent-hint
                  multiple
                  chips
                  class="mt-4"
                ></v-select>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveNotificationSettings"
                  :disabled="!notificationFormValid"
                >
                  Save Notification Settings
                </v-btn>
                
                <v-btn
                  color="secondary"
                  class="mt-4 ml-2"
                  @click="testNotifications"
                >
                  Test Notifications
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Advanced Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Advanced Settings</h2>
              
              <v-alert
                type="warning"
                class="mb-4"
              >
                These settings are for advanced users. Incorrect configuration may cause system instability.
              </v-alert>
              
              <v-form ref="advancedForm" v-model="advancedFormValid">
                <v-switch
                  v-model="settings.advanced.enableDebugMode"
                  label="Enable Debug Mode"
                  hint="Enable detailed logging for troubleshooting"
                  persistent-hint
                ></v-switch>
                
                <v-select
                  v-model="settings.advanced.logLevel"
                  :items="logLevelOptions"
                  label="Log Level"
                  hint="Set the logging verbosity"
                  persistent-hint
                  class="mt-4"
                ></v-select>
                
                <v-text-field
                  v-model="settings.advanced.apiRateLimit"
                  label="API Rate Limit (requests per minute)"
                  type="number"
                  hint="Limit API request rate"
                  persistent-hint
                  :rules="[v => v > 0 || 'Rate limit must be positive']"
                  class="mt-4"
                ></v-text-field>
                
                <v-text-field
                  v-model="settings.advanced.sessionTimeout"
                  label="Session Timeout (minutes)"
                  type="number"
                  hint="User session timeout"
                  persistent-hint
                  :rules="[v => v > 0 || 'Timeout must be positive']"
                  class="mt-4"
                ></v-text-field>
                
                <v-switch
                  v-model="settings.advanced.enableTelemetry"
                  label="Enable Telemetry"
                  hint="Send anonymous usage data to help improve DockerForge"
                  persistent-hint
                  class="mt-4"
                ></v-switch>
                
                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveAdvancedSettings"
                  :disabled="!advancedFormValid"
                >
                  Save Advanced Settings
                </v-btn>
                
                <v-btn
                  color="error"
                  class="mt-4 ml-2"
                  @click="showResetDialog"
                >
                  Reset All Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs-items>
    </template>

    <!-- Reset Confirmation Dialog -->
    <v-dialog v-model="resetDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Reset All Settings</v-card-title>
        <v-card-text>
          Are you sure you want to reset all settings to their default values?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="resetDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="resetAllSettings">
            Reset
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="showSuccessSnackbar"
      :timeout="3000"
      color="success"
    >
      {{ successMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="showSuccessSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Settings',
  data() {
    return {
      loading: true,
      error: null,
      activeTab: 0,
      settings: {
        general: {
          darkMode: false,
          language: 'en',
          dateFormat: 'MM/DD/YYYY',
          refreshInterval: 30,
        },
        docker: {
          socketPath: '/var/run/docker.sock',
          useTLS: false,
          certPath: '',
          registryUrl: 'docker.io',
          pruneUnused: true,
          pruneSchedule: 'weekly',
        },
        security: {
          enableVulnerabilityScanning: true,
          scanSchedule: 'daily',
          vulnerabilitySeverity: 'high',
          enforceImageSigning: false,
          restrictPrivilegedContainers: true,
        },
        monitoring: {
          enableResourceMonitoring: true,
          collectionInterval: 60,
          retentionPeriod: 30,
          enableAnomalyDetection: true,
          cpuThreshold: 80,
          memoryThreshold: 80,
          diskThreshold: 85,
        },
        backup: {
          enableAutoBackup: true,
          backupSchedule: 'weekly',
          backupLocation: '/var/lib/dockerforge/backups',
          retentionCount: 5,
          compressBackups: true,
          includeVolumes: true,
        },
        notifications: {
          enableEmailNotifications: false,
          emailRecipients: '',
          smtpServer: '',
          smtpPort: 587,
          enableSlackNotifications: false,
          slackWebhookUrl: '',
          notificationEvents: ['error', 'security'],
        },
        advanced: {
          enableDebugMode: false,
          logLevel: 'info',
          apiRateLimit: 60,
          sessionTimeout: 30,
          enableTelemetry: true,
        },
      },
      generalFormValid: true,
      dockerFormValid: true,
      securityFormValid: true,
      monitoringFormValid: true,
      backupFormValid: true,
      notificationFormValid: true,
      advancedFormValid: true,
      resetDialog: false,
      showSuccessSnackbar: false,
      successMessage: '',
      
      // Options for select inputs
      languageOptions: [
        { text: 'English', value: 'en' },
        { text: 'Spanish', value: 'es' },
        { text: 'French', value: 'fr' },
        { text: 'German', value: 'de' },
        { text: 'Chinese', value: 'zh' },
        { text: 'Japanese', value: 'ja' },
      ],
      dateFormatOptions: [
        { text: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
        { text: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
        { text: 'YYYY-MM-DD', value: 'YYYY-MM-DD' },
      ],
      pruneScheduleOptions: [
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
        { text: 'Monthly', value: 'monthly' },
      ],
      scanScheduleOptions: [
        { text: 'Hourly', value: 'hourly' },
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
      ],
      severityOptions: [
        { text: 'Critical', value: 'critical' },
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      backupScheduleOptions: [
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
        { text: 'Monthly', value: 'monthly' },
      ],
      notificationEventOptions: [
        { text: 'Errors', value: 'error' },
        { text: 'Warnings', value: 'warning' },
        { text: 'Security Issues', value: 'security' },
        { text: 'Resource Alerts', value: 'resource' },
        { text: 'Container Events', value: 'container' },
        { text: 'Backup Events', value: 'backup' },
      ],
      logLevelOptions: [
        { text: 'Error', value: 'error' },
        { text: 'Warning', value: 'warning' },
        { text: 'Info', value: 'info' },
        { text: 'Debug', value: 'debug' },
        { text: 'Trace', value: 'trace' },
      ],
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchSettings();
    
    // Initialize the dark mode setting from the store
    this.settings.general.darkMode = this.$store.getters.darkMode;
  },
  methods: {
    async fetchSettings() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/settings', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.settings = response.data;
        
        // Mock implementation - just use the default settings
        setTimeout(() => {
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load settings. Please try again.';
        this.loading = false;
      }
    },
    async saveGeneralSettings() {
      if (!this.$refs.generalForm.validate()) return;
      
      try {
        // Update the dark mode setting in the store
        this.$store.commit('SET_DARK_MODE', this.settings.general.darkMode);
        
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/general', this.settings.general, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('General settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save general settings';
      }
    },
    async saveDockerSettings() {
      if (!this.$refs.dockerForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/docker', this.settings.docker, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Docker settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save Docker settings';
      }
    },
    async saveSecuritySettings() {
      if (!this.$refs.securityForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/security', this.settings.security, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Security settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save security settings';
      }
    },
    async saveMonitoringSettings() {
      if (!this.$refs.monitoringForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/monitoring', this.settings.monitoring, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Monitoring settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save monitoring settings';
      }
    },
    async saveBackupSettings() {
      if (!this.$refs.backupForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/backup', this.settings.backup, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Backup settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save backup settings';
      }
    },
    async saveNotificationSettings() {
      if (!this.$refs.notificationForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/notifications', this.settings.notifications, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Notification settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save notification settings';
      }
    },
    async saveAdvancedSettings() {
      if (!this.$refs.advancedForm.validate()) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/advanced', this.settings.advanced, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Advanced settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save advanced settings';
      }
    },
    showResetDialog() {
      this.resetDialog = true;
    },
    async resetAllSettings() {
      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/settings/reset', {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation - reset to default values
        this.fetchSettings();
        this.resetDialog = false;
        this.showSuccessMessage('All settings have been reset to defaults');
      } catch (error) {
        this.error = 'Failed to reset settings';
        this.resetDialog = false;
      }
    },
    async testNotifications() {
      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/settings/notifications/test', {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.showSuccessMessage('Test notification sent successfully');
      } catch (error) {
        this.error = 'Failed to send test notification';
      }
    },
    showSuccessMessage(message) {
      this.successMessage = message;
      this.showSuccessSnackbar = true;
    }
  }
};
</script>

<style scoped>
.settings {
  padding: 16px;
}
</style>
