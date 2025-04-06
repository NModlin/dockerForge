<template>
  <div class="container-stats">
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-chart-line</v-icon>
        Resource Usage
        <v-spacer></v-spacer>
        <v-switch
          v-model="realTimeUpdates"
          label="Real-time updates"
          hide-details
          dense
          class="mt-0 pt-0"
          color="primary"
        ></v-switch>
      </v-card-title>
      <v-card-text>
        <v-tabs v-model="activeTab" background-color="transparent" grow>
          <v-tab>Overview</v-tab>
          <v-tab>CPU</v-tab>
          <v-tab>Memory</v-tab>
          <v-tab>Network</v-tab>
          <v-tab>Disk I/O</v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <!-- Overview Tab -->
          <v-tab-item>
            <v-row class="mt-4">
              <v-col cols="12" md="6">
                <div class="mb-4">
                  <div class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1">CPU Usage</span>
                    <span class="font-weight-bold">{{ currentStats.cpu_percent }}%</span>
                  </div>
                  <v-progress-linear
                    color="primary"
                    height="10"
                    rounded
                    :value="currentStats.cpu_percent"
                  ></v-progress-linear>
                </div>
                <div class="mb-4">
                  <div class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1">Memory Usage</span>
                    <span class="font-weight-bold">{{ formatBytes(currentStats.memory_usage) }} / {{ formatBytes(currentStats.memory_limit) }}</span>
                  </div>
                  <v-progress-linear
                    color="info"
                    height="10"
                    rounded
                    :value="currentStats.memory_percent"
                  ></v-progress-linear>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="mb-4">
                  <div class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1">Network I/O</span>
                    <span class="font-weight-bold">↓ {{ formatBytes(currentStats.network_rx_bytes) }} / ↑ {{ formatBytes(currentStats.network_tx_bytes) }}</span>
                  </div>
                </div>
                <div class="mb-4">
                  <div class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1">Disk I/O</span>
                    <span class="font-weight-bold">↓ {{ formatBytes(currentStats.block_read_bytes) }} / ↑ {{ formatBytes(currentStats.block_write_bytes) }}</span>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-tab-item>

          <!-- CPU Tab -->
          <v-tab-item>
            <v-row class="mt-4">
              <v-col cols="12">
                <div class="chart-wrapper" style="height: 300px;">
                  <line-chart
                    :chart-data="cpuChartData"
                    :height="300"
                    :chart-options="cpuChartOptions"
                  ></line-chart>
                </div>
                <div class="d-flex justify-space-between mt-2">
                  <div>
                    <div class="text-subtitle-2">Current: {{ currentStats.cpu_percent }}%</div>
                    <div class="text-caption">Average: {{ calculateAverage(cpuHistory) }}%</div>
                  </div>
                  <div>
                    <div class="text-subtitle-2">Max: {{ calculateMax(cpuHistory) }}%</div>
                    <div class="text-caption">Min: {{ calculateMin(cpuHistory) }}%</div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-tab-item>

          <!-- Memory Tab -->
          <v-tab-item>
            <v-row class="mt-4">
              <v-col cols="12">
                <div class="chart-wrapper" style="height: 300px;">
                  <line-chart
                    :chart-data="memoryChartData"
                    :height="300"
                    :chart-options="memoryChartOptions"
                  ></line-chart>
                </div>
                <div class="d-flex justify-space-between mt-2">
                  <div>
                    <div class="text-subtitle-2">Current: {{ formatBytes(currentStats.memory_usage) }}</div>
                    <div class="text-caption">Limit: {{ formatBytes(currentStats.memory_limit) }}</div>
                  </div>
                  <div>
                    <div class="text-subtitle-2">Usage: {{ currentStats.memory_percent }}%</div>
                    <div class="text-caption">Average: {{ calculateAverage(memoryHistory) }}%</div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-tab-item>

          <!-- Network Tab -->
          <v-tab-item>
            <v-row class="mt-4">
              <v-col cols="12">
                <div class="chart-wrapper" style="height: 300px;">
                  <line-chart
                    :chart-data="networkChartData"
                    :height="300"
                    :chart-options="networkChartOptions"
                  ></line-chart>
                </div>
                <div class="d-flex justify-space-between mt-2">
                  <div>
                    <div class="text-subtitle-2">Received: {{ formatBytes(currentStats.network_rx_bytes) }}</div>
                    <div class="text-caption">Rate: {{ formatBytesPerSecond(networkRxRate) }}</div>
                  </div>
                  <div>
                    <div class="text-subtitle-2">Transmitted: {{ formatBytes(currentStats.network_tx_bytes) }}</div>
                    <div class="text-caption">Rate: {{ formatBytesPerSecond(networkTxRate) }}</div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-tab-item>

          <!-- Disk I/O Tab -->
          <v-tab-item>
            <v-row class="mt-4">
              <v-col cols="12">
                <div class="chart-wrapper" style="height: 300px;">
                  <line-chart
                    :chart-data="diskChartData"
                    :height="300"
                    :chart-options="diskChartOptions"
                  ></line-chart>
                </div>
                <div class="d-flex justify-space-between mt-2">
                  <div>
                    <div class="text-subtitle-2">Read: {{ formatBytes(currentStats.block_read_bytes) }}</div>
                    <div class="text-caption">Rate: {{ formatBytesPerSecond(diskReadRate) }}</div>
                  </div>
                  <div>
                    <div class="text-subtitle-2">Write: {{ formatBytes(currentStats.block_write_bytes) }}</div>
                    <div class="text-caption">Rate: {{ formatBytesPerSecond(diskWriteRate) }}</div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-tab-item>
        </v-tabs-items>

        <div class="text-caption text-right mt-2">
          <span v-if="lastUpdated">Last updated: {{ formatDate(lastUpdated) }}</span>
          <span v-else>Waiting for data...</span>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import LineChart from '@/components/charts/LineChart.vue';

export default {
  name: 'ContainerStats',
  components: {
    LineChart
  },
  props: {
    containerId: {
      type: String,
      required: true
    },
    initialStats: {
      type: Object,
      default: () => ({
        cpu_percent: 0,
        memory_usage: 0,
        memory_limit: 0,
        memory_percent: 0,
        network_rx_bytes: 0,
        network_tx_bytes: 0,
        block_read_bytes: 0,
        block_write_bytes: 0
      })
    }
  },
  data() {
    return {
      activeTab: 0,
      realTimeUpdates: true,
      socket: null,
      currentStats: { ...this.initialStats },
      lastUpdated: null,
      
      // History arrays for charts
      cpuHistory: [],
      memoryHistory: [],
      networkRxHistory: [],
      networkTxHistory: [],
      diskReadHistory: [],
      diskWriteHistory: [],
      timeLabels: [],
      
      // Rates
      networkRxRate: 0,
      networkTxRate: 0,
      diskReadRate: 0,
      diskWriteRate: 0,
      
      // Max data points to keep
      maxDataPoints: 60,
      
      // Previous values for rate calculation
      prevNetworkRx: 0,
      prevNetworkTx: 0,
      prevDiskRead: 0,
      prevDiskWrite: 0,
      prevTimestamp: null
    };
  },
  computed: {
    cpuChartData() {
      return {
        labels: this.timeLabels,
        datasets: [
          {
            label: 'CPU Usage (%)',
            data: this.cpuHistory,
            borderColor: '#1976D2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ]
      };
    },
    memoryChartData() {
      return {
        labels: this.timeLabels,
        datasets: [
          {
            label: 'Memory Usage (%)',
            data: this.memoryHistory,
            borderColor: '#00BCD4',
            backgroundColor: 'rgba(0, 188, 212, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ]
      };
    },
    networkChartData() {
      return {
        labels: this.timeLabels,
        datasets: [
          {
            label: 'Received (bytes/s)',
            data: this.networkRxHistory,
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          },
          {
            label: 'Transmitted (bytes/s)',
            data: this.networkTxHistory,
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          }
        ]
      };
    },
    diskChartData() {
      return {
        labels: this.timeLabels,
        datasets: [
          {
            label: 'Read (bytes/s)',
            data: this.diskReadHistory,
            borderColor: '#9C27B0',
            backgroundColor: 'rgba(156, 39, 176, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          },
          {
            label: 'Write (bytes/s)',
            data: this.diskWriteHistory,
            borderColor: '#F44336',
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4
          }
        ]
      };
    },
    cpuChartOptions() {
      return {
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            callbacks: {
              label: (context) => `CPU: ${context.raw.toFixed(2)}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            title: {
              display: true,
              text: 'CPU Usage (%)'
            }
          }
        }
      };
    },
    memoryChartOptions() {
      return {
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            callbacks: {
              label: (context) => `Memory: ${context.raw.toFixed(2)}%`
            }
          }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            title: {
              display: true,
              text: 'Memory Usage (%)'
            }
          }
        }
      };
    },
    networkChartOptions() {
      return {
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.raw;
                return `${context.dataset.label}: ${this.formatBytes(value)}/s`;
              }
            }
          }
        },
        scales: {
          y: {
            min: 0,
            title: {
              display: true,
              text: 'Network I/O (bytes/s)'
            },
            ticks: {
              callback: (value) => this.formatBytes(value)
            }
          }
        }
      };
    },
    diskChartOptions() {
      return {
        plugins: {
          legend: {
            display: true
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.raw;
                return `${context.dataset.label}: ${this.formatBytes(value)}/s`;
              }
            }
          }
        },
        scales: {
          y: {
            min: 0,
            title: {
              display: true,
              text: 'Disk I/O (bytes/s)'
            },
            ticks: {
              callback: (value) => this.formatBytes(value)
            }
          }
        }
      };
    }
  },
  watch: {
    initialStats: {
      handler(newStats) {
        this.currentStats = { ...newStats };
      },
      deep: true
    },
    realTimeUpdates(newValue) {
      if (newValue) {
        this.connectWebSocket();
      } else {
        this.disconnectWebSocket();
      }
    }
  },
  mounted() {
    this.fetchInitialStats();
    if (this.realTimeUpdates) {
      this.connectWebSocket();
    }
  },
  beforeDestroy() {
    this.disconnectWebSocket();
  },
  methods: {
    async fetchInitialStats() {
      try {
        const response = await this.$store.dispatch('containers/getContainerStats', this.containerId);
        this.updateStats(response);
        
        // Also fetch historical data
        await this.fetchHistoricalStats();
      } catch (error) {
        console.error('Error fetching container stats:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to load container stats',
          color: 'error'
        });
      }
    },
    
    async fetchHistoricalStats() {
      try {
        const cpuHistory = await this.$store.dispatch('containers/getContainerStatsHistory', {
          id: this.containerId,
          metric_type: 'cpu',
          hours: 1
        });
        
        const memoryHistory = await this.$store.dispatch('containers/getContainerStatsHistory', {
          id: this.containerId,
          metric_type: 'memory',
          hours: 1
        });
        
        const networkHistory = await this.$store.dispatch('containers/getContainerStatsHistory', {
          id: this.containerId,
          metric_type: 'network',
          hours: 1
        });
        
        const diskHistory = await this.$store.dispatch('containers/getContainerStatsHistory', {
          id: this.containerId,
          metric_type: 'disk',
          hours: 1
        });
        
        // Process CPU history
        const cpuData = cpuHistory
          .filter(item => item.unit === '%')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Process memory history
        const memoryData = memoryHistory
          .filter(item => item.unit === '%')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Process network history
        const networkRxData = networkHistory
          .filter(item => item.labels.type === 'rx')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        const networkTxData = networkHistory
          .filter(item => item.labels.type === 'tx')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Process disk history
        const diskReadData = diskHistory
          .filter(item => item.labels.type === 'read')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        const diskWriteData = diskHistory
          .filter(item => item.labels.type === 'write')
          .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Limit to maxDataPoints
        const limit = this.maxDataPoints;
        
        // Update chart data
        this.timeLabels = cpuData.slice(-limit).map(item => {
          const date = new Date(item.timestamp);
          return date.toLocaleTimeString();
        });
        
        this.cpuHistory = cpuData.slice(-limit).map(item => item.value);
        this.memoryHistory = memoryData.slice(-limit).map(item => item.value);
        
        // Calculate rates for network and disk
        this.calculateHistoricalRates(networkRxData, networkTxData, diskReadData, diskWriteData);
        
      } catch (error) {
        console.error('Error fetching historical stats:', error);
      }
    },
    
    calculateHistoricalRates(networkRxData, networkTxData, diskReadData, diskWriteData) {
      // Calculate network rates
      const networkRxRates = this.calculateRates(networkRxData);
      const networkTxRates = this.calculateRates(networkTxData);
      
      // Calculate disk rates
      const diskReadRates = this.calculateRates(diskReadData);
      const diskWriteRates = this.calculateRates(diskWriteData);
      
      // Limit to maxDataPoints
      const limit = this.maxDataPoints;
      
      this.networkRxHistory = networkRxRates.slice(-limit);
      this.networkTxHistory = networkTxRates.slice(-limit);
      this.diskReadHistory = diskReadRates.slice(-limit);
      this.diskWriteHistory = diskWriteRates.slice(-limit);
    },
    
    calculateRates(data) {
      if (data.length < 2) return [];
      
      const rates = [];
      for (let i = 1; i < data.length; i++) {
        const prevValue = data[i-1].value;
        const currValue = data[i].value;
        const prevTime = new Date(data[i-1].timestamp).getTime();
        const currTime = new Date(data[i].timestamp).getTime();
        
        // Calculate time difference in seconds
        const timeDiff = (currTime - prevTime) / 1000;
        
        if (timeDiff > 0) {
          // Calculate rate in bytes per second
          const rate = (currValue - prevValue) / timeDiff;
          rates.push(Math.max(0, rate)); // Ensure rate is not negative
        }
      }
      
      return rates;
    },
    
    connectWebSocket() {
      // Close existing connection if any
      this.disconnectWebSocket();
      
      // Create new WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/stats/ws/${this.containerId}`;
      
      this.socket = new WebSocket(wsUrl);
      
      // Set up event handlers
      this.socket.onopen = () => {
        console.log('WebSocket connection established');
      };
      
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'stats') {
          this.updateStats(data.stats);
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Error connecting to stats service',
          color: 'error'
        });
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
        // Try to reconnect after a delay if real-time updates are still enabled
        if (this.realTimeUpdates) {
          setTimeout(() => {
            this.connectWebSocket();
          }, 5000);
        }
      };
      
      // Send ping every 30 seconds to keep connection alive
      this.pingInterval = setInterval(() => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    },
    
    disconnectWebSocket() {
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
      
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    },
    
    updateStats(stats) {
      const now = new Date();
      const timestamp = now.toLocaleTimeString();
      
      // Update current stats
      this.currentStats = { ...stats };
      this.lastUpdated = now;
      
      // Add new data point to history arrays
      this.timeLabels.push(timestamp);
      this.cpuHistory.push(stats.cpu_percent);
      this.memoryHistory.push(stats.memory_percent);
      
      // Calculate rates
      this.calculateRates(stats);
      
      // Limit arrays to maxDataPoints
      if (this.timeLabels.length > this.maxDataPoints) {
        this.timeLabels.shift();
        this.cpuHistory.shift();
        this.memoryHistory.shift();
        this.networkRxHistory.shift();
        this.networkTxHistory.shift();
        this.diskReadHistory.shift();
        this.diskWriteHistory.shift();
      }
    },
    
    calculateRates(stats) {
      const now = new Date().getTime();
      
      if (this.prevTimestamp) {
        // Calculate time difference in seconds
        const timeDiff = (now - this.prevTimestamp) / 1000;
        
        if (timeDiff > 0) {
          // Calculate network rates
          this.networkRxRate = (stats.network_rx_bytes - this.prevNetworkRx) / timeDiff;
          this.networkTxRate = (stats.network_tx_bytes - this.prevNetworkTx) / timeDiff;
          
          // Calculate disk rates
          this.diskReadRate = (stats.block_read_bytes - this.prevDiskRead) / timeDiff;
          this.diskWriteRate = (stats.block_write_bytes - this.prevDiskWrite) / timeDiff;
          
          // Add to history
          this.networkRxHistory.push(this.networkRxRate);
          this.networkTxHistory.push(this.networkTxRate);
          this.diskReadHistory.push(this.diskReadRate);
          this.diskWriteHistory.push(this.diskWriteRate);
        }
      }
      
      // Update previous values
      this.prevNetworkRx = stats.network_rx_bytes;
      this.prevNetworkTx = stats.network_tx_bytes;
      this.prevDiskRead = stats.block_read_bytes;
      this.prevDiskWrite = stats.block_write_bytes;
      this.prevTimestamp = now;
    },
    
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0 || bytes === undefined) return '0 B';
      
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
      
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    
    formatBytesPerSecond(bytes, decimals = 2) {
      return this.formatBytes(bytes, decimals) + '/s';
    },
    
    formatDate(date) {
      return date.toLocaleString();
    },
    
    calculateAverage(array) {
      if (!array.length) return 0;
      const sum = array.reduce((a, b) => a + b, 0);
      return (sum / array.length).toFixed(2);
    },
    
    calculateMax(array) {
      if (!array.length) return 0;
      return Math.max(...array).toFixed(2);
    },
    
    calculateMin(array) {
      if (!array.length) return 0;
      return Math.min(...array).toFixed(2);
    }
  }
};
</script>

<style scoped>
.container-stats {
  width: 100%;
}

.chart-wrapper {
  position: relative;
  width: 100%;
}
</style>
