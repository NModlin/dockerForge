<template>
  <div class="network-list">
    <h1 class="text-h4 mb-4">Networks</h1>

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
            <v-btn color="primary" to="/networks/create">
              <v-icon left>mdi-plus</v-icon>
              New Network
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
    <v-card v-else-if="networks.length === 0" class="mb-4 text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-lan</v-icon>
      <h3 class="text-h5 mt-4">No networks found</h3>
      <p class="text-body-1 mt-2">
        {{ filters.name ? 'Try adjusting your filters' : 'Create your first network to get started' }}
      </p>
      <v-btn color="primary" class="mt-4" to="/networks/create">
        <v-icon left>mdi-plus</v-icon>
        New Network
      </v-btn>
    </v-card>

    <!-- Network List -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="networks"
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [5, 10, 15, 20],
        }"
        class="elevation-1"
      >
        <!-- Name Column -->
        <template v-slot:item.name="{ item }">
          <router-link :to="`/networks/${item.id}`" class="text-decoration-none">
            {{ item.name }}
          </router-link>
        </template>

        <!-- Scope Column -->
        <template v-slot:item.scope="{ item }">
          <v-chip
            :color="getScopeColor(item.scope)"
            text-color="white"
            small
          >
            {{ item.scope }}
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
            @click="showDeleteDialog(item)"
            title="Delete"
            :disabled="item.name === 'bridge' || item.name === 'host' || item.name === 'none'"
          >
            <v-icon small>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Network</v-card-title>
        <v-card-text>
          Are you sure you want to delete the network <strong>{{ selectedNetwork?.name }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteNetwork">
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
  name: 'NetworkList',
  data() {
    return {
      loading: true,
      error: null,
      networks: [],
      filters: {
        name: '',
      },
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Driver', value: 'driver', sortable: true },
        { text: 'Subnet', value: 'subnet', sortable: false },
        { text: 'Scope', value: 'scope', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      deleteDialog: false,
      selectedNetwork: null,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchNetworks();
  },
  methods: {
    async fetchNetworks() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/networks', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: this.filters,
        // });
        // this.networks = response.data;

        // Mock data for development
        setTimeout(() => {
          this.networks = [
            {
              id: 'n1',
              name: 'bridge',
              driver: 'bridge',
              subnet: '172.17.0.0/16',
              scope: 'local',
              created_at: '2025-03-15T10:00:00Z',
            },
            {
              id: 'n2',
              name: 'host',
              driver: 'host',
              subnet: 'N/A',
              scope: 'local',
              created_at: '2025-03-15T10:00:00Z',
            },
            {
              id: 'n3',
              name: 'none',
              driver: 'null',
              subnet: 'N/A',
              scope: 'local',
              created_at: '2025-03-15T10:00:00Z',
            },
            {
              id: 'n4',
              name: 'app_network',
              driver: 'bridge',
              subnet: '172.18.0.0/16',
              scope: 'local',
              created_at: '2025-03-16T09:00:00Z',
            },
            {
              id: 'n5',
              name: 'overlay_network',
              driver: 'overlay',
              subnet: '10.0.0.0/24',
              scope: 'swarm',
              created_at: '2025-03-16T08:00:00Z',
            },
          ];
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load networks. Please try again.';
        this.loading = false;
      }
    },
    applyFilters() {
      this.fetchNetworks();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getScopeColor(scope) {
      switch (scope) {
        case 'swarm':
          return 'purple';
        case 'global':
          return 'blue';
        case 'local':
        default:
          return 'green';
      }
    },
    showDeleteDialog(network) {
      this.selectedNetwork = network;
      this.deleteDialog = true;
    },
    async deleteNetwork() {
      if (!this.selectedNetwork) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/networks/${this.selectedNetwork.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.networks = this.networks.filter(n => n.id !== this.selectedNetwork.id);
        this.deleteDialog = false;
        this.selectedNetwork = null;
      } catch (error) {
        this.error = `Failed to delete network ${this.selectedNetwork.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.network-list {
  padding: 16px;
}
</style>
