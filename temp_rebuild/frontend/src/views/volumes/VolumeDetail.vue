<template>
  <div class="volume-detail">
    <v-row>
      <v-col cols="12">
        <v-btn text to="/volumes" class="mb-4">
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Volumes
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Volume Not Found -->
    <v-alert v-else-if="!volume" type="warning" class="mb-4">
      Volume not found
    </v-alert>

    <!-- Volume Details -->
    <template v-else>
      <v-row>
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-card-title class="headline">
              {{ volume.name }}
              <v-spacer></v-spacer>
              <v-btn
                color="error"
                text
                @click="showDeleteDialog"
              >
                <v-icon left>mdi-delete</v-icon>
                Delete
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <tbody>
                    <tr>
                      <td class="font-weight-bold">ID</td>
                      <td>{{ volume.id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Driver</td>
                      <td>{{ volume.driver }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Mount Point</td>
                      <td>{{ volume.mountpoint }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Size</td>
                      <td>{{ volume.size }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Created</td>
                      <td>{{ formatDate(volume.created_at) }}</td>
                    </tr>
                    <tr v-if="volume.labels && Object.keys(volume.labels).length > 0">
                      <td class="font-weight-bold">Labels</td>
                      <td>
                        <v-chip
                          v-for="(value, key) in volume.labels"
                          :key="key"
                          class="mr-2 mb-2"
                          small
                        >
                          {{ key }}: {{ value }}
                        </v-chip>
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <!-- Usage Stats -->
          <v-card class="mb-4">
            <v-card-title>Usage</v-card-title>
            <v-card-text>
              <v-progress-linear
                :value="usagePercentage"
                height="25"
                :color="usageColor"
                striped
              >
                <template v-slot:default>
                  <strong>{{ usagePercentage }}%</strong>
                </template>
              </v-progress-linear>
              <div class="mt-2 text-center">
                {{ volume.used || '0 B' }} / {{ volume.size || '0 B' }}
              </div>
            </v-card-text>
          </v-card>

          <!-- Connected Containers -->
          <v-card>
            <v-card-title>Connected Containers</v-card-title>
            <v-card-text v-if="connectedContainers.length === 0">
              <p class="text-center">No containers are using this volume</p>
            </v-card-text>
            <v-list v-else dense>
              <v-list-item
                v-for="container in connectedContainers"
                :key="container.id"
                :to="`/containers/${container.id}`"
              >
                <v-list-item-icon>
                  <v-icon
                    :color="container.status === 'running' ? 'success' : 'grey'"
                  >
                    mdi-docker
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ container.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ container.status }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Volume</v-card-title>
        <v-card-text>
          Are you sure you want to delete the volume <strong>{{ volume?.name }}</strong>?
          This action cannot be undone and may result in data loss.
          <v-alert
            v-if="connectedContainers.length > 0"
            type="warning"
            class="mt-3"
            dense
          >
            This volume is currently used by {{ connectedContainers.length }} container(s).
            Deleting it may cause those containers to malfunction.
          </v-alert>
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
  name: 'VolumeDetail',
  data() {
    return {
      loading: true,
      error: null,
      volume: null,
      connectedContainers: [],
      deleteDialog: false,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
    usagePercentage() {
      if (!this.volume || !this.volume.used || !this.volume.size) {
        return 0;
      }
      
      // This is a simplified calculation for demonstration
      // In a real app, you'd parse the size strings and calculate properly
      return Math.min(Math.round((parseInt(this.volume.used) / parseInt(this.volume.size)) * 100), 100);
    },
    usageColor() {
      if (this.usagePercentage > 90) {
        return 'error';
      } else if (this.usagePercentage > 70) {
        return 'warning';
      } else {
        return 'success';
      }
    },
  },
  created() {
    this.fetchVolumeDetails();
  },
  methods: {
    async fetchVolumeDetails() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get(`/api/volumes/${this.$route.params.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.volume = response.data;
        
        // Mock data for development
        setTimeout(() => {
          this.volume = {
            id: this.$route.params.id,
            name: 'postgres_data',
            driver: 'local',
            mountpoint: '/var/lib/docker/volumes/postgres_data/_data',
            size: '1.2 GB',
            used: '800 MB',
            created_at: '2025-03-15T10:00:00Z',
            labels: {
              'com.example.description': 'PostgreSQL Data',
              'com.example.environment': 'production',
            },
          };
          
          this.connectedContainers = [
            {
              id: 'c1',
              name: 'postgres',
              status: 'running',
            },
          ];
          
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load volume details. Please try again.';
        this.loading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    showDeleteDialog() {
      this.deleteDialog = true;
    },
    async deleteVolume() {
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/volumes/${this.volume.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Navigate back to volumes list
        this.$router.push('/volumes');
      } catch (error) {
        this.error = `Failed to delete volume ${this.volume.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.volume-detail {
  padding: 16px;
}
</style>
