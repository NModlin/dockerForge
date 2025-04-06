<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon v-if="isAuthenticated" @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title class="cursor-pointer" @click="$router.push('/')">DockerForge</v-toolbar-title>

      <!-- Quick Actions Menu -->
      <v-menu v-if="isAuthenticated" offset-y left>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            text
            class="ml-4"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon left>mdi-lightning-bolt</v-icon>
            Quick Actions
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/containers/create">
            <v-list-item-icon>
              <v-icon>mdi-plus-circle</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>New Container</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/images/pull">
            <v-list-item-icon>
              <v-icon>mdi-cloud-download</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Pull Image</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/compose/create">
            <v-list-item-icon>
              <v-icon>mdi-file-plus</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>New Compose Project</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-divider></v-divider>

          <v-list-item to="/security/scan">
            <v-list-item-icon>
              <v-icon>mdi-shield-search</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Security Scan</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/backup/create">
            <v-list-item-icon>
              <v-icon>mdi-backup-restore</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Create Backup</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-menu>

      <v-spacer></v-spacer>

      <template v-if="isAuthenticated">
        <!-- Search -->
        <v-btn icon @click="showSearch = !showSearch">
          <v-icon>mdi-magnify</v-icon>
        </v-btn>

        <!-- Global Search Overlay -->
        <v-dialog v-model="showSearch" max-width="600px" transition="dialog-top-transition">
          <v-card>
            <v-card-title class="headline">Search DockerForge</v-card-title>
            <v-card-text>
              <v-text-field
                v-model="searchQuery"
                label="Search for containers, images, volumes..."
                prepend-icon="mdi-magnify"
                clearable
                autofocus
                @keydown.enter="performSearch"
              ></v-text-field>

              <v-radio-group v-model="searchType" row>
                <v-radio label="All" value="all"></v-radio>
                <v-radio label="Containers" value="containers"></v-radio>
                <v-radio label="Images" value="images"></v-radio>
                <v-radio label="Volumes" value="volumes"></v-radio>
                <v-radio label="Networks" value="networks"></v-radio>
              </v-radio-group>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text @click="showSearch = false">Cancel</v-btn>
              <v-btn color="primary" @click="performSearch">Search</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Notifications -->
        <v-menu offset-y left>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-badge
                :content="unreadNotifications"
                :value="unreadNotifications > 0"
                color="error"
                overlap
              >
                <v-icon>mdi-bell</v-icon>
              </v-badge>
            </v-btn>
          </template>
          <v-list width="320">
            <v-subheader>
              Notifications
              <v-spacer></v-spacer>
              <v-btn x-small text color="primary" @click="markAllAsRead">Mark all as read</v-btn>
            </v-subheader>
            <v-divider></v-divider>

            <template v-if="notifications.length > 0">
              <v-list-item
                v-for="notification in notifications"
                :key="notification.id"
                :class="{ 'grey lighten-4': !notification.read }"
              >
                <v-list-item-avatar>
                  <v-icon :color="getNotificationColor(notification.type)">
                    {{ getNotificationIcon(notification.type) }}
                  </v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>{{ notification.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ notification.message }}</v-list-item-subtitle>
                  <v-list-item-subtitle class="text-caption">
                    {{ formatNotificationTime(notification.timestamp) }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn icon x-small @click="dismissNotification(notification.id)">
                    <v-icon small>mdi-close</v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </template>

            <v-list-item v-if="notifications.length === 0">
              <v-list-item-content class="text-center">
                <v-icon large color="grey lighten-1">mdi-bell-off</v-icon>
                <p class="text-body-2 mt-2">No notifications</p>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>
            <v-list-item to="/notifications" link>
              <v-list-item-content class="text-center">
                <v-list-item-title class="text-caption">View All Notifications</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-menu>

        <!-- Help Menu -->
        <v-menu offset-y left>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon>mdi-help-circle</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item to="/help">
              <v-list-item-icon>
                <v-icon>mdi-book-open-variant</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Documentation</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item @click="startTour">
              <v-list-item-icon>
                <v-icon>mdi-compass</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Guided Tour</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item href="https://github.com/NModlin/dockerForge" target="_blank">
              <v-list-item-icon>
                <v-icon>mdi-github</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>GitHub Repository</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item @click="reportIssue">
              <v-list-item-icon>
                <v-icon>mdi-bug</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Report Issue</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item @click="showAboutDialog = true">
              <v-list-item-icon>
                <v-icon>mdi-information</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>About DockerForge</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-menu>

        <!-- AI Chat Toggle Button -->
        <v-btn icon @click="toggleChat" v-tooltip="'AI Assistant'">
          <v-icon>mdi-robot</v-icon>
        </v-btn>

        <!-- User Menu -->
        <v-menu offset-y left>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon>mdi-account</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="font-weight-bold">{{ currentUser?.username || 'User' }}</v-list-item-title>
                <v-list-item-subtitle>{{ currentUser?.email || '' }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item to="/profile">
              <v-list-item-icon>
                <v-icon>mdi-account-edit</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>My Profile</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item to="/settings">
              <v-list-item-icon>
                <v-icon>mdi-cog</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Settings</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item @click="logout">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>Logout</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-app-bar>

    <!-- About Dialog -->
    <v-dialog v-model="showAboutDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">About DockerForge</v-card-title>
        <v-card-text>
          <div class="text-center mb-4">
            <v-avatar size="80" color="primary" class="white--text">
              <v-icon size="48">mdi-docker</v-icon>
            </v-avatar>
            <h2 class="mt-2">DockerForge</h2>
            <p class="text-body-2">Version 1.0.0</p>
          </div>

          <p>DockerForge is a comprehensive Docker management platform that provides an intuitive web interface for managing containers, images, volumes, networks, and more.</p>

          <p>Built with:</p>
          <ul>
            <li>Vue.js & Vuetify</li>
            <li>FastAPI</li>
            <li>Docker SDK for Python</li>
          </ul>

          <p class="text-caption mt-4">&copy; {{ new Date().getFullYear() }} DockerForge. All rights reserved.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="showAboutDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-navigation-drawer v-if="isAuthenticated" v-model="drawer" app>
      <!-- User profile section -->
      <v-list-item class="px-2">
        <v-list-item-avatar>
          <v-icon>mdi-account-circle</v-icon>
        </v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>{{ currentUser?.username || 'User' }}</v-list-item-title>
          <v-list-item-subtitle>{{ currentUser?.email || '' }}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <!-- Main navigation -->
      <v-list nav dense>
        <!-- Dashboard -->
        <v-list-item to="/" link>
          <v-list-item-icon>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- Docker Resources Group -->
        <v-list-group
          :value="true"
          prepend-icon="mdi-docker"
        >
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title>Docker Resources</v-list-item-title>
            </v-list-item-content>
          </template>

          <v-list-item to="/containers" link>
            <v-list-item-icon>
              <v-icon>mdi-cube</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Containers</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/images" link>
            <v-list-item-icon>
              <v-icon>mdi-package-variant-closed</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Images</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/volumes" link>
            <v-list-item-icon>
              <v-icon>mdi-database</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Volumes</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/networks" link>
            <v-list-item-icon>
              <v-icon>mdi-lan</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Networks</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <!-- Compose Group -->
        <v-list-group
          prepend-icon="mdi-file-document-multiple"
        >
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title>Compose</v-list-item-title>
            </v-list-item-content>
          </template>

          <v-list-item to="/compose" link>
            <v-list-item-icon>
              <v-icon>mdi-view-list</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Projects</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/compose/create" link>
            <v-list-item-icon>
              <v-icon>mdi-plus</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>New Project</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/compose/editor" link>
            <v-list-item-icon>
              <v-icon>mdi-file-edit</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Compose Editor</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <!-- Management Group -->
        <v-list-group
          prepend-icon="mdi-tools"
        >
          <template v-slot:activator>
            <v-list-item-content>
              <v-list-item-title>Management</v-list-item-title>
            </v-list-item-content>
          </template>

          <v-list-item to="/security" link>
            <v-list-item-icon>
              <v-icon>mdi-shield</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Security</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/backup" link>
            <v-list-item-icon>
              <v-icon>mdi-backup-restore</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Backup</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-list-item to="/monitoring" link>
            <v-list-item-icon>
              <v-icon>mdi-chart-line</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Monitoring</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <!-- Settings -->
        <v-list-item to="/settings" link>
          <v-list-item-icon>
            <v-icon>mdi-cog</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <!-- Help -->
        <v-list-item to="/help" link>
          <v-list-item-icon>
            <v-icon>mdi-help-circle</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Help</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn block color="primary" @click="toggleTheme">
            <v-icon left>{{ isDarkMode ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
            {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} DockerForge</span>
    </v-footer>

    <!-- AI Chat Sidebar -->
    <chat-sidebar v-model="isChatSidebarOpen" />

    <!-- Global Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      :multi-line="snackbar.multiLine"
      :vertical="snackbar.vertical"
      :top="snackbar.top"
    >
      {{ snackbar.text }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import ChatSidebar from './components/chat/ChatSidebar.vue';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'App',
  components: {
    ChatSidebar
  },
  data() {
    return {
      drawer: true,
      showSearch: false,
      searchQuery: '',
      searchType: 'all',
      showAboutDialog: false,
      notifications: [
        {
          id: 1,
          type: 'info',
          title: 'Welcome to DockerForge',
          message: 'Get started by exploring the dashboard.',
          timestamp: new Date().toISOString(),
          read: false
        },
        {
          id: 2,
          type: 'warning',
          title: 'Container Warning',
          message: 'Container web-server is using over 80% CPU.',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          read: false
        },
        {
          id: 3,
          type: 'error',
          title: 'Image Pull Failed',
          message: 'Failed to pull image nginx:latest.',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          read: true
        }
      ],
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        timeout: 3000,
        multiLine: false,
        vertical: false,
        top: false
      }
  },
  created() {
    // Apply the theme from store
    this.applyTheme();

    // Initialize auth state from localStorage
    this.$store.dispatch('auth/init');

    // Add navigation guard to protect routes
    this.$router.beforeEach((to, from, next) => {
      const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
      const isAuthenticated = this.$store.getters['auth/isAuthenticated'];
      const passwordChangeRequired = this.$store.getters['auth/passwordChangeRequired'];

      if (requiresAuth && !isAuthenticated) {
        // Redirect to login page if not authenticated
        next('/login');
      } else if (to.path === '/login' && isAuthenticated) {
        // Redirect to dashboard if already authenticated
        next('/');
      } else if (passwordChangeRequired && to.path !== '/change-password' && isAuthenticated) {
        // Redirect to password change page if password change is required
        next({ path: '/change-password', query: { forced: 'true' } });
      } else {
        next();
      }
    });

    // Update context based on route
    this.$router.afterEach((to) => {
      // Get current page from route
      const path = to.path.split('/')[1] || 'dashboard';

      // Update chat context
      this.updateChatContext({
        currentPage: path
      });

      // Add additional context based on route params
      if (to.params.containerId) {
        this.updateChatContext({
          currentContainerId: to.params.containerId
        });
      } else if (to.params.imageId) {
        this.updateChatContext({
          currentImageId: to.params.imageId
        });
      }
    });

    // Listen for snackbar events
    window.addEventListener('show-snackbar', this.handleSnackbarEvent);
  },

  beforeUnmount() {
    // Remove event listener when component is unmounted
    window.removeEventListener('show-snackbar', this.handleSnackbarEvent);
  },
  computed: {
    ...mapGetters('chat', ['isActive']),
    isAuthenticated() {
      return this.$store.getters['auth/isAuthenticated'];
    },
    currentUser() {
      return this.$store.getters['auth/user'];
    },
    isDarkMode() {
      return this.$store.getters.darkMode;
    },
    isChatSidebarOpen: {
      get() {
        return this.isActive;
      },
      set(value) {
        this.$store.commit('chat/SET_ACTIVE', value);
      }
    },
    unreadNotifications() {
      return this.notifications.filter(n => !n.read).length;
    }
  },
  methods: {
    ...mapActions('chat', ['toggleChat', 'updateContext']),
    logout() {
      this.$store.dispatch('auth/logout');
      this.$router.push('/login');
    },
    applyTheme() {
      // Set theme based on store value
      this.$vuetify.theme.global.name = this.isDarkMode ? 'dark' : 'light';
    },
    updateChatContext(contextData) {
      this.updateContext(contextData);
    },
    toggleTheme() {
      this.$store.commit('SET_DARK_MODE', !this.isDarkMode);
    },
    performSearch() {
      if (!this.searchQuery.trim()) return;

      // Close search dialog
      this.showSearch = false;

      // Redirect to search results page with query parameters
      this.$router.push({
        path: '/search',
        query: {
          q: this.searchQuery,
          type: this.searchType
        }
      });

      // Reset search query
      this.searchQuery = '';
    },
    startTour() {
      // This would trigger the guided tour component
      // For now, just navigate to help page
      this.$router.push('/help');
    },
    reportIssue() {
      // Open GitHub issue page in new tab
      window.open('https://github.com/NModlin/dockerForge/issues/new', '_blank');
    },
    getNotificationIcon(type) {
      switch (type) {
        case 'info': return 'mdi-information';
        case 'success': return 'mdi-check-circle';
        case 'warning': return 'mdi-alert';
        case 'error': return 'mdi-alert-circle';
        default: return 'mdi-bell';
      }
    },
    getNotificationColor(type) {
      switch (type) {
        case 'info': return 'info';
        case 'success': return 'success';
        case 'warning': return 'warning';
        case 'error': return 'error';
        default: return 'primary';
      }
    },
    formatNotificationTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;

      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

      return date.toLocaleDateString();
    },
    dismissNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
      }
    },
    markAllAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true;
      });
    },

    handleSnackbarEvent(event) {
      const { text, color, timeout, multiLine, vertical, top } = event.detail;

      // Update snackbar data
      this.snackbar = {
        show: true,
        text,
        color: color || 'success',
        timeout: timeout || 3000,
        multiLine: multiLine || false,
        vertical: vertical || false,
        top: top || false
      };
    }
  },
  watch: {
    // Watch for changes to the dark mode setting
    isDarkMode: {
      handler(newValue) {
        this.$vuetify.theme.global.name = newValue ? 'dark' : 'light';
      },
      immediate: true
    }
  }
};
</script>

<style>
/* Global styles */
</style>
