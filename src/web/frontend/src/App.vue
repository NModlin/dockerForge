<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon v-if="isAuthenticated" @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>DockerForge</v-toolbar-title>
      <v-spacer></v-spacer>
      <template v-if="isAuthenticated">
        <v-btn icon>
          <v-icon>mdi-bell</v-icon>
        </v-btn>
        <!-- AI Chat Toggle Button -->
        <v-btn icon @click="toggleChat" v-tooltip="'AI Assistant'">
          <v-icon>mdi-robot</v-icon>
        </v-btn>
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon>mdi-account</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item>
              <v-list-item-title>{{ currentUser?.username || 'User' }}</v-list-item-title>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item @click="logout">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-app-bar>

    <v-navigation-drawer v-if="isAuthenticated" v-model="drawer" app>
      <v-list>
        <v-list-item to="/" link>
          <v-list-item-icon>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/containers" link>
          <v-list-item-icon>
            <v-icon>mdi-docker</v-icon>
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

        <v-list-item to="/compose" link>
          <v-list-item-icon>
            <v-icon>mdi-file-document-multiple</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Compose</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

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

        <v-list-item to="/settings" link>
          <v-list-item-icon>
            <v-icon>mdi-cog</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
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
    };
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
