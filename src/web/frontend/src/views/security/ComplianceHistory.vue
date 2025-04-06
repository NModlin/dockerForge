<template>
  <div class="compliance-history">
    <v-container fluid>
      <div class="d-flex align-center mb-4">
        <h1 class="text-h4">
          <v-icon large left>mdi-chart-timeline</v-icon>
          Compliance History
        </h1>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          class="mr-2"
          :to="{ name: 'ComplianceDashboard' }"
        >
          <v-icon left>mdi-view-dashboard</v-icon>
          Dashboard
        </v-btn>
        <v-btn
          color="primary"
          :to="{ name: 'ComplianceReports' }"
        >
          <v-icon left>mdi-file-document</v-icon>
          Reports
        </v-btn>
      </div>

      <!-- Filters -->
      <v-card class="mb-4">
        <v-card-title>
          <v-icon left>mdi-filter</v-icon>
          Filters
          <v-spacer></v-spacer>
          <v-btn
            text
            color="primary"
            @click="resetFilters"
          >
            <v-icon left>mdi-refresh</v-icon>
            Reset
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.timeRange"
                label="Time Range"
                :items="timeRangeOptions"
                @change="applyFilters"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.resourceTypes"
                label="Resource Types"
                :items="resourceTypeOptions"
                multiple
                chips
                @change="applyFilters"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.severityLevels"
                label="Severity Levels"
                :items="severityLevelOptions"
                multiple
                chips
                @change="applyFilters"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.policyIds"
                label="Policies"
                :items="policyOptions"
                item-text="text"
                item-value="value"
                multiple
                chips
                @change="applyFilters"
              ></v-select>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Loading State -->
      <div v-if="complianceLoading" class="text-center pa-4">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4">Loading compliance history...</div>
      </div>

      <!-- Error State -->
      <v-alert
        v-else-if="complianceError"
        type="error"
        dismissible
        class="mt-4"
      >
        {{ complianceError }}
      </v-alert>

      <!-- Content -->
      <template v-else-if="complianceHistory && complianceHistory.length > 0">
        <!-- Compliance Score Trend Chart -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-chart-line</v-icon>
            Compliance Score Trend
          </v-card-title>
          <v-card-text>
            <div class="chart-container" style="height: 300px;">
              <compliance-trend-chart
                :data="complianceHistory"
                :time-range="filters.timeRange"
              ></compliance-trend-chart>
            </div>
          </v-card-text>
        </v-card>

        <!-- Resource Type Compliance Chart -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-chart-bar</v-icon>
            Resource Type Compliance
          </v-card-title>
          <v-card-text>
            <div class="chart-container" style="height: 300px;">
              <resource-compliance-chart
                :data="resourceComplianceData"
              ></resource-compliance-chart>
            </div>
          </v-card-text>
        </v-card>

        <!-- Policy Compliance History -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-shield-check</v-icon>
            Policy Compliance History
          </v-card-title>
          <v-data-table
            :headers="policyHeaders"
            :items="policyComplianceHistory"
            :items-per-page="10"
            class="elevation-1"
          >
            <!-- Policy Name Column -->
            <template v-slot:item.policy_name="{ item }">
              <router-link
                :to="{ name: 'PolicyDetail', params: { id: item.policy_id } }"
                class="text-decoration-none"
              >
                {{ item.policy_name }}
              </router-link>
            </template>

            <!-- Compliance Trend Column -->
            <template v-slot:item.trend="{ item }">
              <v-sparkline
                :value="item.compliance_history"
                :gradient="['#f72047', '#ffd200', '#1feaea']"
                :smooth="10"
                auto-draw
                line-width="2"
                padding="5"
                height="50"
              ></v-sparkline>
            </template>

            <!-- Current Status Column -->
            <template v-slot:item.current_status="{ item }">
              <v-chip
                :color="item.is_compliant ? 'success' : 'error'"
                text-color="white"
                small
              >
                {{ item.is_compliant ? 'Compliant' : 'Non-Compliant' }}
              </v-chip>
            </template>

            <!-- Violations Column -->
            <template v-slot:item.violations="{ item }">
              <v-chip
                v-if="item.violation_count > 0"
                color="error"
                small
              >
                {{ item.violation_count }} {{ item.violation_count === 1 ? 'Violation' : 'Violations' }}
              </v-chip>
              <span v-else>No violations</span>
            </template>
          </v-data-table>
        </v-card>

        <!-- Compliance Events Timeline -->
        <v-card>
          <v-card-title>
            <v-icon left>mdi-timeline</v-icon>
            Compliance Events Timeline
          </v-card-title>
          <v-card-text>
            <v-timeline dense>
              <v-timeline-item
                v-for="(event, index) in complianceEvents"
                :key="index"
                :color="getEventColor(event)"
                small
              >
                <template v-slot:opposite>
                  <span class="text-caption">{{ formatDate(event.timestamp) }}</span>
                </template>
                <v-card outlined>
                  <v-card-title class="text-subtitle-2">
                    {{ event.title }}
                  </v-card-title>
                  <v-card-text>
                    <div>{{ event.description }}</div>
                    <div v-if="event.resource_type && event.resource_name" class="mt-2">
                      <v-chip x-small class="mr-1">{{ event.resource_type }}</v-chip>
                      <router-link
                        :to="getResourceRoute(event)"
                        class="text-decoration-none"
                      >
                        {{ event.resource_name }}
                      </router-link>
                    </div>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </template>

      <!-- No Data State -->
      <v-card v-else class="text-center pa-4">
        <v-icon large color="grey lighten-1">mdi-chart-timeline-variant</v-icon>
        <p class="text-body-1 mt-2">No compliance history data available for the selected filters.</p>
        <p class="text-caption">Try changing your filter settings or generate a compliance report.</p>
        <v-btn
          color="primary"
          class="mt-2"
          :to="{ name: 'ComplianceReports' }"
        >
          Generate Report
        </v-btn>
      </v-card>
    </v-container>
  </div>
</template>

<script>
import { mapState, mapActions, mapMutations } from 'vuex';
import { format, parseISO } from 'date-fns';
import ComplianceTrendChart from '@/components/security/ComplianceTrendChart.vue';
import ResourceComplianceChart from '@/components/security/ResourceComplianceChart.vue';

export default {
  name: 'ComplianceHistory',
  
  components: {
    ComplianceTrendChart,
    ResourceComplianceChart
  },
  
  data() {
    return {
      filters: {
        timeRange: '30d',
        resourceTypes: ['image', 'container', 'volume', 'network'],
        policyIds: [],
        severityLevels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
      },
      timeRangeOptions: [
        { text: 'Last 7 Days', value: '7d' },
        { text: 'Last 30 Days', value: '30d' },
        { text: 'Last 90 Days', value: '90d' },
        { text: 'Last 6 Months', value: '180d' },
        { text: 'Last Year', value: '365d' }
      ],
      resourceTypeOptions: [
        { text: 'Images', value: 'image' },
        { text: 'Containers', value: 'container' },
        { text: 'Volumes', value: 'volume' },
        { text: 'Networks', value: 'network' }
      ],
      severityLevelOptions: [
        { text: 'Critical', value: 'CRITICAL' },
        { text: 'High', value: 'HIGH' },
        { text: 'Medium', value: 'MEDIUM' },
        { text: 'Low', value: 'LOW' }
      ],
      policyHeaders: [
        { text: 'Policy Name', value: 'policy_name', sortable: true },
        { text: 'Compliance Trend', value: 'trend', sortable: false },
        { text: 'Current Status', value: 'current_status', sortable: true },
        { text: 'Violations', value: 'violations', sortable: true },
        { text: 'Last Change', value: 'last_change', sortable: true }
      ]
    };
  },
  
  computed: {
    ...mapState('security', [
      'complianceLoading',
      'complianceError',
      'complianceHistory',
      'policies',
      'complianceFilters'
    ]),
    
    policyOptions() {
      return this.policies.map(policy => ({
        text: policy.name,
        value: policy.id
      }));
    },
    
    resourceComplianceData() {
      if (!this.complianceHistory || this.complianceHistory.length === 0) {
        return [];
      }
      
      // Get the latest data point
      const latestData = this.complianceHistory[this.complianceHistory.length - 1];
      
      return [
        {
          resource_type: 'Images',
          compliant: latestData.image_compliant || 0,
          non_compliant: latestData.image_non_compliant || 0
        },
        {
          resource_type: 'Containers',
          compliant: latestData.container_compliant || 0,
          non_compliant: latestData.container_non_compliant || 0
        },
        {
          resource_type: 'Volumes',
          compliant: latestData.volume_compliant || 0,
          non_compliant: latestData.volume_non_compliant || 0
        },
        {
          resource_type: 'Networks',
          compliant: latestData.network_compliant || 0,
          non_compliant: latestData.network_non_compliant || 0
        }
      ];
    },
    
    policyComplianceHistory() {
      if (!this.complianceHistory || this.complianceHistory.length === 0 || !this.policies) {
        return [];
      }
      
      return this.policies.map(policy => {
        // Extract compliance history for this policy
        const complianceHistory = this.complianceHistory.map(dataPoint => {
          const policyData = dataPoint.policy_compliance.find(p => p.policy_id === policy.id);
          return policyData ? (policyData.compliant ? 100 : 0) : 50; // 100 for compliant, 0 for non-compliant
        });
        
        // Get the latest data point for this policy
        const latestDataPoint = this.complianceHistory[this.complianceHistory.length - 1];
        const latestPolicyData = latestDataPoint.policy_compliance.find(p => p.policy_id === policy.id);
        
        return {
          policy_id: policy.id,
          policy_name: policy.name,
          compliance_history: complianceHistory,
          is_compliant: latestPolicyData ? latestPolicyData.compliant : true,
          violation_count: latestPolicyData ? latestPolicyData.violations : 0,
          last_change: latestPolicyData ? latestPolicyData.last_change : null
        };
      });
    },
    
    complianceEvents() {
      if (!this.complianceHistory || this.complianceHistory.length === 0) {
        return [];
      }
      
      // Extract significant events from the compliance history
      const events = [];
      
      // Add policy violation events
      this.complianceHistory.forEach(dataPoint => {
        dataPoint.policy_compliance.forEach(policyData => {
          if (policyData.violations > 0) {
            const policy = this.policies.find(p => p.id === policyData.policy_id);
            if (policy) {
              events.push({
                timestamp: dataPoint.timestamp,
                title: `Policy Violation: ${policy.name}`,
                description: `${policyData.violations} violation(s) detected`,
                type: 'violation',
                policy_id: policy.id,
                policy_name: policy.name
              });
            }
          }
        });
        
        // Add resource compliance events
        if (dataPoint.resource_events && dataPoint.resource_events.length > 0) {
          dataPoint.resource_events.forEach(event => {
            events.push({
              timestamp: event.timestamp,
              title: event.title,
              description: event.description,
              type: event.type,
              resource_type: event.resource_type,
              resource_id: event.resource_id,
              resource_name: event.resource_name
            });
          });
        }
      });
      
      // Sort events by timestamp (newest first)
      return events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }
  },
  
  created() {
    // Initialize filters from store
    this.filters = { ...this.complianceFilters };
    
    // Fetch data
    this.fetchPolicies();
    this.fetchComplianceHistory();
  },
  
  methods: {
    ...mapActions('security', [
      'fetchComplianceHistory',
      'fetchPolicies'
    ]),
    
    ...mapMutations('security', [
      'UPDATE_COMPLIANCE_FILTERS'
    ]),
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    
    getEventColor(event) {
      switch (event.type) {
        case 'violation':
          return 'error';
        case 'remediation':
          return 'success';
        case 'policy_change':
          return 'info';
        case 'resource_change':
          return 'warning';
        default:
          return 'grey';
      }
    },
    
    getResourceRoute(event) {
      if (!event.resource_type || !event.resource_id) {
        return { name: 'Dashboard' };
      }
      
      switch (event.resource_type) {
        case 'image':
          return { name: 'ImageDetail', params: { id: event.resource_id } };
        case 'container':
          return { name: 'ContainerDetail', params: { id: event.resource_id } };
        case 'volume':
          return { name: 'VolumeDetail', params: { id: event.resource_id } };
        case 'network':
          return { name: 'NetworkDetail', params: { id: event.resource_id } };
        default:
          return { name: 'Dashboard' };
      }
    },
    
    applyFilters() {
      // Update filters in store
      this.UPDATE_COMPLIANCE_FILTERS(this.filters);
      
      // Fetch data with new filters
      this.fetchComplianceHistory();
    },
    
    resetFilters() {
      this.filters = {
        timeRange: '30d',
        resourceTypes: ['image', 'container', 'volume', 'network'],
        policyIds: [],
        severityLevels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
      };
      
      this.applyFilters();
    }
  }
};
</script>

<style scoped>
.compliance-history {
  margin-bottom: 2rem;
}

.chart-container {
  position: relative;
  width: 100%;
}
</style>
