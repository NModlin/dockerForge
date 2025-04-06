<template>
  <div class="notifications">
    <h1 class="text-h4 mb-4">Notifications</h1>

    <!-- Notification Controls -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="filter"
              :items="filterOptions"
              label="Filter"
              outlined
              dense
              hide-details
              @change="applyFilters"
            ></v-select>
          </v-col>

          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="timeRange"
              :items="timeRangeOptions"
              label="Time Range"
              outlined
              dense
              hide-details
              @change="applyFilters"
            ></v-select>
          </v-col>

          <v-spacer></v-spacer>

          <v-col cols="auto">
            <v-btn color="primary" text @click="markAllAsRead">
              <v-icon left>mdi-check-all</v-icon>
              Mark All as Read
            </v-btn>

            <v-btn color="error" text @click="clearAllNotifications">
              <v-icon left>mdi-delete-sweep</v-icon>
              Clear All
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- No Notifications -->
    <v-card v-else-if="filteredNotifications.length === 0" class="text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-bell-off</v-icon>
      <h3 class="text-h5 mt-4">No notifications</h3>
      <p class="text-body-1 mt-2">You don't have any notifications at the moment.</p>
    </v-card>

    <!-- Notification List -->
    <template v-else>
      <v-card v-for="(group, date) in groupedNotifications" :key="date" class="mb-4">
        <v-subheader>{{ formatGroupDate(date) }}</v-subheader>

        <v-list two-line>
          <template v-for="(notification, index) in group" :key="notification.id">
            <v-list-item
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
                  {{ formatTime(notification.timestamp) }}
                </v-list-item-subtitle>
              </v-list-item-content>

              <v-list-item-action>
                <v-btn
                  icon
                  small
                  :color="notification.read ? 'grey' : 'primary'"
                  @click="toggleRead(notification)"
                  :title="notification.read ? 'Mark as unread' : 'Mark as read'"
                >
                  <v-icon small>{{ notification.read ? 'mdi-email' : 'mdi-email-open' }}</v-icon>
                </v-btn>

                <v-btn
                  icon
                  small
                  color="error"
                  @click="dismissNotification(notification.id)"
                  title="Delete"
                >
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>

            <v-divider
              v-if="index < group.length - 1"
              :key="`divider-${notification.id}`"
              inset
            ></v-divider>
          </template>
        </v-list>
      </v-card>

      <!-- Load More Button -->
      <div class="text-center mt-4" v-if="hasMoreNotifications">
        <v-btn text color="primary" @click="loadMoreNotifications" :loading="loadingMore">
          Load More
        </v-btn>
      </div>
    </template>

    <!-- Clear All Confirmation Dialog -->
    <v-dialog v-model="clearAllDialog" max-width="400">
      <v-card>
        <v-card-title class="headline">Clear All Notifications</v-card-title>
        <v-card-text>
          Are you sure you want to delete all notifications? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="clearAllDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="confirmClearAll">Delete All</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'NotificationList',
  data() {
    return {
      loading: true,
      loadingMore: false,
      error: null,
      notifications: [],
      page: 1,
      hasMoreNotifications: true,

      // Filters
      filter: 'all',
      filterOptions: [
        { text: 'All Notifications', value: 'all' },
        { text: 'Unread', value: 'unread' },
        { text: 'Read', value: 'read' },
        { text: 'Info', value: 'info' },
        { text: 'Warning', value: 'warning' },
        { text: 'Error', value: 'error' }
      ],

      timeRange: 'all',
      timeRangeOptions: [
        { text: 'All Time', value: 'all' },
        { text: 'Today', value: 'today' },
        { text: 'This Week', value: 'week' },
        { text: 'This Month', value: 'month' }
      ],

      clearAllDialog: false
    };
  },
  computed: {
    filteredNotifications() {
      let filtered = [...this.notifications];

      // Apply type/read filter
      if (this.filter === 'unread') {
        filtered = filtered.filter(n => !n.read);
      } else if (this.filter === 'read') {
        filtered = filtered.filter(n => n.read);
      } else if (['info', 'warning', 'error', 'success'].includes(this.filter)) {
        filtered = filtered.filter(n => n.type === this.filter);
      }

      // Apply time range filter
      if (this.timeRange !== 'all') {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        if (this.timeRange === 'today') {
          filtered = filtered.filter(n => new Date(n.timestamp) >= today);
        } else if (this.timeRange === 'week') {
          const weekStart = new Date(today);
          weekStart.setDate(today.getDate() - today.getDay());
          filtered = filtered.filter(n => new Date(n.timestamp) >= weekStart);
        } else if (this.timeRange === 'month') {
          const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
          filtered = filtered.filter(n => new Date(n.timestamp) >= monthStart);
        }
      }

      return filtered;
    },

    groupedNotifications() {
      const groups = {};

      this.filteredNotifications.forEach(notification => {
        const date = new Date(notification.timestamp);
        const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;

        if (!groups[dateKey]) {
          groups[dateKey] = [];
        }

        groups[dateKey].push(notification);
      });

      // Sort each group by timestamp (newest first)
      Object.keys(groups).forEach(key => {
        groups[key].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      });

      // Sort groups by date (newest first)
      const sortedGroups = {};
      Object.keys(groups)
        .sort((a, b) => {
          const [yearA, monthA, dayA] = a.split('-').map(Number);
          const [yearB, monthB, dayB] = b.split('-').map(Number);

          if (yearA !== yearB) return yearB - yearA;
          if (monthA !== monthB) return monthB - monthA;
          return dayB - dayA;
        })
        .forEach(key => {
          sortedGroups[key] = groups[key];
        });

      return sortedGroups;
    }
  },
  created() {
    this.loadNotifications();
  },
  methods: {
    async loadNotifications() {
      this.loading = true;
      this.error = null;

      try {
        // In a real app, this would fetch from the API
        // For now, use mock data
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay

        this.notifications = [
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
            timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
            read: false
          },
          {
            id: 3,
            type: 'error',
            title: 'Image Pull Failed',
            message: 'Failed to pull image nginx:latest.',
            timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
            read: true
          },
          {
            id: 4,
            type: 'success',
            title: 'Container Created',
            message: 'Successfully created container "database".',
            timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            read: true
          },
          {
            id: 5,
            type: 'info',
            title: 'System Update Available',
            message: 'A new version of DockerForge is available.',
            timestamp: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
            read: true
          },
          {
            id: 6,
            type: 'warning',
            title: 'Volume Space Warning',
            message: 'Volume "data" is using over 90% of available space.',
            timestamp: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
            read: false
          },
          {
            id: 7,
            type: 'info',
            title: 'Network Created',
            message: 'Successfully created network "backend".',
            timestamp: new Date(Date.now() - 604800000).toISOString(), // 1 week ago
            read: true
          }
        ];
      } catch (error) {
        this.error = `Failed to load notifications: ${error.message}`;
        console.error('Error loading notifications:', error);
      } finally {
        this.loading = false;
      }
    },

    async loadMoreNotifications() {
      if (this.loadingMore) return;

      this.loadingMore = true;

      try {
        // In a real app, this would fetch more notifications from the API
        // For now, simulate loading more notifications
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay

        const moreNotifications = [
          {
            id: 8,
            type: 'error',
            title: 'Container Crashed',
            message: 'Container "api" exited with code 1.',
            timestamp: new Date(Date.now() - 1209600000).toISOString(), // 2 weeks ago
            read: true
          },
          {
            id: 9,
            type: 'info',
            title: 'Backup Completed',
            message: 'Successfully completed backup of all containers.',
            timestamp: new Date(Date.now() - 1814400000).toISOString(), // 3 weeks ago
            read: true
          },
          {
            id: 10,
            type: 'success',
            title: 'Security Scan Completed',
            message: 'No vulnerabilities found in your images.',
            timestamp: new Date(Date.now() - 2592000000).toISOString(), // 1 month ago
            read: true
          }
        ];

        this.notifications = [...this.notifications, ...moreNotifications];
        this.page++;

        // For demo purposes, disable "Load More" after loading additional notifications
        this.hasMoreNotifications = false;
      } catch (error) {
        console.error('Error loading more notifications:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to load more notifications: ${error.message}`,
          color: 'error'
        });
      } finally {
        this.loadingMore = false;
      }
    },

    applyFilters() {
      // In a real app, this might trigger a new API request with filter parameters
      // For this demo, we're just filtering the local data
    },

    toggleRead(notification) {
      notification.read = !notification.read;

      // In a real app, this would update the notification status via the API
      // For now, just update the local state
    },

    dismissNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
      }

      // In a real app, this would delete the notification via the API
    },

    markAllAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true;
      });

      // In a real app, this would update all notifications via the API
      this.$store.dispatch('showSnackbar', {
        text: 'All notifications marked as read',
        color: 'success'
      });
    },

    clearAllNotifications() {
      this.clearAllDialog = true;
    },

    confirmClearAll() {
      this.notifications = [];
      this.clearAllDialog = false;

      // In a real app, this would delete all notifications via the API
      this.$store.dispatch('showSnackbar', {
        text: 'All notifications cleared',
        color: 'success'
      });
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

    formatGroupDate(dateKey) {
      const [year, month, day] = dateKey.split('-').map(Number);
      const date = new Date(year, month, day);
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterday = new Date(today);
      yesterday.setDate(today.getDate() - 1);

      if (date.getTime() === today.getTime()) {
        return 'Today';
      } else if (date.getTime() === yesterday.getTime()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
      }
    },

    formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    }
  }
};
</script>

<style scoped>
.notifications {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
