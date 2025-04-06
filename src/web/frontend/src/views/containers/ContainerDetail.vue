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
                :disabled="container.status === 'running' || actionInProgress"
                @click="showStartDialog"
                :loading="actionInProgress && actionType === 'start'"
              >
                <v-icon left>mdi-play</v-icon>
                Start
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="error"
                :disabled="container.status !== 'running' || actionInProgress"
                @click="showStopDialog"
                :loading="actionInProgress && actionType === 'stop'"
              >
                <v-icon left>mdi-stop</v-icon>
                Stop
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-btn
                block
                color="warning"
                :disabled="container.status !== 'running' || actionInProgress"
                @click="showRestartDialog"
                :loading="actionInProgress && actionType === 'restart'"
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
                :disabled="actionInProgress"
                :loading="actionInProgress && actionType === 'delete'"
              >
                <v-icon left>mdi-delete</v-icon>
                Delete
              </v-btn>
            </v-col>
          </v-row>

          <v-row class="mt-4">
            <v-col cols="12" sm="6" md="4">
              <v-btn
                block
                color="primary"
                :disabled="container.status !== 'running'"
                @click="openTerminal"
              >
                <v-icon left>mdi-console</v-icon>
                Terminal
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-btn
                block
                color="primary"
                :disabled="container.status !== 'running'"
                @click="openStats"
              >
                <v-icon left>mdi-chart-line</v-icon>
                Stats
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-btn
                block
                color="primary"
                @click="openInspect"
              >
                <v-icon left>mdi-magnify</v-icon>
                Inspect
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
                    <div class="d-flex align-center">
                      <v-chip
                        :color="getHealthColor(container.health_status)"
                        text-color="white"
                        small
                        class="mr-2"
                      >
                        {{ container.health_status }}
                      </v-chip>
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn
                            x-small
                            icon
                            v-bind="attrs"
                            v-on="on"
                            @click="openInspect"
                          >
                            <v-icon small>mdi-information-outline</v-icon>
                          </v-btn>
                        </template>
                        <span>View detailed health check information</span>
                      </v-tooltip>
                    </div>
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

      <!-- Resource Usage Stats -->
      <container-stats
        v-if="container.status === 'running'"
        :container-id="containerId"
        :initial-stats="container.resource_usage || {}"
      ></container-stats>

      <!-- Basic Resource Usage for non-running containers -->
      <v-card v-else-if="container.resource_usage" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-chart-line</v-icon>
          Resource Usage
          <v-spacer></v-spacer>
          <v-chip color="error" small>Container not running</v-chip>
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
          <v-spacer></v-spacer>
          <v-text-field
            v-model="labelSearch"
            append-icon="mdi-magnify"
            label="Search labels"
            single-line
            hide-details
            dense
            class="ml-2"
            style="max-width: 250px"
          ></v-text-field>
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
                <tr v-for="(value, key) in filteredLabels" :key="key">
                  <td class="font-weight-medium">{{ key }}</td>
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
          <v-btn icon @click="fetchLogs" :loading="logsLoading" :disabled="logsLoading">
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
          <v-btn icon @click="autoRefreshLogs = !autoRefreshLogs" :color="autoRefreshLogs ? 'primary' : ''">
            <v-icon>mdi-autorenew</v-icon>
          </v-btn>
          <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on">
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item @click="downloadLogs">
                <v-list-item-icon>
                  <v-icon>mdi-download</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Download Logs</v-list-item-title>
              </v-list-item>
              <v-list-item @click="clearLogs">
                <v-list-item-icon>
                  <v-icon>mdi-delete</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Clear Logs</v-list-item-title>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item>
                <v-list-item-title>Tail Lines:</v-list-item-title>
                <v-list-item-action>
                  <v-select
                    v-model="logTailLines"
                    :items="[10, 50, 100, 500, 1000, 'all']"
                    dense
                    hide-details
                    class="logs-tail-select"
                    @change="fetchLogs"
                  ></v-select>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-card-title>

        <v-card-text>
          <!-- Log Filters -->
          <v-row class="mb-3">
            <v-col cols="12" sm="6" md="8">
              <v-text-field
                v-model="logSearchQuery"
                label="Search logs"
                prepend-icon="mdi-magnify"
                clearable
                hide-details
                dense
                @input="filterLogs"
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-select
                v-model="logLevel"
                :items="['All Levels', 'Info', 'Warning', 'Error', 'Debug']"
                label="Log Level"
                prepend-icon="mdi-filter-variant"
                hide-details
                dense
                @change="filterLogs"
              ></v-select>
            </v-col>
          </v-row>

          <div v-if="logsLoading" class="d-flex justify-center align-center my-5">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
          <div v-else-if="logsError" class="text-center red--text">
            {{ logsError }}
          </div>
          <div v-else-if="logs.length === 0" class="text-center grey--text">
            No logs available
          </div>
          <div v-else-if="filteredLogs.length === 0" class="text-center grey--text">
            No logs match your filter criteria
          </div>
          <v-sheet v-else class="logs-container pa-2" color="grey lighten-4" rounded>
            <pre class="logs-content"><span v-for="(log, index) in filteredLogs" :key="index" :class="getLogLevelClass(log)">{{ log }}
</span></pre>
          </v-sheet>

          <!-- Log Stats -->
          <div class="d-flex justify-space-between mt-2 text-caption grey--text">
            <span>Showing {{ filteredLogs.length }} of {{ logs.length }} log entries</span>
            <span v-if="container.status === 'running'">
              <v-icon small color="success" v-if="autoRefreshLogs">mdi-autorenew</v-icon>
              Auto-refresh {{ autoRefreshLogs ? 'enabled' : 'disabled' }}
            </span>
          </div>
        </v-card-text>
      </v-card>
    </template>

    <!-- Action Confirmation Dialogs -->

    <!-- Start Confirmation Dialog -->
    <v-dialog v-model="startDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Start Container</v-card-title>
        <v-card-text>
          Are you sure you want to start the container <strong>{{ container?.name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="startDialog = false">
            Cancel
          </v-btn>
          <v-btn color="success" text @click="startContainer">
            Start
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Stop Confirmation Dialog -->
    <v-dialog v-model="stopDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Stop Container</v-card-title>
        <v-card-text>
          Are you sure you want to stop the container <strong>{{ container?.name }}</strong>?
          Any running processes inside the container will be terminated.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="stopDialog = false">
            Cancel
          </v-btn>
          <v-btn color="error" text @click="stopContainer">
            Stop
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Restart Confirmation Dialog -->
    <v-dialog v-model="restartDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Restart Container</v-card-title>
        <v-card-text>
          Are you sure you want to restart the container <strong>{{ container?.name }}</strong>?
          The container will be stopped and then started again.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="restartDialog = false">
            Cancel
          </v-btn>
          <v-btn color="warning" text @click="restartContainer">
            Restart
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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

    <!-- Container Inspect Dialog -->
    <v-dialog v-model="showInspectDialog" fullscreen hide-overlay transition="dialog-bottom-transition">
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="showInspectDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Container Inspection: {{ container?.name }}</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
        <v-card-text class="pa-0">
          <container-inspect
            :container-id="containerId"
            :inspect-data="inspectData"
            @show-snackbar="showSnackbar"
          ></container-inspect>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions, mapState } from 'vuex';
import ContainerStats from '@/components/containers/ContainerStats.vue';
import ContainerInspect from '@/components/containers/ContainerInspect.vue';

export default {
  name: 'ContainerDetail',
  components: {
    ContainerStats,
    ContainerInspect,
  },
  data() {
    return {
      loading: true,
      error: null,
      container: null,
      logs: [],
      filteredLogs: [],
      logsLoading: false,
      logsError: null,
      logSearchQuery: '',
      logLevel: 'All Levels',
      logTailLines: 100,
      autoRefreshLogs: false,
      labelSearch: '',
      logRefreshInterval: null,
      deleteDialog: false,
      startDialog: false,
      stopDialog: false,
      restartDialog: false,
      actionInProgress: false,
      actionType: null,
      showInspectDialog: false,
      inspectData: null,
      inspectLoading: false,
      inspectError: null,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
    ...mapState('containers', {
      storeContainer: 'currentContainer',
      storeLoading: 'loading',
      storeError: 'error',
    }),
    containerId() {
      return this.$route.params.id;
    },
    filteredLabels() {
      if (!this.container?.labels) return {};

      if (!this.labelSearch) return this.container.labels;

      const search = this.labelSearch.toLowerCase();
      const result = {};

      Object.entries(this.container.labels).forEach(([key, value]) => {
        if (key.toLowerCase().includes(search) ||
            (value && value.toLowerCase().includes(search))) {
          result[key] = value;
        }
      });

      return result;
    },
  },
  created() {
    this.fetchContainer();
    this.fetchLogs();
  },

  mounted() {
    // Set up auto-refresh for logs if container is running
    this.setupLogRefresh();
  },

  beforeDestroy() {
    // Clear the log refresh interval when component is destroyed
    this.clearLogRefreshInterval();
  },

  watch: {
    storeContainer(newContainer) {
      if (newContainer) {
        this.container = newContainer;
        this.loading = false;
      }
    },
    storeError(newError) {
      if (newError) {
        this.error = newError;
        this.loading = false;
        this.actionInProgress = false;
      }
    },
    'container.status': {
      handler(newStatus) {
        // Update log refresh when container status changes
        this.setupLogRefresh();

        // If container is now running, fetch fresh logs
        if (newStatus === 'running') {
          this.fetchLogs();
        }
      },
      immediate: false
    },
    autoRefreshLogs(newValue) {
      // Show feedback when auto-refresh is toggled
      if (newValue) {
        this.showSnackbar('Auto-refresh enabled', 'info');
      }
    },
  },
  methods: {
    ...mapActions({
      getContainer: 'containers/getContainer',
      startContainerAction: 'containers/startContainer',
      stopContainerAction: 'containers/stopContainer',
      restartContainerAction: 'containers/restartContainer',
      removeContainerAction: 'containers/removeContainer',
      getContainerLogs: 'containers/getContainerLogs',
      clearError: 'containers/clearError',
    }),

    async fetchContainer() {
      this.loading = true;
      this.error = null;

      try {
        await this.getContainer(this.containerId);

        // If we're still using mock data, use this instead
        if (!this.storeContainer) {
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
        }
      } catch (error) {
        this.error = 'Failed to load container details. Please try again.';
        this.loading = false;
      }
    },
    async fetchLogs() {
      this.logsLoading = true;
      this.logsError = null;

      try {
        // Try to get logs from the API
        const response = await this.getContainerLogs({
          id: this.containerId,
          tail: this.logTailLines === 'all' ? null : this.logTailLines
        }).catch(() => null);

        if (response && response.logs) {
          this.logs = response.logs;
          this.filterLogs();
          this.logsLoading = false;
        } else {
          // Mock data for development
          setTimeout(() => {
          this.logs = [
            `2025-03-16T19:00:00.000Z [INFO] Container ${this.containerId} started`,
            `2025-03-16T19:00:01.000Z [INFO] Container ${this.containerId} running`,
            `2025-03-16T19:00:02.000Z [INFO] Container ${this.containerId} healthy`,
            `2025-03-16T19:00:03.000Z [DEBUG] Container ${this.containerId} processing request`,
            `2025-03-16T19:00:04.000Z [INFO] Container ${this.containerId} request completed`,
            `2025-03-16T19:00:05.000Z [WARNING] Container ${this.containerId} high memory usage detected`,
            `2025-03-16T19:00:06.000Z [ERROR] Container ${this.containerId} failed to connect to database`,
            `2025-03-16T19:00:07.000Z [INFO] Container ${this.containerId} retrying database connection`,
            `2025-03-16T19:00:08.000Z [INFO] Container ${this.containerId} database connection established`,
            `2025-03-16T19:00:09.000Z [DEBUG] Container ${this.containerId} processing another request`,
          ];
          this.filterLogs();
          this.logsLoading = false;
        }, 1000);
        }
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
    showStartDialog() {
      this.startDialog = true;
    },

    async startContainer() {
      this.startDialog = false;
      this.actionInProgress = true;
      this.actionType = 'start';
      this.clearError();

      try {
        await this.startContainerAction(this.containerId);
        this.actionInProgress = false;
        this.showSnackbar('Container started successfully', 'success');
        this.fetchLogs();
      } catch (error) {
        this.showSnackbar(`Failed to start container: ${error.message}`, 'error');
        this.actionInProgress = false;
      }
    },
    showStopDialog() {
      this.stopDialog = true;
    },

    async stopContainer() {
      this.stopDialog = false;
      this.actionInProgress = true;
      this.actionType = 'stop';
      this.clearError();

      try {
        await this.stopContainerAction(this.containerId);
        this.actionInProgress = false;
        this.showSnackbar('Container stopped successfully', 'success');
      } catch (error) {
        this.showSnackbar(`Failed to stop container: ${error.message}`, 'error');
        this.actionInProgress = false;
      }
    },
    showRestartDialog() {
      this.restartDialog = true;
    },

    async restartContainer() {
      this.restartDialog = false;
      this.actionInProgress = true;
      this.actionType = 'restart';
      this.clearError();

      try {
        await this.restartContainerAction(this.containerId);
        this.actionInProgress = false;
        this.showSnackbar('Container restarted successfully', 'success');
        this.fetchLogs();
      } catch (error) {
        this.showSnackbar(`Failed to restart container: ${error.message}`, 'error');
        this.actionInProgress = false;
      }
    },
    showDeleteDialog() {
      this.deleteDialog = true;
    },
    async deleteContainer() {
      this.deleteDialog = false;
      this.actionInProgress = true;
      this.actionType = 'delete';
      this.clearError();

      try {
        await this.removeContainerAction(this.containerId);
        this.actionInProgress = false;
        this.showSnackbar('Container deleted successfully', 'success');
        this.$router.push('/containers');
      } catch (error) {
        this.showSnackbar(`Failed to delete container: ${error.message}`, 'error');
        this.actionInProgress = false;
      }
    },

    showSnackbar(text, color = 'info') {
      this.$store.dispatch('showSnackbar', { text, color });
    },

    // Additional container actions
    openTerminal() {
      if (this.container.status !== 'running') {
        this.showSnackbar('Container must be running to open terminal', 'warning');
        return;
      }

      this.$router.push(`/containers/${this.containerId}/terminal`);
    },

    openStats() {
      if (this.container.status !== 'running') {
        this.showSnackbar('Container must be running to view stats', 'warning');
        return;
      }

      // Scroll to stats section
      const statsElement = document.querySelector('.container-stats');
      if (statsElement) {
        statsElement.scrollIntoView({ behavior: 'smooth' });
      }
    },

    async openInspect() {
      this.showInspectDialog = true;

      try {
        // Fetch the container inspect data using Vuex
        await this.$store.dispatch('containers/inspectContainer', this.containerId);
        this.inspectData = this.$store.state.containers.inspectData;
      } catch (error) {
        this.showSnackbar('Failed to load container inspect data', 'error');
      }
    },

    // Log management methods
    filterLogs() {
      if (!this.logs || this.logs.length === 0) {
        this.filteredLogs = [];
        return;
      }

      let filtered = [...this.logs];

      // Filter by search query
      if (this.logSearchQuery) {
        const query = this.logSearchQuery.toLowerCase();
        filtered = filtered.filter(log => log.toLowerCase().includes(query));
      }

      // Filter by log level
      if (this.logLevel !== 'All Levels') {
        const level = this.logLevel.toUpperCase();
        filtered = filtered.filter(log => log.includes(`[${level}]`));
      }

      this.filteredLogs = filtered;
    },

    getLogLevelClass(log) {
      if (log.includes('[ERROR]')) return 'log-error';
      if (log.includes('[WARNING]')) return 'log-warning';
      if (log.includes('[INFO]')) return 'log-info';
      if (log.includes('[DEBUG]')) return 'log-debug';
      return '';
    },

    downloadLogs() {
      if (!this.logs || this.logs.length === 0) {
        this.showSnackbar('No logs available to download', 'warning');
        return;
      }

      const content = this.logs.join('\n');
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.container.name}-logs-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.showSnackbar('Logs downloaded successfully', 'success');
    },

    clearLogs() {
      this.logs = [];
      this.filteredLogs = [];
      this.showSnackbar('Logs cleared', 'info');
    },

    setupLogRefresh() {
      // Clear any existing interval
      this.clearLogRefreshInterval();

      // Set up auto-refresh if container is running
      if (this.container && this.container.status === 'running') {
        this.logRefreshInterval = setInterval(() => {
          if (this.autoRefreshLogs && !this.logsLoading) {
            this.fetchLogs();
          }
        }, 5000); // Refresh every 5 seconds
      }
    },

    clearLogRefreshInterval() {
      if (this.logRefreshInterval) {
        clearInterval(this.logRefreshInterval);
        this.logRefreshInterval = null;
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
  max-height: 400px;
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

.log-info {
  color: #2196F3;
}

.log-warning {
  color: #FB8C00;
}

.log-error {
  color: #F44336;
  font-weight: bold;
}

.log-debug {
  color: #9E9E9E;
}

.logs-tail-select {
  max-width: 100px;
}
</style>
