<template>
  <div class="monitoring-dashboard">
    <h1 class="text-h4 mb-4">Monitoring Dashboard</h1>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- System Overview -->
      <v-row>
        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="primary">mdi-cpu-64-bit</v-icon>
              CPU Usage
            </v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :rotate="-90"
                :size="100"
                :width="15"
                :value="systemMetrics.cpu_usage"
                :color="getResourceColor(systemMetrics.cpu_usage)"
              >
                <span class="text-h5">{{ systemMetrics.cpu_usage }}%</span>
              </v-progress-circular>
              <div class="mt-2">
                <small>{{ systemMetrics.cpu_cores }} Cores</small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="green">mdi-memory</v-icon>
              Memory Usage
            </v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :rotate="-90"
                :size="100"
                :width="15"
                :value="systemMetrics.memory_usage_percent"
                :color="getResourceColor(systemMetrics.memory_usage_percent)"
              >
                <span class="text-h5">{{ systemMetrics.memory_usage_percent }}%</span>
              </v-progress-circular>
              <div class="mt-2">
                <small>{{ formatSize(systemMetrics.memory_used) }} / {{ formatSize(systemMetrics.memory_total) }}</small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="blue">mdi-harddisk</v-icon>
              Disk Usage
            </v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :rotate="-90"
                :size="100"
                :width="15"
                :value="systemMetrics.disk_usage_percent"
                :color="getResourceColor(systemMetrics.disk_usage_percent)"
              >
                <span class="text-h5">{{ systemMetrics.disk_usage_percent }}%</span>
              </v-progress-circular>
              <div class="mt-2">
                <small>{{ formatSize(systemMetrics.disk_used) }} / {{ formatSize(systemMetrics.disk_total) }}</small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="purple">mdi-docker</v-icon>
              Docker Stats
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h5">{{ containerStats.running }}</div>
                  <div class="text-subtitle-1 success--text">Running</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h5">{{ containerStats.total }}</div>
                  <div class="text-subtitle-1">Total</div>
                </v-col>
              </v-row>
              <v-divider class="my-2"></v-divider>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h5">{{ imageStats.count }}</div>
                  <div class="text-subtitle-1">Images</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h5">{{ volumeStats.count }}</div>
                  <div class="text-subtitle-1">Volumes</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Resource Usage Charts -->
      <v-row>
        <v-col cols="12" md="6">
          <v-card class="mb-4">
            <v-card-title>
              CPU Usage History
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="cpuTimeRange" mandatory>
                <v-btn small value="1h">1h</v-btn>
                <v-btn small value="6h">6h</v-btn>
                <v-btn small value="24h">24h</v-btn>
                <v-btn small value="7d">7d</v-btn>
              </v-btn-toggle>
            </v-card-title>
            <v-card-text>
              <canvas id="cpuChart" height="250"></canvas>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card class="mb-4">
            <v-card-title>
              Memory Usage History
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="memoryTimeRange" mandatory>
                <v-btn small value="1h">1h</v-btn>
                <v-btn small value="6h">6h</v-btn>
                <v-btn small value="24h">24h</v-btn>
                <v-btn small value="7d">7d</v-btn>
              </v-btn-toggle>
            </v-card-title>
            <v-card-text>
              <canvas id="memoryChart" height="250"></canvas>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Container Resource Usage -->
      <h2 class="text-h5 mb-3">Container Resource Usage</h2>
      <v-card class="mb-4">
        <v-data-table
          :headers="containerHeaders"
          :items="containerResources"
          :items-per-page="5"
          :sort-by="['cpu_percent']"
          :sort-desc="[true]"
          class="elevation-1"
        >
          <!-- Name Column -->
          <template v-slot:item.name="{ item }">
            <router-link :to="`/containers/${item.id}`" class="text-decoration-none">
              {{ item.name }}
            </router-link>
          </template>

          <!-- CPU Column -->
          <template v-slot:item.cpu_percent="{ item }">
            <v-progress-linear
              :value="item.cpu_percent"
              height="20"
              :color="getResourceColor(item.cpu_percent)"
              striped
            >
              <template v-slot:default>
                <strong>{{ item.cpu_percent.toFixed(1) }}%</strong>
              </template>
            </v-progress-linear>
          </template>

          <!-- Memory Column -->
          <template v-slot:item.memory_percent="{ item }">
            <v-progress-linear
              :value="item.memory_percent"
              height="20"
              :color="getResourceColor(item.memory_percent)"
              striped
            >
              <template v-slot:default>
                <strong>{{ item.memory_percent.toFixed(1) }}%</strong>
              </template>
            </v-progress-linear>
            <div class="text-caption">
              {{ formatSize(item.memory_usage) }}
            </div>
          </template>

          <!-- Network Column -->
          <template v-slot:item.network="{ item }">
            <div>
              <v-icon small color="success">mdi-arrow-down</v-icon>
              {{ formatSize(item.network_rx) }}/s
            </div>
            <div>
              <v-icon small color="info">mdi-arrow-up</v-icon>
              {{ formatSize(item.network_tx) }}/s
            </div>
          </template>

          <!-- Disk Column -->
          <template v-slot:item.disk="{ item }">
            <div>
              <v-icon small color="success">mdi-arrow-down</v-icon>
              {{ formatSize(item.disk_read) }}/s
            </div>
            <div>
              <v-icon small color="info">mdi-arrow-up</v-icon>
              {{ formatSize(item.disk_write) }}/s
            </div>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              :to="`/containers/${item.id}`"
              title="View Details"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="showContainerMetrics(item)"
              title="View Metrics"
            >
              <v-icon small>mdi-chart-line</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- Alerts and Anomalies -->
      <h2 class="text-h5 mb-3">Alerts and Anomalies</h2>
      <v-row>
        <v-col cols="12">
          <v-expansion-panels>
            <v-expansion-panel
              v-for="(alert, i) in alerts"
              :key="i"
            >
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon
                    :color="getAlertSeverityColor(alert.severity)"
                    class="mr-2"
                  >
                    mdi-alert-circle
                  </v-icon>
                  <span>{{ alert.title }}</span>
                  <v-chip
                    class="ml-2"
                    x-small
                    :color="getAlertSeverityColor(alert.severity)"
                    text-color="white"
                  >
                    {{ alert.severity }}
                  </v-chip>
                  <v-spacer></v-spacer>
                  <span class="text-caption">{{ formatDate(alert.timestamp) }}</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <p>{{ alert.description }}</p>
                <div v-if="alert.resource">
                  <strong>Resource:</strong> {{ alert.resource.name }} ({{ alert.resource.type }})
                </div>
                <div v-if="alert.metrics && alert.metrics.length > 0">
                  <strong>Metrics:</strong>
                  <ul>
                    <li v-for="(metric, j) in alert.metrics" :key="j">
                      {{ metric.name }}: {{ metric.value }} {{ metric.unit }}
                    </li>
                  </ul>
                </div>
                <div class="d-flex mt-2">
                  <v-btn
                    color="primary"
                    text
                    small
                    @click="acknowledgeAlert(alert)"
                    v-if="!alert.acknowledged"
                  >
                    <v-icon left small>mdi-check</v-icon>
                    Acknowledge
                  </v-btn>
                  <v-btn
                    color="success"
                    text
                    small
                    @click="resolveAlert(alert)"
                    v-if="!alert.resolved"
                  >
                    <v-icon left small>mdi-check-all</v-icon>
                    Resolve
                  </v-btn>
                  <v-btn
                    color="info"
                    text
                    small
                    :to="getResourceLink(alert.resource)"
                    v-if="alert.resource"
                  >
                    <v-icon left small>mdi-eye</v-icon>
                    View Resource
                  </v-btn>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-card v-if="alerts.length === 0" class="text-center pa-5">
            <v-icon size="64" color="success">mdi-check-circle</v-icon>
            <h3 class="text-h5 mt-4">No active alerts</h3>
            <p class="text-body-1 mt-2">
              All systems are operating normally
            </p>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Container Metrics Dialog -->
    <v-dialog v-model="containerMetricsDialog" max-width="800">
      <v-card>
        <v-card-title class="headline">
          {{ selectedContainer?.name }} Metrics
          <v-spacer></v-spacer>
          <v-btn icon @click="containerMetricsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-tabs v-model="activeMetricTab">
            <v-tab>CPU</v-tab>
            <v-tab>Memory</v-tab>
            <v-tab>Network</v-tab>
            <v-tab>Disk</v-tab>
          </v-tabs>
          <v-tabs-items v-model="activeMetricTab">
            <v-tab-item>
              <div class="pa-4">
                <canvas id="containerCpuChart" height="250"></canvas>
              </div>
            </v-tab-item>
            <v-tab-item>
              <div class="pa-4">
                <canvas id="containerMemoryChart" height="250"></canvas>
              </div>
            </v-tab-item>
            <v-tab-item>
              <div class="pa-4">
                <canvas id="containerNetworkChart" height="250"></canvas>
              </div>
            </v-tab-item>
            <v-tab-item>
              <div class="pa-4">
                <canvas id="containerDiskChart" height="250"></canvas>
              </div>
            </v-tab-item>
          </v-tabs-items>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="containerMetricsDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
// Import Chart.js for real-time charts
import Chart from 'chart.js/auto';
import {
  getResourceStatsSummary,
  getHostMetricsHistory,
  getContainerMetrics,
  getContainerMetricsHistory,
  createContainerStatsWebSocket
} from '@/services/monitoring';

export default {
  name: 'MonitoringDashboard',
  data() {
    return {
      loading: true,
      error: null,
      refreshInterval: null,
      systemMetrics: {
        cpu_usage: 0,
        cpu_cores: 0,
        memory_usage_percent: 0,
        memory_used: 0,
        memory_total: 0,
        disk_usage_percent: 0,
        disk_used: 0,
        disk_total: 0,
      },
      containerStats: {
        running: 0,
        total: 0,
      },
      imageStats: {
        count: 0,
      },
      volumeStats: {
        count: 0,
      },
      cpuTimeRange: '1h',
      memoryTimeRange: '1h',
      containerHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'CPU', value: 'cpu_percent', sortable: true },
        { text: 'Memory', value: 'memory_percent', sortable: true },
        { text: 'Network I/O', value: 'network', sortable: false },
        { text: 'Disk I/O', value: 'disk', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      containerResources: [],
      alerts: [],
      containerMetricsDialog: false,
      selectedContainer: null,
      activeMetricTab: 0,
      charts: {
        cpu: null,
        memory: null,
        containerCpu: null,
        containerMemory: null,
        containerNetwork: null,
        containerDisk: null,
      },
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  watch: {
    cpuTimeRange() {
      this.updateCpuChart();
    },
    memoryTimeRange() {
      this.updateMemoryChart();
    },
  },
  created() {
    this.fetchMonitoringData();
  },
  mounted() {
    // Set up auto-refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.fetchMonitoringData(false);
    }, 30000);
  },
  beforeDestroy() {
    // Clear the refresh interval when component is destroyed
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async fetchMonitoringData(showLoading = true) {
      if (showLoading) {
        this.loading = true;
      }
      this.error = null;

      try {
        // Get resource stats summary from API
        const summary = await getResourceStatsSummary();

        // Update system metrics
        this.systemMetrics = {
          cpu_usage: summary.cpu_usage,
          cpu_cores: summary.cpu_cores,
          memory_usage_percent: summary.memory_usage_percent,
          memory_used: summary.memory_used,
          memory_total: summary.memory_total,
          disk_usage_percent: summary.disk_usage_percent,
          disk_used: summary.disk_used,
          disk_total: summary.disk_total,
        };

        // Update container stats
        this.containerStats = {
          running: summary.running_containers,
          total: summary.container_count,
        };

        // Update image stats
        this.imageStats = {
          count: summary.image_count,
        };

        // Update volume stats
        this.volumeStats = {
          count: summary.volume_count,
        };

        // Fetch container resources
        // In a real implementation, this would be fetched from the API
        // For now, we'll use mock data
        // For now, we'll use mock data for container resources
        this.containerResources = [
          {
            id: 'c1',
            name: 'web-server',
            cpu_percent: 12.5,
            memory_percent: 8.2,
            memory_usage: 1024 * 1024 * 256, // 256 MB
            network: { rx: '1.2 MB/s', tx: '3.5 MB/s' },
            disk: { read: '0.5 MB/s', write: '0.2 MB/s' },
          },
          {
            id: 'c2',
            name: 'api-service',
            cpu_percent: 28.7,
            memory_percent: 15.3,
            memory_usage: 1024 * 1024 * 512, // 512 MB
            network: { rx: '2.8 MB/s', tx: '1.7 MB/s' },
            disk: { read: '0.3 MB/s', write: '0.8 MB/s' },
          },
          {
            id: 'c3',
            name: 'database',
            cpu_percent: 45.2,
            memory_percent: 62.8,
            memory_usage: 1024 * 1024 * 1024 * 2, // 2 GB
            network: { rx: '0.5 MB/s', tx: '0.3 MB/s' },
            disk: { read: '4.2 MB/s', write: '3.8 MB/s' },
          },
          {
            id: 'c4',
            name: 'cache',
            cpu_percent: 5.3,
            memory_percent: 28.1,
            memory_usage: 1024 * 1024 * 768, // 768 MB
            network: { rx: '4.5 MB/s', tx: '3.2 MB/s' },
            disk: { read: '0.1 MB/s', write: '0.05 MB/s' },
          },
          {
            id: 'c5',
            name: 'worker',
            cpu_percent: 78.9,
            memory_percent: 42.6,
            memory_usage: 1024 * 1024 * 896, // 896 MB
            network: { rx: '0.3 MB/s', tx: '0.2 MB/s' },
            disk: { read: '2.1 MB/s', write: '1.8 MB/s' },
          },
        ];

        // Mock alerts for development
        this.alerts = [
          {
            id: 'a1',
            title: 'High CPU Usage',
            description: 'Container "worker" is using excessive CPU resources (78.9%). This may indicate a performance issue or resource contention.',
            severity: 'warning',
            timestamp: '2025-03-17T05:45:00Z',
            acknowledged: false,
            resolved: false,
            resource: {
              type: 'container',
              id: 'c5',
              name: 'worker',
            },
            metrics: [
              {
                name: 'CPU Usage',
                value: 78.9,
                unit: '%',
              },
            ],
          },
          {
            id: 'a2',
            title: 'Memory Leak Detected',
            description: 'Container "database" shows a steady increase in memory usage over the past 6 hours, indicating a possible memory leak.',
            severity: 'critical',
            timestamp: '2025-03-17T04:30:00Z',
            acknowledged: true,
            resolved: false,
            resource: {
              type: 'container',
              id: 'c3',
              name: 'database',
            },
            metrics: [
              {
                name: 'Memory Usage',
                value: 62.8,
                unit: '%',
              },
              {
                name: 'Memory Growth Rate',
                value: 5.2,
                unit: '%/hour',
              },
            ],
          },
          {
            id: 'a3',
            title: 'Disk Space Warning',
            description: 'Host system is running low on disk space (68.3% used). Consider cleaning up unused images and volumes.',
            severity: 'warning',
            timestamp: '2025-03-17T03:15:00Z',
            acknowledged: false,
            resolved: false,
            resource: {
              type: 'host',
              id: 'host',
              name: 'Docker Host',
            },
            metrics: [
              {
                name: 'Disk Usage',
                value: 68.3,
                unit: '%',
              },
            ],
          },
        ];

        this.loading = false;

        // Initialize charts after data is loaded
        this.$nextTick(() => {
          this.initCharts();
        });
      } catch (error) {
        this.error = 'Failed to load monitoring data. Please try again.';
        this.loading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    formatSize(bytes) {
      if (bytes === 0) return '0 Bytes';

      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));

      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    getResourceColor(percent) {
      if (percent >= 90) {
        return 'error';
      } else if (percent >= 70) {
        return 'warning';
      } else if (percent >= 50) {
        return 'info';
      } else {
        return 'success';
      }
    },
    getAlertSeverityColor(severity) {
      switch (severity) {
        case 'critical':
          return 'error';
        case 'warning':
          return 'warning';
        case 'info':
          return 'info';
        default:
          return 'grey';
      }
    },
    getResourceLink(resource) {
      if (!resource) return '#';

      switch (resource.type) {
        case 'container':
          return `/containers/${resource.id}`;
        case 'image':
          return `/images/${resource.id}`;
        case 'volume':
          return `/volumes/${resource.id}`;
        case 'network':
          return `/networks/${resource.id}`;
        default:
          return '#';
      }
    },
    showContainerMetrics(container) {
      this.selectedContainer = container;
      this.containerMetricsDialog = true;

      // Initialize container charts after dialog is shown
      this.$nextTick(() => {
        this.initContainerCharts();
      });
    },
    acknowledgeAlert(alert) {
      // In a real implementation, this would call the API
      // await axios.post(`/api/monitoring/alerts/${alert.id}/acknowledge`, {}, {
      //   headers: { Authorization: `Bearer ${this.token}` },
      // });

      // Mock implementation
      alert.acknowledged = true;
    },
    resolveAlert(alert) {
      // In a real implementation, this would call the API
      // await axios.post(`/api/monitoring/alerts/${alert.id}/resolve`, {}, {
      //   headers: { Authorization: `Bearer ${this.token}` },
      // });

      // Mock implementation
      alert.resolved = true;

      // Remove the alert from the list after a short delay
      setTimeout(() => {
        this.alerts = this.alerts.filter(a => a.id !== alert.id);
      }, 500);
    },
    async initCharts() {
      try {
        // Get CPU metrics history
        const cpuHistory = await getHostMetricsHistory('cpu', 24);

        // Get memory metrics history
        const memoryHistory = await getHostMetricsHistory('memory', 24);

        // Prepare data for charts
        const cpuLabels = [];
        const cpuData = [];
        const memoryLabels = [];
        const memoryData = [];

        // Process CPU data
        cpuHistory.forEach(item => {
          const date = new Date(item.timestamp);
          cpuLabels.push(date.toLocaleTimeString());
          cpuData.push(item.data.percent);
        });

        // Process memory data
        memoryHistory.forEach(item => {
          const date = new Date(item.timestamp);
          memoryLabels.push(date.toLocaleTimeString());
          memoryData.push(item.data.virtual.percent);
        });

        // Create CPU chart
        const cpuCtx = document.getElementById('cpuChart');
        if (cpuCtx) {
          if (this.charts.cpu) {
            this.charts.cpu.destroy();
          }

          this.charts.cpu = new Chart(cpuCtx, {
            type: 'line',
            data: {
              labels: cpuLabels,
              datasets: [
                {
                  label: 'CPU Usage (%)',
                  data: cpuData,
                  borderColor: '#1976D2',
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'CPU Usage (%)',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }

        // Create memory chart
        const memoryCtx = document.getElementById('memoryChart');
        if (memoryCtx) {
          if (this.charts.memory) {
            this.charts.memory.destroy();
          }

          this.charts.memory = new Chart(memoryCtx, {
            type: 'line',
            data: {
              labels: memoryLabels,
              datasets: [
                {
                  label: 'Memory Usage (%)',
                  data: memoryData,
                  borderColor: '#4CAF50',
                  backgroundColor: 'rgba(76, 175, 80, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Memory Usage (%)',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }
      } catch (error) {
        console.error('Error initializing charts:', error);
      }
    },
    async updateCpuChart() {
      try {
        // Get hours from time range
        let hours = 1;
        switch (this.cpuTimeRange) {
          case '1h':
            hours = 1;
            break;
          case '6h':
            hours = 6;
            break;
          case '12h':
            hours = 12;
            break;
          case '24h':
            hours = 24;
            break;
        }

        // Get CPU metrics history
        const cpuHistory = await getHostMetricsHistory('cpu', hours);

        // Prepare data for chart
        const cpuLabels = [];
        const cpuData = [];

        // Process CPU data
        cpuHistory.forEach(item => {
          const date = new Date(item.timestamp);
          cpuLabels.push(date.toLocaleTimeString());
          cpuData.push(item.data.percent);
        });

        // Update chart data
        if (this.charts.cpu) {
          this.charts.cpu.data.labels = cpuLabels;
          this.charts.cpu.data.datasets[0].data = cpuData;
          this.charts.cpu.update();
        }
      } catch (error) {
        console.error('Error updating CPU chart:', error);
      }
    },
    async updateMemoryChart() {
      try {
        // Get hours from time range
        let hours = 1;
        switch (this.memoryTimeRange) {
          case '1h':
            hours = 1;
            break;
          case '6h':
            hours = 6;
            break;
          case '12h':
            hours = 12;
            break;
          case '24h':
            hours = 24;
            break;
        }

        // Get memory metrics history
        const memoryHistory = await getHostMetricsHistory('memory', hours);

        // Prepare data for chart
        const memoryLabels = [];
        const memoryData = [];

        // Process memory data
        memoryHistory.forEach(item => {
          const date = new Date(item.timestamp);
          memoryLabels.push(date.toLocaleTimeString());
          memoryData.push(item.data.virtual.percent);
        });

        // Update chart data
        if (this.charts.memory) {
          this.charts.memory.data.labels = memoryLabels;
          this.charts.memory.data.datasets[0].data = memoryData;
          this.charts.memory.update();
        }
      } catch (error) {
        console.error('Error updating memory chart:', error);
      }
    },
    async initContainerCharts() {
      if (!this.selectedContainer) return;

      try {
        // In a real implementation, we would fetch container metrics history from the API
        // For now, we'll create mock data

        // Create mock data for container charts
        const timeLabels = [];
        const cpuData = [];
        const memoryData = [];
        const networkRxData = [];
        const networkTxData = [];
        const diskReadData = [];
        const diskWriteData = [];

        // Generate time labels for the last 24 hours
        const now = new Date();
        for (let i = 23; i >= 0; i--) {
          const time = new Date(now);
          time.setHours(now.getHours() - i);
          timeLabels.push(time.toLocaleTimeString());

          // Generate random data points
          cpuData.push(Math.random() * 50 + (this.selectedContainer.cpu_percent - 25));
          memoryData.push(Math.random() * 30 + (this.selectedContainer.memory_percent - 15));
          networkRxData.push(Math.random() * 5 + 0.5);
          networkTxData.push(Math.random() * 3 + 0.2);
          diskReadData.push(Math.random() * 5 + 0.5);
          diskWriteData.push(Math.random() * 3 + 0.2);
        }

        // Create CPU chart
        const containerCpuCtx = document.getElementById('containerCpuChart');
        if (containerCpuCtx) {
          if (this.charts.containerCpu) {
            this.charts.containerCpu.destroy();
          }

          this.charts.containerCpu = new Chart(containerCpuCtx, {
            type: 'line',
            data: {
              labels: timeLabels,
              datasets: [
                {
                  label: 'CPU Usage (%)',
                  data: cpuData,
                  borderColor: '#1976D2',
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'CPU Usage (%)',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }

        // Create Memory chart
        const containerMemoryCtx = document.getElementById('containerMemoryChart');
        if (containerMemoryCtx) {
          if (this.charts.containerMemory) {
            this.charts.containerMemory.destroy();
          }

          this.charts.containerMemory = new Chart(containerMemoryCtx, {
            type: 'line',
            data: {
              labels: timeLabels,
              datasets: [
                {
                  label: 'Memory Usage (%)',
                  data: memoryData,
                  borderColor: '#4CAF50',
                  backgroundColor: 'rgba(76, 175, 80, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Memory Usage (%)',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }

        // Create Network chart
        const containerNetworkCtx = document.getElementById('containerNetworkChart');
        if (containerNetworkCtx) {
          if (this.charts.containerNetwork) {
            this.charts.containerNetwork.destroy();
          }

          this.charts.containerNetwork = new Chart(containerNetworkCtx, {
            type: 'line',
            data: {
              labels: timeLabels,
              datasets: [
                {
                  label: 'Network RX (MB/s)',
                  data: networkRxData,
                  borderColor: '#2196F3',
                  backgroundColor: 'rgba(33, 150, 243, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
                {
                  label: 'Network TX (MB/s)',
                  data: networkTxData,
                  borderColor: '#FF9800',
                  backgroundColor: 'rgba(255, 152, 0, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'MB/s',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }

        // Create Disk chart
        const containerDiskCtx = document.getElementById('containerDiskChart');
        if (containerDiskCtx) {
          if (this.charts.containerDisk) {
            this.charts.containerDisk.destroy();
          }

          this.charts.containerDisk = new Chart(containerDiskCtx, {
            type: 'line',
            data: {
              labels: timeLabels,
              datasets: [
                {
                  label: 'Disk Read (MB/s)',
                  data: diskReadData,
                  borderColor: '#4CAF50',
                  backgroundColor: 'rgba(76, 175, 80, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
                {
                  label: 'Disk Write (MB/s)',
                  data: diskWriteData,
                  borderColor: '#9C27B0',
                  backgroundColor: 'rgba(156, 39, 176, 0.1)',
                  fill: true,
                  tension: 0.4,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'MB/s',
                  },
                },
                x: {
                  title: {
                    display: true,
                    text: 'Time',
                  },
                },
              },
            },
          });
        }
      } catch (error) {
        console.error('Error initializing container charts:', error);
      }
    }
  }
};
</script>

<style scoped>
.monitoring-dashboard {
  padding: 16px;
}
</style>
