<template>
  <div class="container-detail">
    <div class="d-flex align-center mb-4">
      <v-btn icon class="mr-2" to="/containers">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <h1 class="text-h4">{{ loading ? 'Container Details' : container.name }}</h1>
      <v-spacer></v-spacer>
      <v-chip
        v-if="container && container.status"
        :color="getStatusColor(container.status)"
        text-color="white"
        class="mr-2"
      >
        {{ container.status }}
      </v-chip>
      <v-chip
        v-if="container && container.health_status"
        :color="getHealthColor(container.health_status)"
        text-color="white"
      >
        {{ container.health_status }}
      </v-chip>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Container Details -->
    <template v-else-if="container">
      <!-- Action Buttons -->
      <v-card class="mb-4">
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="success"
                :disabled="container.status === 'running'"
                @click="startContainer"
              >
                <v-icon left>mdi-play</v-icon>
                Start
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="error"
                :disabled="container.status !== 'running'"
                @click="stopContainer"
              >
                <v-icon left>mdi-stop</v-icon>
                Stop
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="warning"
                :disabled="container.status !== 'running'"
                @click="restartContainer"
              >
                <v-icon left>mdi-restart</v-icon>
                Restart
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="error"
                outlined
                @click="showDeleteDialog"
              >
                <v-icon left>mdi-delete</v-icon>
                Delete
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Basic Info -->
      <v-card class="mb-4">
        <v-card-title>
          <v-icon left>mdi-information</v-icon>
          Basic Information
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <tbody>
                <tr>
                  <td class="font-weight-bold">ID</td>
                  <td>{{ container.id }}</td>
                </tr>
                <tr>
                  <td class="font-weight-bold">Name</td>
                  <td>{{ container.name }}</td>
                </tr>
                <tr>
                  <td class="font-weight-bold">Image</td>
                  <td>{{ container.image }}</td>
                </tr>
                <tr>
                  <td class="font-weight-bold">Status</td>
                  <td>
                    <v-chip
                      :color="getStatusColor(container.status)"
                      text-color="white"
                      small
                    >
                      {{ container.status }}
                    </v-chip>
                  </td>
                </tr>
                <tr v-if="container.health_status">
                  <td class="font-weight-bold">Health</td>
                  <td>
                    <v-chip
                      :color="getHealthColor(container.health_status)"
                      text-color="white"
                      small
                    >
                      {{ container.health_status }}
                    </v-chip>
                  </td>
                </tr>
                <tr>
                  <td class="font-weight-bold">Created</td>
                  <td>{{ formatDate(container.created_at) }}</td>
                </tr>
                <tr v-if="container.started_at">
                  <td class="font-weight-bold">Started</td>
                  <td>{{ formatDate(container.started_at) }}</td>
                </tr>
                <tr v-if="container.ip_address">
                  <td class="font-weight-bold">IP Address</td>
                  <td>{{ container.ip_address }}</td>
                </tr>
                <tr v-if="container.network">
                  <td class="font-weight-bold">Network</td>
                  <td>{{ container.network }}</td>
                </tr>
                <tr v-if="container.restart_policy">
                  <td class="font-weight-bold">Restart Policy</td>
                  <td>{{ container.restart_policy }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>

      <!-- Resource Usage -->
      <v-card v-if="container.resource_usage" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-chart-line</v-icon>
          Resource Usage
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <div class="mb-2">
                <div class="d-flex justify-space-between align-center">
                  <span>CPU Usage</span>
                  <span>{{ container.resource_usage.cpu_percent }}%</span>
                </div>
                <v-progress-linear
                  color="primary"
                  height="10"
                  rounded
                  :value="container.resource_usage.cpu_percent"
                ></v-progress-linear>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="mb-2">
                <div class="d-flex justify-space-between align-center">
                  <span>Memory Usage</span>
                  <span>{{ container.resource_usage.memory_usage }} / {{ container.resource_usage.memory_limit }}</span>
                </div>
                <v-progress-linear
                  color="info"
                  height="10"
                  rounded
                  :value="container.resource_usage.memory_percent"
                ></v-progress-linear>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Ports -->
      <v-card v-if="container.ports && container.ports.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-lan-connect</v-icon>
          Port Mappings
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>Host IP</th>
                  <th>Host Port</th>
                  <th>Container Port</th>
                  <th>Protocol</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(port, index) in container.ports" :key="index">
                  <td>{{ port.host_ip || '0.0.0.0' }}</td>
                  <td>{{ port.host_port }}</td>
                  <td>{{ port.container_port }}</td>
                  <td>{{ port.protocol }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>

      <!-- Volumes -->
      <v-card v-if="container.volumes && container.volumes.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-database</v-icon>
          Volume Mappings
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>Host Path</th>
                  <th>Container Path</th>
                  <th>Mode</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(volume, index) in container.volumes" :key="index">
                  <td>{{ volume.host_path }}</td>
                  <td>{{ volume.container_path }}</td>
                  <td>{{ volume.mode }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>

      <!-- Environment Variables -->
      <v-card v-if="container.environment && Object.keys(container.environment).length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-code-braces</v-icon>
          Environment Variables
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, key) in container.environment" :key="key">
                  <td>{{ key }}</td>
                  <td>{{ value }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>

      <!-- Labels -->
      <v-card v-if="container.labels && Object.keys(container.labels).length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-tag-multiple</v-icon>
          Labels
        </v-card-title>
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, key) in container.labels" :key="key">
                  <td>{{ key }}</td>
                  <td>{{ value }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>

      <!-- Logs -->
      <v-card class="mb-4">
        <v-card-title>
          <v-icon left>mdi-text</v-icon>
          Logs
          <v-spacer></v-spacer>
          <v-btn icon @click="fetchLogs">
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <div v-if="logsLoading" class="d-flex justify-center align-center my-5">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
          <div v-else-if="logsError" class="text-center red--text">
            {{ logsError }}
          </div>
          <div v-else-if="logs.length === 0" class="text-center grey--text">
            No logs available
          </div>
          <v-sheet v-else class="logs-container pa-2" color="grey lighten-4" rounded>
            <pre class="logs-content">{{ logs.join('\n') }}</pre>
          </v-sheet>
        </v-card-text>
      </v-card>
    </template>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Container</v-card-title>
        <v-card-text>
          Are you sure you want to delete the container <strong>{{ container?.name }}</strong>?
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
  name: 'ContainerDetail',
  data() {
    return {
      loading: true,
      error: null,
      container: null,
      logs: [],
      logsLoading: false,
      logsError: null,
      deleteDialog: false,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
    containerId() {
      return this.$route.params.id;
    },
  },
  created() {
    this.fetchContainer();
    this.fetchLogs();
  },
  methods: {
    async fetchContainer() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get(`/api/containers/${this.containerId}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.container = response.data;

        // Mock data for development
        setTimeout(() => {
          if (this.containerId === 'c1') {
            this.container = {
              id: 'c1',
              name: 'nginx',
              image: 'nginx:latest',
              status: 'running',
              created_at: '2025-03-16T10:00:00Z',
              started_at: '2025-03-16T10:01:00Z',
              finished_at: null,
              health_status: 'healthy',
              ip_address: '172.17.0.2',
              command: "nginx -g 'daemon off;'",
              entrypoint: null,
              environment: {
                NGINX_HOST: 'example.com',
                NGINX_PORT: '80',
              },
              ports: [
                { host_ip: '0.0.0.0', host_port: 8080, container_port: 80, protocol: 'tcp' },
              ],
              volumes: [
                { host_path: '/data', container_path: '/usr/share/nginx/html', mode: 'rw' },
              ],
              network: 'bridge',
              restart_policy: 'unless-stopped',
              labels: { 'com.example.description': 'Web server' },
              resource_usage: {
                cpu_percent: 0.5,
                memory_usage: '10MB',
                memory_limit: '100MB',
                memory_percent: 10.0,
              },
            };
          } else if (this.containerId === 'c2') {
            this.container = {
              id: 'c2',
              name: 'redis',
              image: 'redis:alpine',
              status: 'running',
              created_at: '2025-03-16T09:00:00Z',
              started_at: '2025-03-16T09:01:00Z',
              finished_at: null,
              health_status: 'healthy',
              ip_address: '172.17.0.3',
              command: 'redis-server',
              entrypoint: null,
              environment: {},
              ports: [
                { host_ip: '0.0.0.0', host_port: 6379, container_port: 6379, protocol: 'tcp' },
              ],
              volumes: [
                { host_path: '/data/redis', container_path: '/data', mode: 'rw' },
              ],
              network: 'bridge',
              restart_policy: 'always',
              labels: { 'com.example.description': 'Redis cache' },
              resource_usage: {
                cpu_percent: 0.2,
                memory_usage: '5MB',
                memory_limit: '50MB',
                memory_percent: 10.0,
              },
            };
          } else if (this.containerId === 'c3') {
            this.container = {
              id: 'c3',
              name: 'postgres',
              image: 'postgres:13',
              status: 'stopped',
              created_at: '2025-03-16T08:00:00Z',
              started_at: '2025-03-16T08:01:00Z',
              finished_at: '2025-03-16T08:30:00Z',
              health_status: null,
              ip_address: null,
              command: 'postgres',
              entrypoint: null,
              environment: {
                POSTGRES_USER: 'user',
                POSTGRES_PASSWORD: 'password',
                POSTGRES_DB: 'db',
              },
              ports: [
                { host_ip: '0.0.0.0', host_port: 5432, container_port: 5432, protocol: 'tcp' },
              ],
              volumes: [
                { host_path: '/data/postgres', container_path: '/var/lib/postgresql/data', mode: 'rw' },
              ],
              network: 'bridge',
              restart_policy: 'no',
              labels: { 'com.example.description': 'PostgreSQL database' },
              resource_usage: null,
            };
          } else {
            this.error = `Container with ID ${this.containerId} not found`;
          }
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load container details. Please try again.';
        this.loading = false;
      }
    },
    async fetchLogs() {
      this.logsLoading = true;
      this.logsError = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get(`/api/containers/${this.containerId}/logs`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.logs = response.data.logs;

        // Mock data for development
        setTimeout(() => {
          this.logs = [
            `2025-03-16T19:00:00.000Z Container ${this.containerId} started`,
            `2025-03-16T19:00:01.000Z Container ${this.containerId} running`,
            `2025-03-16T19:00:02.000Z Container ${this.containerId} healthy`,
            `2025-03-16T19:00:03.000Z Container ${this.containerId} processing request`,
            `2025-03-16T19:00:04.000Z Container ${this.containerId} request completed`,
          ];
          this.logsLoading = false;
        }, 1000);
      } catch (error) {
        this.logsError = 'Failed to load container logs. Please try again.';
        this.logsLoading = false;
      }
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
    async startContainer() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${this.containerId}/start`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.container.status = 'running';
        this.container.started_at = new Date().toISOString();
        this.container.finished_at = null;
        this.container.health_status = 'starting';
        this.container.ip_address = '172.17.0.2';
        
        // Simulate health check
        setTimeout(() => {
          this.container.health_status = 'healthy';
          this.$forceUpdate();
        }, 2000);
      } catch (error) {
        this.error = `Failed to start container ${this.container.name}`;
      }
    },
    async stopContainer() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${this.containerId}/stop`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.container.status = 'stopped';
        this.container.finished_at = new Date().toISOString();
        this.container.health_status = null;
        this.container.ip_address = null;
        this.container.resource_usage = null;
      } catch (error) {
        this.error = `Failed to stop container ${this.container.name}`;
      }
    },
    async restartContainer() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/containers/${this.containerId}/restart`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.container.status = 'running';
        this.container.started_at = new Date().toISOString();
        this.container.finished_at = null;
        this.container.health_status = 'starting';
        
        // Simulate health check
        setTimeout(() => {
          this.container.health_status = 'healthy';
          this.$forceUpdate();
        }, 2000);
      } catch (error) {
        this.error = `Failed to restart container ${this.container.name}`;
      }
    },
    showDeleteDialog() {
      this.deleteDialog = true;
    },
    async deleteContainer() {
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/containers/${this.containerId}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.deleteDialog = false;
        this.$router.push('/containers');
      } catch (error) {
        this.error = `Failed to delete container ${this.container.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.container-detail {
  padding: 16px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
}

.logs-content {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>
