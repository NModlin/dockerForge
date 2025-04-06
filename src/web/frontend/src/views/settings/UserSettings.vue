<template>
  <div class="user-settings">
    <v-card flat>
      <v-card-text>
        <h2 class="text-h5 mb-4">User Preferences</h2>

        <v-alert
          v-if="error"
          type="error"
          dismissible
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-alert
          v-if="success"
          type="success"
          dismissible
          class="mb-4"
        >
          {{ success }}
        </v-alert>

        <v-tabs v-model="activeTab" background-color="primary" dark>
          <v-tab>Appearance</v-tab>
          <v-tab>Notifications</v-tab>
          <v-tab>Display</v-tab>
          <v-tab>Keyboard</v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <!-- Appearance Settings -->
          <v-tab-item>
            <v-form ref="appearanceForm" v-model="appearanceFormValid" class="mt-4">
              <v-select
                v-model="preferences.theme"
                :items="themeOptions"
                :label="$t('settings.appearance.theme')"
                :hint="$t('settings.appearance.theme')"
                persistent-hint
              >
                <template v-slot:selection="{ item }">
                  <v-chip :color="getThemeColor(item.raw.value)" class="mr-2">
                    <v-icon start>mdi-palette</v-icon>
                    {{ item.title }}
                  </v-chip>
                </template>
                <template v-slot:item="{ item, props }">
                  <v-list-item v-bind="props">
                    <template v-slot:prepend>
                      <v-avatar :color="getThemeColor(item.raw.value)" size="24" class="mr-2"></v-avatar>
                    </template>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                  </v-list-item>
                </template>
              </v-select>

              <v-select
                v-model="preferences.language"
                :items="languageOptions"
                :label="$t('settings.appearance.language')"
                :hint="$t('settings.appearance.language')"
                persistent-hint
                class="mt-4"
              >
                <template v-slot:selection="{ item }">
                  <v-chip class="mr-2">
                    <v-icon start>mdi-translate</v-icon>
                    {{ item.title }}
                  </v-chip>
                </template>
              </v-select>

              <v-select
                v-model="preferences.dateFormat"
                :items="dateFormatOptions"
                label="Date Format"
                hint="Select your preferred date format"
                persistent-hint
                class="mt-4"
              ></v-select>

              <v-select
                v-model="preferences.timeFormat"
                :items="timeFormatOptions"
                label="Time Format"
                hint="Select your preferred time format"
                persistent-hint
                class="mt-4"
              ></v-select>

              <v-btn
                color="primary"
                class="mt-4"
                @click="saveAppearanceSettings"
                :disabled="!appearanceFormValid || loading"
                :loading="loading"
              >
                Save Appearance Settings
              </v-btn>
            </v-form>
          </v-tab-item>

          <!-- Notification Settings -->
          <v-tab-item>
            <v-form ref="notificationForm" v-model="notificationFormValid" class="mt-4">
              <v-switch
                v-model="preferences.notifications.enabled"
                :label="$t('settings.notifications.enable')"
                hint="Receive notifications about important events"
                persistent-hint
                color="primary"
              >
                <template v-slot:label>
                  <div>
                    <span>{{ $t('settings.notifications.enable') }}</span>
                    <v-tooltip location="right">
                      <template v-slot:activator="{ props }">
                        <v-icon v-bind="props" size="small" class="ml-1">mdi-information-outline</v-icon>
                      </template>
                      <span>Receive notifications about important events</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-switch>

              <v-switch
                v-model="preferences.notifications.desktop"
                :label="$t('settings.notifications.desktop')"
                hint="Show notifications on your desktop"
                persistent-hint
                :disabled="!preferences.notifications.enabled"
                color="primary"
                class="mt-4"
              >
                <template v-slot:label>
                  <div class="d-flex align-center">
                    <v-icon class="mr-2">mdi-desktop-mac</v-icon>
                    <span>{{ $t('settings.notifications.desktop') }}</span>
                  </div>
                </template>
              </v-switch>

              <v-switch
                v-model="preferences.notifications.email"
                :label="$t('settings.notifications.email')"
                hint="Receive notifications via email"
                persistent-hint
                :disabled="!preferences.notifications.enabled"
                color="primary"
                class="mt-4"
              >
                <template v-slot:label>
                  <div class="d-flex align-center">
                    <v-icon class="mr-2">mdi-email-outline</v-icon>
                    <span>{{ $t('settings.notifications.email') }}</span>
                  </div>
                </template>
              </v-switch>

              <v-text-field
                v-model="preferences.notifications.emailAddress"
                :label="$t('settings.notifications.emailAddress')"
                hint="Email address for notifications"
                persistent-hint
                :rules="[
                  v => !preferences.notifications.email || !!v || 'Email address is required',
                  v => !preferences.notifications.email || !v || /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) || 'Email address must be valid'
                ]"
                :disabled="!preferences.notifications.enabled || !preferences.notifications.email"
                class="mt-4"
                prepend-inner-icon="mdi-email"
                clearable
              ></v-text-field>

              <v-select
                v-model="preferences.notifications.events"
                :items="notificationEventOptions"
                :label="$t('settings.notifications.events')"
                hint="Select which events trigger notifications"
                persistent-hint
                multiple
                chips
                :disabled="!preferences.notifications.enabled"
                class="mt-4"
                prepend-inner-icon="mdi-bell-outline"
              >
                <template v-slot:selection="{ item }">
                  <v-chip
                    :color="getEventColor(item.raw.value)"
                    class="mr-1"
                    size="small"
                  >
                    <v-icon start size="x-small">{{ getEventIcon(item.raw.value) }}</v-icon>
                    {{ item.title }}
                  </v-chip>
                </template>
                <template v-slot:item="{ item, props }">
                  <v-list-item v-bind="props">
                    <template v-slot:prepend>
                      <v-icon :color="getEventColor(item.raw.value)" size="small">{{ getEventIcon(item.raw.value) }}</v-icon>
                    </template>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                  </v-list-item>
                </template>
              </v-select>

              <v-btn
                color="primary"
                class="mt-4"
                @click="saveNotificationSettings"
                :disabled="!notificationFormValid || loading"
                :loading="loading"
              >
                Save Notification Settings
              </v-btn>

              <v-btn
                color="secondary"
                class="mt-4 ml-2"
                @click="testNotifications"
                :disabled="!preferences.notifications.enabled || loading"
                :loading="testingNotifications"
              >
                Test Notifications
              </v-btn>
            </v-form>
          </v-tab-item>

          <!-- Display Settings -->
          <v-tab-item>
            <v-form ref="displayForm" v-model="displayFormValid" class="mt-4">
              <v-card class="mb-4 pa-3" variant="outlined">
                <v-card-title class="text-subtitle-1">Layout Options</v-card-title>
                <v-card-text>
                  <v-switch
                    v-model="preferences.display.compactView"
                    :label="$t('settings.display.compactView')"
                    :hint="$t('settings.display.compactViewHint')"
                    persistent-hint
                    color="primary"
                  >
                    <template v-slot:label>
                      <div class="d-flex align-center">
                        <v-icon class="mr-2">mdi-view-compact</v-icon>
                        <span>{{ $t('settings.display.compactView') }}</span>
                      </div>
                    </template>
                  </v-switch>

                  <v-switch
                    v-model="preferences.display.showSystemContainers"
                    :label="$t('settings.display.showSystemContainers')"
                    :hint="$t('settings.display.showSystemContainersHint')"
                    persistent-hint
                    color="primary"
                    class="mt-4"
                  >
                    <template v-slot:label>
                      <div class="d-flex align-center">
                        <v-icon class="mr-2">mdi-docker</v-icon>
                        <span>{{ $t('settings.display.showSystemContainers') }}</span>
                      </div>
                    </template>
                  </v-switch>
                </v-card-text>
              </v-card>

              <v-card class="mb-4 pa-3" variant="outlined">
                <v-card-title class="text-subtitle-1">Display Preferences</v-card-title>
                <v-card-text>
                  <v-text-field
                    v-model="preferences.display.refreshInterval"
                    :label="$t('settings.display.refreshInterval')"
                    type="number"
                    :hint="$t('settings.display.refreshIntervalHint')"
                    persistent-hint
                    :rules="[v => v >= 0 || 'Interval must be non-negative']"
                    prepend-inner-icon="mdi-refresh"
                    suffix="seconds"
                  ></v-text-field>

                  <v-select
                    v-model="preferences.display.defaultPage"
                    :items="defaultPageOptions"
                    :label="$t('settings.display.defaultPage')"
                    :hint="$t('settings.display.defaultPageHint')"
                    persistent-hint
                    class="mt-4"
                    prepend-inner-icon="mdi-home"
                  >
                    <template v-slot:selection="{ item }">
                      <v-chip class="mr-2">
                        <v-icon start>{{ getPageIcon(item.raw.value) }}</v-icon>
                        {{ item.title }}
                      </v-chip>
                    </template>
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-icon>{{ getPageIcon(item.raw.value) }}</v-icon>
                        </template>
                        <v-list-item-title>{{ item.title }}</v-list-item-title>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-card-text>
              </v-card>

              <v-btn
                color="primary"
                class="mt-4"
                @click="saveDisplaySettings"
                :disabled="!displayFormValid || loading"
                :loading="loading"
              >
                Save Display Settings
              </v-btn>
            </v-form>
          </v-tab-item>

          <!-- Keyboard Settings -->
          <v-tab-item>
            <v-form ref="keyboardForm" v-model="keyboardFormValid" class="mt-4">
              <v-switch
                v-model="preferences.keyboard.enableShortcuts"
                label="Enable Keyboard Shortcuts"
                hint="Use keyboard shortcuts for common actions"
                persistent-hint
              ></v-switch>

              <div v-if="preferences.keyboard.enableShortcuts" class="mt-4">
                <h3 class="text-subtitle-1 mb-2">Keyboard Shortcuts</h3>
                <p class="text-caption mb-4">Customize keyboard shortcuts for common actions.</p>

                <v-simple-table>
                  <template v-slot:default>
                    <thead>
                      <tr>
                        <th>Action</th>
                        <th>Shortcut</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(shortcut, action) in keyboardShortcuts" :key="action">
                        <td>{{ getActionName(action) }}</td>
                        <td>
                          <v-text-field
                            v-model="keyboardShortcuts[action]"
                            dense
                            hide-details
                            single-line
                            placeholder="e.g., Ctrl+S"
                            @focus="startRecordingShortcut(action)"
                            @blur="stopRecordingShortcut"
                            :readonly="recordingShortcut === action"
                          ></v-text-field>
                        </td>
                        <td>
                          <v-btn
                            icon
                            small
                            @click="resetShortcut(action)"
                            :disabled="keyboardShortcuts[action] === defaultShortcuts[action]"
                          >
                            <v-icon>mdi-refresh</v-icon>
                          </v-btn>
                        </td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </div>

              <v-btn
                color="primary"
                class="mt-4"
                @click="saveKeyboardSettings"
                :disabled="!keyboardFormValid || loading"
                :loading="loading"
              >
                Save Keyboard Settings
              </v-btn>
            </v-form>
          </v-tab-item>
        </v-tabs-items>

        <v-divider class="my-4"></v-divider>

        <v-btn
          color="error"
          @click="showResetDialog"
          :disabled="loading"
        >
          Reset All Preferences
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Reset Confirmation Dialog -->
    <v-dialog v-model="resetDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Reset All Preferences</v-card-title>
        <v-card-text>
          Are you sure you want to reset all user preferences to their default values?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="resetDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="resetAllPreferences">
            Reset
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'UserSettings',
  data() {
    return {
      activeTab: 0,
      error: null,
      success: null,
      loading: false,
      testingNotifications: false,
      resetDialog: false,
      recordingShortcut: null,

      // Form validation
      appearanceFormValid: true,
      notificationFormValid: true,
      displayFormValid: true,
      keyboardFormValid: true,

      // Local copy of preferences for editing
      preferences: {
        theme: 'light',
        language: 'en',
        dateFormat: 'MM/DD/YYYY',
        timeFormat: '24h',
        notifications: {
          enabled: true,
          desktop: true,
          email: false,
          emailAddress: '',
          events: ['error', 'security']
        },
        display: {
          compactView: false,
          showSystemContainers: false,
          refreshInterval: 30,
          defaultPage: 'dashboard'
        },
        keyboard: {
          enableShortcuts: true,
          customShortcuts: {}
        }
      },

      // Keyboard shortcuts
      keyboardShortcuts: {},
      defaultShortcuts: {
        'refresh': 'F5',
        'search': 'Ctrl+F',
        'save': 'Ctrl+S',
        'new-container': 'Ctrl+N',
        'help': 'F1',
        'toggle-sidebar': 'Ctrl+B',
        'toggle-chat': 'Ctrl+Shift+C',
        'toggle-dark-mode': 'Ctrl+Shift+D'
      },

      // Options for select inputs
      themeOptions: [
        { text: this.$t('settings.appearance.themeOptions.light'), value: 'light' },
        { text: this.$t('settings.appearance.themeOptions.dark'), value: 'dark' },
        { text: this.$t('settings.appearance.themeOptions.highContrast') || 'High Contrast', value: 'highContrast' },
        { text: this.$t('settings.appearance.themeOptions.system'), value: 'system' },
        { text: this.$t('settings.appearance.themeOptions.blue'), value: 'blue' },
        { text: this.$t('settings.appearance.themeOptions.green'), value: 'green' },
        { text: this.$t('settings.appearance.themeOptions.purple'), value: 'purple' },
        { text: this.$t('settings.appearance.themeOptions.orange'), value: 'orange' },
        { text: this.$t('settings.appearance.themeOptions.red'), value: 'red' }
      ],
      languageOptions: [
        { text: 'English', value: 'en' },
        { text: 'Español', value: 'es' },
        { text: 'Français', value: 'fr' },
        { text: 'Deutsch', value: 'de' },
        { text: '中文', value: 'zh' },
        { text: '日本語', value: 'ja' }
      ],
      dateFormatOptions: [
        { text: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
        { text: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
        { text: 'YYYY-MM-DD', value: 'YYYY-MM-DD' }
      ],
      timeFormatOptions: [
        { text: '24-hour (14:30)', value: '24h' },
        { text: '12-hour (2:30 PM)', value: '12h' }
      ],
      notificationEventOptions: [
        { text: 'Errors', value: 'error' },
        { text: 'Warnings', value: 'warning' },
        { text: 'Security Issues', value: 'security' },
        { text: 'Resource Alerts', value: 'resource' },
        { text: 'Container Events', value: 'container' },
        { text: 'Image Events', value: 'image' },
        { text: 'Volume Events', value: 'volume' },
        { text: 'Network Events', value: 'network' },
        { text: 'Backup Events', value: 'backup' }
      ],
      defaultPageOptions: [
        { text: 'Dashboard', value: 'dashboard' },
        { text: 'Containers', value: 'containers' },
        { text: 'Images', value: 'images' },
        { text: 'Volumes', value: 'volumes' },
        { text: 'Networks', value: 'networks' },
        { text: 'Compose', value: 'compose' }
      ]
    };
  },
  computed: {
    ...mapState('settings', ['userPreferences']),
    ...mapGetters('settings', ['getUserPreferences'])
  },
  created() {
    // Initialize preferences from store
    this.initializePreferences();

    // Initialize keyboard shortcuts
    this.initializeKeyboardShortcuts();

    // Add keyboard event listener for shortcut recording
    window.addEventListener('keydown', this.handleKeyDown);
  },
  beforeDestroy() {
    // Remove keyboard event listener
    window.removeEventListener('keydown', this.handleKeyDown);
  },
  methods: {
    ...mapActions('settings', [
      'fetchUserPreferences',
      'saveUserPreferences',
      'updateNotificationSettings',
      'updateDisplaySettings',
      'updateKeyboardSettings',
      'resetUserPreferences'
    ]),

    async initializePreferences() {
      this.loading = true;
      try {
        // Fetch preferences from the store/API
        await this.fetchUserPreferences();

        // Copy preferences to local state for editing
        this.preferences = JSON.parse(JSON.stringify(this.getUserPreferences));
      } catch (error) {
        this.error = 'Failed to load user preferences';
        console.error('Error loading preferences:', error);
      } finally {
        this.loading = false;
      }
    },

    initializeKeyboardShortcuts() {
      // Initialize with default shortcuts
      this.keyboardShortcuts = { ...this.defaultShortcuts };

      // Override with custom shortcuts if available
      if (this.preferences.keyboard && this.preferences.keyboard.customShortcuts) {
        Object.keys(this.preferences.keyboard.customShortcuts).forEach(action => {
          this.keyboardShortcuts[action] = this.preferences.keyboard.customShortcuts[action];
        });
      }
    },

    async saveAppearanceSettings() {
      if (!this.$refs.appearanceForm.validate()) return;

      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Extract appearance settings
        const { theme, language, dateFormat, timeFormat } = this.preferences;

        // Save to store/API
        await this.saveUserPreferences({ theme, language, dateFormat, timeFormat });

        // Apply theme immediately
        this.applyTheme(theme);

        // Apply language immediately
        this.applyLanguage(language);

        this.success = this.$t('settings.appearance.saveSuccess') || 'Appearance settings saved successfully';
      } catch (error) {
        this.error = this.$t('settings.appearance.saveError') || 'Failed to save appearance settings';
        console.error('Error saving appearance settings:', error);
      } finally {
        this.loading = false;
      }
    },

    // Apply theme
    applyTheme(themeName) {
      // Import dynamically to avoid circular dependencies
      import('../../themes').then(({ applyTheme }) => {
        applyTheme(themeName, this.$vuetify);
      });
    },

    // Apply language
    applyLanguage(lang) {
      this.$i18n.locale = lang;
      localStorage.setItem('language', lang);
      document.documentElement.setAttribute('lang', lang);
    },

    // Get theme color for display
    getThemeColor(themeName) {
      const themeColors = {
        light: '#F8F9FA',
        dark: '#212529',
        highContrast: '#FFFF00',
        system: '#6C757D',
        blue: '#1976D2',
        green: '#388E3C',
        purple: '#6A1B9A',
        orange: '#E65100',
        red: '#C62828'
      };
      return themeColors[themeName] || themeColors.light;
    },

    // Get event color for notification events
    getEventColor(eventType) {
      const eventColors = {
        error: 'error',
        warning: 'warning',
        security: 'deep-purple',
        resource: 'orange',
        container: 'primary',
        image: 'indigo',
        volume: 'teal',
        network: 'cyan',
        backup: 'green'
      };
      return eventColors[eventType] || 'grey';
    },

    // Get event icon for notification events
    getEventIcon(eventType) {
      const eventIcons = {
        error: 'mdi-alert-circle',
        warning: 'mdi-alert',
        security: 'mdi-shield-alert',
        resource: 'mdi-chart-line',
        container: 'mdi-docker',
        image: 'mdi-image',
        volume: 'mdi-database',
        network: 'mdi-lan',
        backup: 'mdi-backup-restore'
      };
      return eventIcons[eventType] || 'mdi-bell';
    },

    // Get icon for page
    getPageIcon(page) {
      const pageIcons = {
        dashboard: 'mdi-view-dashboard',
        containers: 'mdi-docker',
        images: 'mdi-image-multiple',
        volumes: 'mdi-database',
        networks: 'mdi-lan',
        compose: 'mdi-file-document',
        security: 'mdi-shield',
        settings: 'mdi-cog'
      };
      return pageIcons[page] || 'mdi-home';
    },

    async saveNotificationSettings() {
      if (!this.$refs.notificationForm.validate()) return;

      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Save to store/API
        await this.updateNotificationSettings(this.preferences.notifications);

        this.success = 'Notification settings saved successfully';
      } catch (error) {
        this.error = 'Failed to save notification settings';
        console.error('Error saving notification settings:', error);
      } finally {
        this.loading = false;
      }
    },

    async saveDisplaySettings() {
      if (!this.$refs.displayForm.validate()) return;

      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Save to store/API
        await this.updateDisplaySettings(this.preferences.display);

        this.success = 'Display settings saved successfully';
      } catch (error) {
        this.error = 'Failed to save display settings';
        console.error('Error saving display settings:', error);
      } finally {
        this.loading = false;
      }
    },

    async saveKeyboardSettings() {
      if (!this.$refs.keyboardForm.validate()) return;

      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Prepare custom shortcuts
        const customShortcuts = {};

        // Only save shortcuts that differ from defaults
        Object.keys(this.keyboardShortcuts).forEach(action => {
          if (this.keyboardShortcuts[action] !== this.defaultShortcuts[action]) {
            customShortcuts[action] = this.keyboardShortcuts[action];
          }
        });

        // Update keyboard settings
        const keyboardSettings = {
          enableShortcuts: this.preferences.keyboard.enableShortcuts,
          customShortcuts
        };

        // Save to store/API
        await this.updateKeyboardSettings(keyboardSettings);

        this.success = 'Keyboard settings saved successfully';
      } catch (error) {
        this.error = 'Failed to save keyboard settings';
        console.error('Error saving keyboard settings:', error);
      } finally {
        this.loading = false;
      }
    },

    async testNotifications() {
      this.testingNotifications = true;
      this.error = null;
      this.success = null;

      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/settings/notifications/test');

        // Mock implementation
        await new Promise(resolve => setTimeout(resolve, 1000));

        this.success = 'Test notification sent successfully';
      } catch (error) {
        this.error = 'Failed to send test notification';
        console.error('Error sending test notification:', error);
      } finally {
        this.testingNotifications = false;
      }
    },

    showResetDialog() {
      this.resetDialog = true;
    },

    async resetAllPreferences() {
      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Reset preferences in store/API
        const defaultPreferences = await this.resetUserPreferences();

        // Update local state
        this.preferences = JSON.parse(JSON.stringify(defaultPreferences));

        // Reset keyboard shortcuts
        this.keyboardShortcuts = { ...this.defaultShortcuts };

        this.success = 'All preferences have been reset to defaults';
        this.resetDialog = false;
      } catch (error) {
        this.error = 'Failed to reset preferences';
        console.error('Error resetting preferences:', error);
      } finally {
        this.loading = false;
      }
    },

    // Keyboard shortcut recording
    startRecordingShortcut(action) {
      this.recordingShortcut = action;
    },

    stopRecordingShortcut() {
      this.recordingShortcut = null;
    },

    handleKeyDown(event) {
      if (!this.recordingShortcut) return;

      // Prevent default browser actions
      event.preventDefault();

      // Build shortcut string
      const keys = [];
      if (event.ctrlKey) keys.push('Ctrl');
      if (event.shiftKey) keys.push('Shift');
      if (event.altKey) keys.push('Alt');
      if (event.metaKey) keys.push('Meta');

      // Add the key if it's not a modifier
      const key = event.key;
      if (!['Control', 'Shift', 'Alt', 'Meta'].includes(key)) {
        keys.push(key === ' ' ? 'Space' : key.length === 1 ? key.toUpperCase() : key);
      }

      // Set the shortcut
      if (keys.length > 0) {
        this.keyboardShortcuts[this.recordingShortcut] = keys.join('+');
      }

      // Stop recording
      this.stopRecordingShortcut();
    },

    resetShortcut(action) {
      this.keyboardShortcuts[action] = this.defaultShortcuts[action];
    },

    getActionName(action) {
      // Convert action ID to display name
      const actionNames = {
        'refresh': 'Refresh',
        'search': 'Search',
        'save': 'Save',
        'new-container': 'New Container',
        'help': 'Help',
        'toggle-sidebar': 'Toggle Sidebar',
        'toggle-chat': 'Toggle Chat',
        'toggle-dark-mode': 'Toggle Dark Mode'
      };

      return actionNames[action] || action;
    }
  }
};
</script>

<style scoped>
.user-settings {
  max-width: 100%;
}
</style>
