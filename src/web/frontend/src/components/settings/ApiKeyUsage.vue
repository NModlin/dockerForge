<template>
  <div class="api-key-usage">
    <v-card flat>
      <v-card-text>
        <div class="d-flex align-center mb-4">
          <h2 class="text-h5">API Key Usage</h2>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="refreshData"
            :loading="loading"
            :disabled="loading"
          >
            <v-icon left>mdi-refresh</v-icon>
            Refresh
          </v-btn>
        </div>

        <v-alert
          v-if="error"
          type="error"
          dismissible
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <!-- Loading State -->
        <div v-if="loading" class="d-flex justify-center align-center my-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <!-- No Data State -->
        <v-alert
          v-else-if="!usageStats || !usageStats.total_requests"
          type="info"
          outlined
          class="mb-4"
        >
          No usage data available for this API key yet.
        </v-alert>

        <!-- Usage Stats -->
        <template v-else>
          <!-- Usage Summary Cards -->
          <v-row>
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="usage-card">
                <v-card-text>
                  <div class="text-overline">Total Requests</div>
                  <div class="text-h4">{{ usageStats.total_requests }}</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="usage-card">
                <v-card-text>
                  <div class="text-overline">Today</div>
                  <div class="text-h4">{{ usageStats.requests_today }}</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="usage-card">
                <v-card-text>
                  <div class="text-overline">Success Rate</div>
                  <div class="text-h4">{{ usageStats.success_rate }}%</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card outlined class="usage-card">
                <v-card-text>
                  <div class="text-overline">Avg Response Time</div>
                  <div class="text-h4">{{ usageStats.avg_response_time }} ms</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Usage Charts -->
          <v-row class="mt-4">
            <v-col cols="12" md="8">
              <v-card outlined>
                <v-card-title>Usage Over Time</v-card-title>
                <v-card-text>
                  <canvas id="usageChart" height="250"></canvas>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card outlined>
                <v-card-title>Top Endpoints</v-card-title>
                <v-card-text>
                  <canvas id="endpointsChart" height="250"></canvas>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Usage Details -->
          <v-card outlined class="mt-4">
            <v-card-title>
              Usage Details
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
                class="ml-2"
              ></v-text-field>
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="usageRecords"
              :items-per-page="10"
              :search="search"
              :loading="detailsLoading"
              :footer-props="{
                'items-per-page-options': [5, 10, 25, 50],
                'items-per-page-text': 'Records per page'
              }"
              class="elevation-0"
            >
              <!-- Endpoint Column -->
              <template v-slot:item.endpoint="{ item }">
                <div class="font-weight-medium">{{ item.endpoint }}</div>
              </template>

              <!-- Method Column -->
              <template v-slot:item.method="{ item }">
                <v-chip
                  small
                  :color="getMethodColor(item.method)"
                  text-color="white"
                >
                  {{ item.method }}
                </v-chip>
              </template>

              <!-- Status Code Column -->
              <template v-slot:item.status_code="{ item }">
                <v-chip
                  small
                  :color="getStatusColor(item.status_code)"
                  text-color="white"
                >
                  {{ item.status_code }}
                </v-chip>
              </template>

              <!-- Response Time Column -->
              <template v-slot:item.response_time="{ item }">
                {{ item.response_time.toFixed(2) }} ms
              </template>

              <!-- Date Column -->
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
            </v-data-table>
          </v-card>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import Chart from 'chart.js/auto';

export default {
  name: 'ApiKeyUsage',
  props: {
    apiKeyId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      search: '',
      detailsLoading: false,
      usageRecords: [],
      charts: {
        usage: null,
        endpoints: null
      },
      headers: [
        { text: 'Endpoint', value: 'endpoint', sortable: true },
        { text: 'Method', value: 'method', sortable: true },
        { text: 'Status', value: 'status_code', sortable: true },
        { text: 'Response Time', value: 'response_time', sortable: true },
        { text: 'Date', value: 'created_at', sortable: true }
      ]
    };
  },
  computed: {
    ...mapGetters('apiKeys', [
      'getKeyUsageStats',
      'isUsageLoading',
      'getError'
    ]),
    
    loading() {
      return this.isUsageLoading;
    },
    
    error() {
      return this.getError;
    },
    
    usageStats() {
      return this.getKeyUsageStats;
    }
  },
  mounted() {
    this.loadData();
  },
  beforeDestroy() {
    // Destroy charts to prevent memory leaks
    if (this.charts.usage) {
      this.charts.usage.destroy();
    }
    if (this.charts.endpoints) {
      this.charts.endpoints.destroy();
    }
  },
  methods: {
    ...mapActions('apiKeys', [
      'fetchKeyUsageStats',
      'fetchKeyUsage'
    ]),
    
    async loadData() {
      await this.fetchKeyUsageStats(this.apiKeyId);
      await this.loadUsageRecords();
      this.$nextTick(() => {
        this.renderCharts();
      });
    },
    
    async loadUsageRecords() {
      this.detailsLoading = true;
      try {
        const params = {
          limit: 50,
          offset: 0
        };
        const records = await this.fetchKeyUsage({ keyId: this.apiKeyId, params });
        this.usageRecords = records;
      } catch (error) {
        console.error('Error loading usage records:', error);
      } finally {
        this.detailsLoading = false;
      }
    },
    
    refreshData() {
      this.loadData();
    },
    
    renderCharts() {
      if (!this.usageStats) return;
      
      this.renderUsageChart();
      this.renderEndpointsChart();
    },
    
    renderUsageChart() {
      const ctx = document.getElementById('usageChart');
      if (!ctx) return;
      
      // Destroy existing chart if it exists
      if (this.charts.usage) {
        this.charts.usage.destroy();
      }
      
      const usageData = this.usageStats.usage_over_time || [];
      
      // Prepare data for chart
      const labels = usageData.map(item => item.date);
      const data = usageData.map(item => item.count);
      
      // Create chart
      this.charts.usage = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Requests',
            data: data,
            backgroundColor: 'rgba(25, 118, 210, 0.2)',
            borderColor: 'rgba(25, 118, 210, 1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Number of Requests'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    },
    
    renderEndpointsChart() {
      const ctx = document.getElementById('endpointsChart');
      if (!ctx) return;
      
      // Destroy existing chart if it exists
      if (this.charts.endpoints) {
        this.charts.endpoints.destroy();
      }
      
      const endpointsData = this.usageStats.top_endpoints || [];
      
      // Prepare data for chart
      const labels = endpointsData.map(item => {
        // Shorten endpoint for display
        const endpoint = item.endpoint;
        return endpoint.length > 20 ? endpoint.substring(0, 20) + '...' : endpoint;
      });
      const data = endpointsData.map(item => item.count);
      
      // Create chart
      this.charts.endpoints = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: [
              'rgba(25, 118, 210, 0.7)',
              'rgba(76, 175, 80, 0.7)',
              'rgba(255, 193, 7, 0.7)',
              'rgba(244, 67, 54, 0.7)',
              'rgba(156, 39, 176, 0.7)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw || 0;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    },
    
    getMethodColor(method) {
      const colors = {
        GET: 'primary',
        POST: 'success',
        PUT: 'warning',
        DELETE: 'error',
        PATCH: 'info'
      };
      return colors[method] || 'grey';
    },
    
    getStatusColor(statusCode) {
      if (statusCode >= 200 && statusCode < 300) {
        return 'success';
      } else if (statusCode >= 300 && statusCode < 400) {
        return 'info';
      } else if (statusCode >= 400 && statusCode < 500) {
        return 'warning';
      } else {
        return 'error';
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.usage-card {
  height: 100%;
}
</style>
