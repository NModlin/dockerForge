<template>
  <div class="container-list">
    <h1 class="text-h4 mb-4">Containers</h1>

    <!-- Filters and Actions -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="filters.name"
              label="Filter by name"
              prepend-icon="mdi-magnify"
              clearable
              @input="applyFilters"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Filter by status"
              prepend-icon="mdi-filter"
              clearable
              @change="applyFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4" class="d-flex align-center justify-end">
            <v-btn color="primary" to="/containers/create">
              <v-icon left>mdi-plus</v-icon>
              New Container
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

    <!-- Empty State -->
    <v-card v-else-if="containers.length === 0" class="mb-4 text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-docker</v-icon>
      <h3 class="text-h5 mt-4">No containers found</h3>
      <p class="text-body-1 mt-2">
        {{ filters.name || filters.status ? 'Try adjusting your filters' : 'Create your first container to get started' }}
      </p>
      <v-btn color="primary" class="mt-4" to="/containers/create">
        <v-icon left>mdi-plus</v-icon>
        New Container
      </v-btn>
    </v-card>

    <!-- Container List -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="containers"
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [5, 10, 15, 20],
        }"
        class="elevation-1"
      >
        <!-- Name Column -->
        <template v-slot:item.name="{ item }">
          <router-link :to="`/containers/${item.id}`" class="text-decoration-none">
            {{ item.name }}
          </router-link>
        </template>

        <!-- Status Column -->
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            text-color="white"
            small
          >
            {{ item.status }}
          </v-chip>
        </template>

        <!-- Health Column -->
        <template v-slot:item.health_status="{ item }">
          <v-chip
            v-if="item.health_status"
            :color="getHealthColor(item.health_status)"
            text-color="white"
            small
          >
            {{ item.health_status }}
          </v-chip>
          <span v-else>-</span>
        </template>

        <!-- Created Column -->
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- Actions Column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            small
            :disabled="item.status === 'running'"
            @click="startContainer(item)"
            title="Start"
          >
            <v-icon small>mdi-play</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            :disabled="item.status !== 'running'"
            @click="stopContainer(item)"
            title="Stop"
          >
            <v-icon small>mdi-stop</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            :disabled="item.status !== 'running'"
            @click="restartContainer(item)"
            title="Restart"
          >
            <v-icon small>mdi-restart</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            @click="showDeleteDialog(item)"
            title="Delete"
          >
            <v-icon small>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Container</v-card-title>
        <v-card-text>
          Are you sure you want to delete the container <strong>{{ selectedContainer?.name }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteContainer">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';

export default {
  name: 'ContainerList',
  data() {
    return {
      loading: true,
      error: null,
      containers: [],
      filters: {
        name: '',
        status: '',
      },
      statusOptions: [
        { text: 'All', value: '' },
        { text: 'Running', value: 'running' },
        { text: 'Stopped', value: 'stopped' },
        { text: 'Created', value: 'created' },
        { text: 'Paused', value: 'paused' },
      ],
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Image', value: 'image', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Health', value: 'health_status', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      deleteDialog: false,
      selectedContainer: null,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchContainers();
  },
  methods: {
    async fetchContainers() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/containers', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: this.filters,
        // });
        // this.containers = response.data;

        // Mock data for development
        setTimeout(() => {
          this.containers = [
            {
              id: 'c1',
              name: 'nginx',
              image: 'nginx:latest',
              status: 'running',
              created_at: '2025-03-16T10:00:00Z',
              health_status: 'healthy',
            },
            {
              id: 'c2',
              name: 'redis',
              image: 'redis:alpine',
              status: 'running',
              created_at: '2025-03-16T09:00:00Z',
              health_status: 'healthy',
            },
            {
              id: 'c3',
              name: 'postgres',
              image: 'postgres:13',
              status: 'stopped',
              created_at: '2025-03-16T08:00:00Z',
              health_status: null,
            },
          ];
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load containers. Please try again.';
        this.loading = false;
      }
    },
    applyFilters() {
      this.fetchContainers();
    },
    getStatusColor(status) {
      switch (status) {
        case 'running':
          return 'success';
        case 'stopped':
          return 'error';
        case 'paused':
          return 'warning';
        case 'created':
          return 'info';
        default:
          return 'grey';
      }
    },
    getHealthColor(health) {
      switch (health) {
        case 'healthy':
          return 'success';
        case 'unhealthy':
          return 'error';
        case 'starting':
          return 'warning';
        default:
          return 'grey';
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async startContainer(container) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${container.id}/start`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        container.status = 'running';
        this.$forceUpdate();
      } catch (error) {
        this.error = `Failed to start container ${container.name}`;
      }
    },
    async stopContainer(container) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${container.id}/stop`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        container.status = 'stopped';
        this.$forceUpdate();
      } catch (error) {
        this.error = `Failed to stop container ${container.name}`;
      }
    },
    async restartContainer(container) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${container.id}/restart`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        container.status = 'running';
        this.$forceUpdate();
      } catch (error) {
        this.error = `Failed to restart container ${container.name}`;
      }
    },
    showDeleteDialog(container) {
      this.selectedContainer = container;
      this.deleteDialog = true;
    },
    async deleteContainer() {
      if (!this.selectedContainer) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/containers/${this.selectedContainer.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.containers = this.containers.filter(c => c.id !== this.selectedContainer.id);
        this.deleteDialog = false;
        this.selectedContainer = null;
      } catch (error) {
        this.error = `Failed to delete container ${this.selectedContainer.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.container-list {
  padding: 16px;
}
</style>
