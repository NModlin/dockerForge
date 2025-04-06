<template>
  <div class="network-detail">
    <v-row>
      <v-col cols="12">
        <v-btn text to="/networks" class="mb-4">
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Networks
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

    <!-- Network Not Found -->
    <v-alert v-else-if="!network" type="warning" class="mb-4">
      Network not found
    </v-alert>

    <!-- Network Details -->
    <template v-else>
      <v-row>
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-card-title class="headline">
              {{ network.name }}
              <v-chip
                class="ml-2"
                :color="getScopeColor(network.scope)"
                text-color="white"
                small
              >
                {{ network.scope }}
              </v-chip>
              <v-spacer></v-spacer>
              <v-btn
                color="error"
                text
                @click="showDeleteDialog"
                :disabled="isDefaultNetwork"
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
                      <td>{{ network.id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Driver</td>
                      <td>{{ network.driver }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Subnet</td>
                      <td>{{ network.subnet }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Gateway</td>
                      <td>{{ network.gateway || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">IP Range</td>
                      <td>
                        <v-chip
                          v-if="network.subnet && network.subnet !== 'N/A'"
                          small
                          color="primary"
                          text-color="white"
                        >
                          {{ network.subnet }}
                        </v-chip>
                        <span v-else>N/A</span>
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Internal</td>
                      <td>{{ network.internal ? 'Yes' : 'No' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Created</td>
                      <td>{{ formatDate(network.created_at) }}</td>
                    </tr>
                    <tr v-if="network.labels && Object.keys(network.labels).length > 0">
                      <td class="font-weight-bold">Labels</td>
                      <td>
                        <v-chip
                          v-for="(value, key) in network.labels"
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

          <!-- Network Options -->
          <v-card v-if="network.options && Object.keys(network.options).length > 0" class="mb-4">
            <v-card-title>Network Options</v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Option</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(value, key) in network.options" :key="key">
                      <td>{{ key }}</td>
                      <td>{{ value }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <!-- Connected Containers -->
          <v-card>
            <v-card-title>
              Connected Containers
              <v-spacer></v-spacer>
              <v-btn
                text
                small
                color="primary"
                @click="openConnectContainerDialog"
                :disabled="isDefaultNetwork && network.driver === 'null'"
              >
                <v-icon left small>mdi-link</v-icon>
                Connect
              </v-btn>
            </v-card-title>
            <v-card-text v-if="connectedContainers.length === 0">
              <div class="text-center pa-4">
                <v-icon large color="grey lighten-1">mdi-docker</v-icon>
                <p class="text-body-2 mt-2 grey--text">No containers connected</p>
                <v-btn
                  v-if="!isDefaultNetwork && network.driver !== 'null'"
                  color="primary"
                  class="mt-4"
                  small
                  @click="openConnectContainerDialog"
                >
                  <v-icon left>mdi-link</v-icon>
                  Connect Container
                </v-btn>
              </div>
            </v-card-text>
            <v-list v-else dense>
              <v-list-item
                v-for="container in connectedContainers"
                :key="container.id"
              >
                <v-list-item-icon>
                  <v-icon
                    :color="container.status === 'running' ? 'success' : 'grey'"
                  >
                    mdi-docker
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>
                    <router-link :to="`/containers/${container.id}`" class="text-decoration-none">
                      {{ container.name }}
                    </router-link>
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ container.ip_address || 'No IP assigned' }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn
                    icon
                    x-small
                    color="error"
                    @click="confirmDisconnectContainer(container)"
                    :disabled="isDefaultNetwork && container.name === 'bridge'"
                  >
                    <v-icon x-small>mdi-link-off</v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Network Visualization -->
          <v-card class="mt-4">
            <v-card-title>
              Network Visualization
            </v-card-title>
            <v-card-text>
              <div class="network-visualization pa-4">
                <div v-if="connectedContainers.length === 0" class="text-center pa-4">
                  <p class="text-body-2 grey--text">No containers to visualize</p>
                </div>
                <div v-else class="network-diagram">
                  <div class="network-node gateway" v-if="network.gateway && network.gateway !== 'N/A'">
                    <v-icon large>mdi-router-wireless</v-icon>
                    <div class="node-label">Gateway</div>
                    <div class="node-sublabel">{{ network.gateway }}</div>
                  </div>

                  <div class="network-connections">
                    <div
                      v-for="(container, index) in connectedContainers"
                      :key="index"
                      class="network-node container"
                    >
                      <v-icon large>mdi-docker</v-icon>
                      <div class="node-label">{{ container.name }}</div>
                      <div class="node-sublabel">{{ container.ip_address || 'No IP' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Network</v-card-title>
        <v-card-text>
          Are you sure you want to delete the network <strong>{{ network?.name }}</strong>?
          This action cannot be undone.
          <v-alert
            v-if="connectedContainers.length > 0"
            type="warning"
            class="mt-3"
            dense
          >
            This network is currently used by {{ connectedContainers.length }} container(s).
            Deleting it may cause those containers to lose connectivity.
          </v-alert>
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

    <!-- Connect Container Dialog -->
    <v-dialog v-model="connectContainerDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon left>mdi-link</v-icon>
          Connect Container
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-select
            v-model="selectedContainer"
            :items="availableContainers"
            label="Select Container"
            outlined
            dense
            :loading="loadingContainers"
          ></v-select>

          <v-text-field
            v-model="containerAliases"
            label="Network Aliases (comma-separated)"
            hint="Optional aliases for the container in this network"
            persistent-hint
            outlined
            dense
          ></v-text-field>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey darken-1" @click="connectContainerDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!selectedContainer"
            @click="connectContainer"
          >
            Connect
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Disconnect Container Dialog -->
    <v-dialog v-model="disconnectContainerDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">
          <v-icon left color="error">mdi-alert</v-icon>
          Disconnect Container
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="py-4">
          <p>Are you sure you want to disconnect the container <strong>{{ containerToDisconnect?.name }}</strong> from this network?</p>
          <p class="text-caption mt-2">This action will remove the container from the network, and it will no longer be able to communicate with other containers on this network.</p>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey darken-1" @click="disconnectContainerDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="disconnectContainer"
          >
            Disconnect
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'NetworkDetail',
  data() {
    return {
      loading: true,
      error: null,
      network: null,
      connectedContainers: [],
      deleteDialog: false,
      connectContainerDialog: false,
      disconnectContainerDialog: false,
      selectedContainer: null,
      containerAliases: '',
      containerToDisconnect: null,
      availableContainers: [],
      loadingContainers: false,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
    isDefaultNetwork() {
      if (!this.network) return false;
      return ['bridge', 'host', 'none'].includes(this.network.name);
    },
  },
  created() {
    this.fetchNetworkDetails();
    this.fetchAvailableContainers();
  },
  methods: {
    async fetchNetworkDetails() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get(`/api/networks/${this.$route.params.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.network = response.data;

        // Mock data for development
        setTimeout(() => {
          // Simulate different networks based on the ID parameter
          if (this.$route.params.id === 'n1') {
            this.network = {
              id: 'n1',
              name: 'bridge',
              driver: 'bridge',
              subnet: '172.17.0.0/16',
              gateway: '172.17.0.1',
              scope: 'local',
              internal: false,
              created_at: '2025-03-15T10:00:00Z',
              options: {
                'com.docker.network.bridge.default_bridge': 'true',
                'com.docker.network.bridge.enable_icc': 'true',
                'com.docker.network.bridge.enable_ip_masquerade': 'true',
                'com.docker.network.bridge.host_binding_ipv4': '0.0.0.0',
                'com.docker.network.bridge.name': 'docker0',
                'com.docker.network.driver.mtu': '1500',
              },
            };

            this.connectedContainers = [
              {
                id: 'c1',
                name: 'nginx',
                status: 'running',
                ip_address: '172.17.0.2',
              },
              {
                id: 'c2',
                name: 'redis',
                status: 'running',
                ip_address: '172.17.0.3',
              },
            ];
          } else if (this.$route.params.id === 'n4') {
            this.network = {
              id: 'n4',
              name: 'app_network',
              driver: 'bridge',
              subnet: '172.18.0.0/16',
              gateway: '172.18.0.1',
              scope: 'local',
              internal: false,
              created_at: '2025-03-16T09:00:00Z',
              labels: {
                'com.example.environment': 'development',
                'com.example.project': 'dockerforge',
              },
            };

            this.connectedContainers = [
              {
                id: 'c3',
                name: 'postgres',
                status: 'stopped',
                ip_address: '172.18.0.2',
              },
            ];
          } else if (this.$route.params.id === 'n5') {
            this.network = {
              id: 'n5',
              name: 'overlay_network',
              driver: 'overlay',
              subnet: '10.0.0.0/24',
              gateway: '10.0.0.1',
              scope: 'swarm',
              internal: false,
              created_at: '2025-03-16T08:00:00Z',
              options: {
                'com.docker.network.driver.overlay.vxlanid_list': '4097',
                'com.docker.network.driver.overlay.mtu': '1450',
              },
            };

            this.connectedContainers = [];
          } else {
            // Default network for any other ID
            this.network = {
              id: this.$route.params.id,
              name: 'unknown_network',
              driver: 'bridge',
              subnet: '192.168.0.0/24',
              gateway: '192.168.0.1',
              scope: 'local',
              internal: false,
              created_at: '2025-03-16T00:00:00Z',
            };

            this.connectedContainers = [];
          }

          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load network details. Please try again.';
        this.loading = false;
      }
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
    showDeleteDialog() {
      this.deleteDialog = true;
    },
    async deleteNetwork() {
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/networks/${this.network.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Navigate back to networks list
        this.$router.push('/networks');
      } catch (error) {
        this.error = `Failed to delete network ${this.network.name}`;
        this.deleteDialog = false;
      }
    },

    async fetchAvailableContainers() {
      this.loadingContainers = true;
      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/containers', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // const containers = response.data;

        // Mock data for development
        setTimeout(() => {
          const allContainers = [
            { id: 'c1', name: 'nginx', status: 'running' },
            { id: 'c2', name: 'redis', status: 'running' },
            { id: 'c3', name: 'postgres', status: 'stopped' },
            { id: 'c4', name: 'mongodb', status: 'running' },
            { id: 'c5', name: 'mysql', status: 'running' }
          ];

          // Filter out containers that are already connected to the network
          const connectedIds = this.connectedContainers.map(c => c.id);
          this.availableContainers = allContainers
            .filter(c => !connectedIds.includes(c.id))
            .map(c => ({
              text: `${c.name} (${c.status})`,
              value: c.id,
              ...c
            }));

          this.loadingContainers = false;
        }, 500);
      } catch (error) {
        this.error = 'Failed to load available containers';
        this.loadingContainers = false;
      }
    },

    openConnectContainerDialog() {
      this.selectedContainer = null;
      this.containerAliases = '';
      this.connectContainerDialog = true;
    },

    confirmDisconnectContainer(container) {
      this.containerToDisconnect = container;
      this.disconnectContainerDialog = true;
    },

    async connectContainer() {
      if (!this.selectedContainer) return;

      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/networks/${this.network.id}/connect`, {
        //   containerId: this.selectedContainer,
        //   aliases: this.containerAliases ? this.containerAliases.split(',').map(a => a.trim()) : []
        // }, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        const selectedContainerData = this.availableContainers.find(c => c.value === this.selectedContainer);
        if (selectedContainerData) {
          this.connectedContainers.push({
            id: selectedContainerData.id,
            name: selectedContainerData.name,
            status: selectedContainerData.status,
            ip_address: `${this.network.subnet.split('/')[0].slice(0, -1)}${Math.floor(Math.random() * 254) + 1}`
          });

          // Update available containers
          this.availableContainers = this.availableContainers.filter(c => c.value !== this.selectedContainer);
        }

        this.connectContainerDialog = false;
      } catch (error) {
        this.error = 'Failed to connect container to network';
      }
    },

    async disconnectContainer() {
      if (!this.containerToDisconnect) return;

      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/networks/${this.network.id}/disconnect`, {
        //   containerId: this.containerToDisconnect.id
        // }, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.connectedContainers = this.connectedContainers.filter(c => c.id !== this.containerToDisconnect.id);

        // Add the container back to available containers
        this.availableContainers.push({
          text: `${this.containerToDisconnect.name} (${this.containerToDisconnect.status || 'unknown'})`,
          value: this.containerToDisconnect.id,
          id: this.containerToDisconnect.id,
          name: this.containerToDisconnect.name,
          status: this.containerToDisconnect.status || 'unknown'
        });

        this.disconnectContainerDialog = false;
        this.containerToDisconnect = null;
      } catch (error) {
        this.error = 'Failed to disconnect container from network';
      }
    },
  },
};
</script>

<style scoped>
.network-detail {
  padding: 16px;
}

.network-visualization {
  min-height: 200px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.network-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.network-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  margin: 10px;
  min-width: 120px;
}

.gateway {
  background-color: rgba(33, 150, 243, 0.1);
  border: 2px solid #2196F3;
}

.container {
  background-color: rgba(76, 175, 80, 0.1);
  border: 2px solid #4CAF50;
}

.node-label {
  font-weight: bold;
  margin-top: 5px;
}

.node-sublabel {
  font-size: 0.8rem;
  color: #666;
}

.network-connections {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20px;
  position: relative;
}

.network-connections::before {
  content: '';
  position: absolute;
  top: -20px;
  left: 50%;
  width: 2px;
  height: 20px;
  background-color: #ccc;
}
</style>
