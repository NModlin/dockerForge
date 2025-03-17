<template>
  <div class="volume-list">
    <h1 class="text-h4 mb-4">Volumes</h1>

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
            <v-btn color="primary" to="/volumes/create">
              <v-icon left>mdi-plus</v-icon>
              New Volume
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
    <v-card v-else-if="volumes.length === 0" class="mb-4 text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-database</v-icon>
      <h3 class="text-h5 mt-4">No volumes found</h3>
      <p class="text-body-1 mt-2">
        {{ filters.name ? 'Try adjusting your filters' : 'Create your first volume to get started' }}
      </p>
      <v-btn color="primary" class="mt-4" to="/volumes/create">
        <v-icon left>mdi-plus</v-icon>
        New Volume
      </v-btn>
    </v-card>

    <!-- Volume List -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="volumes"
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [5, 10, 15, 20],
        }"
        class="elevation-1"
      >
        <!-- Name Column -->
        <template v-slot:item.name="{ item }">
          <router-link :to="`/volumes/${item.id}`" class="text-decoration-none">
            {{ item.name }}
          </router-link>
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
        <v-card-title class="headline">Delete Volume</v-card-title>
        <v-card-text>
          Are you sure you want to delete the volume <strong>{{ selectedVolume?.name }}</strong>?
          This action cannot be undone and may result in data loss.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteVolume">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'VolumeList',
  data() {
    return {
      loading: true,
      error: null,
      volumes: [],
      filters: {
        name: '',
      },
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Driver', value: 'driver', sortable: true },
        { text: 'Mount Point', value: 'mountpoint', sortable: false },
        { text: 'Size', value: 'size', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      deleteDialog: false,
      selectedVolume: null,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchVolumes();
  },
  methods: {
    async fetchVolumes() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/volumes', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: this.filters,
        // });
        // this.volumes = response.data;

        // Mock data for development
        setTimeout(() => {
          this.volumes = [
            {
              id: 'v1',
              name: 'postgres_data',
              driver: 'local',
              mountpoint: '/var/lib/docker/volumes/postgres_data/_data',
              size: '1.2 GB',
              created_at: '2025-03-15T10:00:00Z',
            },
            {
              id: 'v2',
              name: 'redis_data',
              driver: 'local',
              mountpoint: '/var/lib/docker/volumes/redis_data/_data',
              size: '256 MB',
              created_at: '2025-03-15T09:00:00Z',
            },
            {
              id: 'v3',
              name: 'nginx_config',
              driver: 'local',
              mountpoint: '/var/lib/docker/volumes/nginx_config/_data',
              size: '4 MB',
              created_at: '2025-03-15T08:00:00Z',
            },
          ];
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load volumes. Please try again.';
        this.loading = false;
      }
    },
    applyFilters() {
      this.fetchVolumes();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    showDeleteDialog(volume) {
      this.selectedVolume = volume;
      this.deleteDialog = true;
    },
    async deleteVolume() {
      if (!this.selectedVolume) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/volumes/${this.selectedVolume.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.volumes = this.volumes.filter(v => v.id !== this.selectedVolume.id);
        this.deleteDialog = false;
        this.selectedVolume = null;
      } catch (error) {
        this.error = `Failed to delete volume ${this.selectedVolume.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.volume-list {
  padding: 16px;
}
</style>
