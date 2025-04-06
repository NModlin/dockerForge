<template>
  <div class="compose-list">
    <h1 class="text-h4 mb-4">Docker Compose</h1>

    <!-- Filters and Actions -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="filters.name"
              label="Filter by name"
              prepend-icon="mdi-magnify"
              clearable
              @input="applyFilters"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" class="d-flex align-center justify-end">
            <v-btn color="primary" to="/compose/create">
              <v-icon left>mdi-plus</v-icon>
              New Compose Project
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
    <v-card v-else-if="composeProjects.length === 0" class="mb-4 text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-docker</v-icon>
      <h3 class="text-h5 mt-4">No compose projects found</h3>
      <p class="text-body-1 mt-2">
        {{ filters.name ? 'Try adjusting your filters' : 'Create your first compose project to get started' }}
      </p>
      <v-btn color="primary" class="mt-4" to="/compose/create">
        <v-icon left>mdi-plus</v-icon>
        New Compose Project
      </v-btn>
    </v-card>

    <!-- Compose Projects List -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="composeProjects"
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [5, 10, 15, 20],
        }"
        class="elevation-1"
      >
        <!-- Name Column -->
        <template v-slot:item.name="{ item }">
          <div class="d-flex align-center">
            <v-chip
              small
              :color="getStatusColor(item.status)"
              text-color="white"
              class="mr-2"
            >
              {{ item.status }}
            </v-chip>
            <router-link :to="`/compose/${item.id}`" class="text-decoration-none">
              {{ item.name }}
            </router-link>
          </div>
        </template>

        <!-- Services Column -->
        <template v-slot:item.service_count="{ item }">
          <v-chip
            small
            color="primary"
            text-color="white"
          >
            {{ item.service_count }} services
          </v-chip>
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
            @click="startComposeProject(item)"
            title="Start"
          >
            <v-icon small>mdi-play</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            :disabled="item.status !== 'running'"
            @click="stopComposeProject(item)"
            title="Stop"
          >
            <v-icon small>mdi-stop</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            @click="navigateToEditCompose(item)"
            title="Edit"
          >
            <v-icon small>mdi-pencil</v-icon>
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
        <v-card-title class="headline">Delete Compose Project</v-card-title>
        <v-card-text>
          Are you sure you want to delete the compose project <strong>{{ selectedProject?.name }}</strong>?
          <v-checkbox
            v-model="deleteWithVolumes"
            label="Also remove associated volumes"
            class="mt-4"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteComposeProject">
            Delete
          </v-btn>
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
import { mapGetters } from 'vuex';

export default {
  name: 'ComposeList',
  data() {
    return {
      loading: true,
      error: null,
      composeProjects: [],
      filters: {
        name: '',
      },
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
      headers: [
        { text: 'Name', value: 'name', sortable: true },

        { text: 'Services', value: 'service_count', sortable: true },
        { text: 'Location', value: 'location', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      deleteDialog: false,
      selectedProject: null,
      deleteWithVolumes: false,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchComposeProjects();
  },
  methods: {
    async fetchComposeProjects() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/compose', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: this.filters,
        // });
        // this.composeProjects = response.data;

        // Mock data for development
        setTimeout(() => {
          this.composeProjects = [
            {
              id: 'c1',
              name: 'web-app',
              status: 'running',
              service_count: 3,
              location: '/home/user/projects/web-app',
              created_at: '2025-03-15T10:00:00Z',
            },
            {
              id: 'c2',
              name: 'database-cluster',
              status: 'stopped',
              service_count: 2,
              location: '/home/user/projects/database-cluster',
              created_at: '2025-03-14T09:00:00Z',
            },
            {
              id: 'c3',
              name: 'monitoring-stack',
              status: 'running',
              service_count: 4,
              location: '/home/user/projects/monitoring',
              created_at: '2025-03-13T08:00:00Z',
            },
          ];
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load compose projects. Please try again.';
        this.loading = false;
      }
    },
    applyFilters() {
      this.fetchComposeProjects();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getStatusColor(status) {
      switch (status) {
        case 'running':
          return 'success';
        case 'stopped':
          return 'error';
        case 'partial':
          return 'warning';
        default:
          return 'grey';
      }
    },
    async startComposeProject(project) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${project.id}/start`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        project.status = 'running';
        this.$forceUpdate();
        this.showSuccess(`Compose project ${project.name} started successfully`);
      } catch (error) {
        this.error = `Failed to start compose project ${project.name}`;
        this.showError(this.error);
      }
    },
    async stopComposeProject(project) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${project.id}/stop`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        project.status = 'stopped';
        this.$forceUpdate();
        this.showSuccess(`Compose project ${project.name} stopped successfully`);
      } catch (error) {
        this.error = `Failed to stop compose project ${project.name}`;
        this.showError(this.error);
      }
    },
    showDeleteDialog(project) {
      this.selectedProject = project;
      this.deleteWithVolumes = false;
      this.deleteDialog = true;
    },
    async deleteComposeProject() {
      if (!this.selectedProject) return;

      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/compose/${this.selectedProject.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: { removeVolumes: this.deleteWithVolumes },
        // });

        // Mock implementation
        this.composeProjects = this.composeProjects.filter(p => p.id !== this.selectedProject.id);
        this.deleteDialog = false;
        this.showSuccess(`Compose project ${this.selectedProject.name} deleted successfully`);
        this.selectedProject = null;
      } catch (error) {
        this.error = `Failed to delete compose project ${this.selectedProject.name}`;
        this.showError(this.error);
        this.deleteDialog = false;
      }
    },

    navigateToEditCompose(project) {
      this.$router.push(`/compose/${project.id}/edit`);
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
    },
  },
};
</script>

<style scoped>
.compose-list {
  padding: 16px;
}
</style>
