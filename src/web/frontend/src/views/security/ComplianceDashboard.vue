<template>
  <div class="compliance-dashboard">
    <div class="d-flex align-center mb-4">
      <h1 class="text-h4">Compliance Dashboard</h1>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        class="mr-2"
        :to="{ name: 'ComplianceReports' }"
      >
        <v-icon left>mdi-file-document</v-icon>
        Compliance Reports
      </v-btn>
      <v-btn
        color="primary"
        class="mr-2"
        :to="{ name: 'ComplianceHistory' }"
      >
        <v-icon left>mdi-chart-timeline</v-icon>
        Compliance History
      </v-btn>
      <v-btn
        color="primary"
        :to="{ name: 'PolicyViolations' }"
      >
        <v-icon left>mdi-alert</v-icon>
        Policy Violations
      </v-btn>
    </div>

    <!-- Filter Controls -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-filter</v-icon>
        Compliance Filters
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.timeRange"
              :items="timeRangeOptions"
              label="Time Range"
              @change="updateFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.resourceTypes"
              :items="resourceTypeOptions"
              label="Resource Types"
              multiple
              chips
              small-chips
              @change="updateFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.policyIds"
              :items="policyOptions"
              label="Policies"
              multiple
              chips
              small-chips
              @change="updateFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.severityLevels"
              :items="severityOptions"
              label="Severity Levels"
              multiple
              chips
              small-chips
              @change="updateFilters"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading State -->
    <div v-if="complianceLoading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="complianceError" type="error" class="mb-4">
      {{ complianceError }}
    </v-alert>

    <!-- Dashboard Content -->
    <template v-else-if="complianceData">
      <!-- Compliance Overview -->
      <v-row>
        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left :color="getComplianceScoreColor(complianceScore)">
                mdi-check-decagram
              </v-icon>
              Compliance Score
            </v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :rotate="-90"
                :size="150"
                :width="15"
                :value="complianceScore"
                :color="getComplianceScoreColor(complianceScore)"
              >
                <span class="text-h4">{{ complianceScore }}</span>
              </v-progress-circular>
              <div class="mt-4">
                <v-chip
                  :color="getComplianceScoreColor(complianceScore)"
                  text-color="white"
                >
                  {{ getComplianceScoreLabel(complianceScore) }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="primary">mdi-shield-check</v-icon>
              Policy Compliance
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 success--text">{{ complianceData.compliant_policies }}</div>
                  <div class="text-subtitle-1">Compliant</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 error--text">{{ complianceData.non_compliant_policies }}</div>
                  <div class="text-subtitle-1">Non-Compliant</div>
                </v-col>
              </v-row>
              <v-progress-linear
                :value="(complianceData.compliant_policies / (complianceData.compliant_policies + complianceData.non_compliant_policies)) * 100"
                color="success"
                height="20"
                class="mt-2"
              >
                <template v-slot:default>
                  {{ Math.round((complianceData.compliant_policies / (complianceData.compliant_policies + complianceData.non_compliant_policies)) * 100) }}%
                </template>
              </v-progress-linear>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="info">mdi-docker</v-icon>
              Resource Compliance
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 success--text">{{ complianceData.compliant_resources }}</div>
                  <div class="text-subtitle-1">Compliant</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 error--text">{{ complianceData.non_compliant_resources }}</div>
                  <div class="text-subtitle-1">Non-Compliant</div>
                </v-col>
              </v-row>
              <v-progress-linear
                :value="(complianceData.compliant_resources / (complianceData.compliant_resources + complianceData.non_compliant_resources)) * 100"
                color="success"
                height="20"
                class="mt-2"
              >
                <template v-slot:default>
                  {{ Math.round((complianceData.compliant_resources / (complianceData.compliant_resources + complianceData.non_compliant_resources)) * 100) }}%
                </template>
              </v-progress-linear>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Policy Compliance Breakdown -->
      <h2 class="text-h5 mb-3">Policy Compliance</h2>
      <v-card class="mb-4">
        <v-data-table
          :headers="policyHeaders"
          :items="policyComplianceStats"
          :items-per-page="5"
          class="elevation-1"
        >
          <!-- Policy Column -->
          <template v-slot:item.policy_name="{ item }">
            <router-link
              :to="{ name: 'PolicyDetail', params: { id: item.policy_id } }"
              class="text-decoration-none"
            >
              {{ item.policy_name }}
            </router-link>
          </template>

          <!-- Status Column -->
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="item.compliant ? 'success' : 'error'"
              text-color="white"
              small
            >
              {{ item.compliant ? 'Compliant' : 'Non-Compliant' }}
            </v-chip>
          </template>

          <!-- Violations Column -->
          <template v-slot:item.violations="{ item }">
            <v-chip
              v-if="item.violations > 0"
              color="error"
              small
            >
              {{ item.violations }} {{ item.violations === 1 ? 'Violation' : 'Violations' }}
            </v-chip>
            <span v-else>No violations</span>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              :to="{ name: 'PolicyDetail', params: { id: item.policy_id } }"
              title="View Policy"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              v-if="!item.compliant"
              icon
              small
              :to="{ name: 'PolicyViolations' }"
              title="View Violations"
              color="error"
            >
              <v-icon small>mdi-alert</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- Resource Compliance Breakdown -->
      <h2 class="text-h5 mb-3">Resource Compliance</h2>
      <v-row>
        <v-col cols="12" md="6" lg="3" v-for="(resource, index) in resourceComplianceStats" :key="index">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left :color="getResourceTypeColor(resource.resource_type)">
                {{ getResourceTypeIcon(resource.resource_type) }}
              </v-icon>
              {{ capitalizeFirstLetter(resource.resource_type) }}s
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 success--text">{{ resource.compliant_count }}</div>
                  <div class="text-subtitle-1">Compliant</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h4 error--text">{{ resource.non_compliant_count }}</div>
                  <div class="text-subtitle-1">Non-Compliant</div>
                </v-col>
              </v-row>
              <v-progress-linear
                :value="(resource.compliant_count / (resource.compliant_count + resource.non_compliant_count)) * 100"
                color="success"
                height="20"
                class="mt-2"
              >
                <template v-slot:default>
                  {{ Math.round((resource.compliant_count / (resource.compliant_count + resource.non_compliant_count)) * 100) }}%
                </template>
              </v-progress-linear>
              <v-btn
                color="primary"
                block
                class="mt-4"
                :to="getResourceListRoute(resource.resource_type)"
              >
                View {{ capitalizeFirstLetter(resource.resource_type) }}s
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Recent Compliance Reports -->
      <h2 class="text-h5 mb-3">Recent Compliance Reports</h2>
      <v-card v-if="recentReports.length > 0" class="mb-4">
        <v-data-table
          :headers="reportHeaders"
          :items="recentReports"
          :items-per-page="5"
          class="elevation-1"
        >
          <!-- Report Name Column -->
          <template v-slot:item.name="{ item }">
            <router-link
              :to="{ name: 'ComplianceReportDetail', params: { id: item.id } }"
              class="text-decoration-none"
            >
              {{ item.name }}
            </router-link>
          </template>

          <!-- Generated Date Column -->
          <template v-slot:item.generated_at="{ item }">
            {{ formatDate(item.generated_at) }}
          </template>

          <!-- Compliance Score Column -->
          <template v-slot:item.compliance_score="{ item }">
            <v-chip
              :color="getComplianceScoreColor(item.compliance_score)"
              text-color="white"
              small
            >
              {{ item.compliance_score }}%
            </v-chip>
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              :to="{ name: 'ComplianceReportDetail', params: { id: item.id } }"
              title="View Report"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="exportReport(item.id, 'PDF')"
              title="Export as PDF"
              color="error"
            >
              <v-icon small>mdi-file-pdf-box</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="exportReport(item.id, 'CSV')"
              title="Export as CSV"
              color="success"
            >
              <v-icon small>mdi-file-excel</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
      <v-card v-else class="pa-4 text-center mb-4">
        <p>No compliance reports generated yet.</p>
        <v-btn
          color="primary"
          :to="{ name: 'ComplianceReports' }"
        >
          Generate Report
        </v-btn>
      </v-card>
    </template>
    <v-card v-else class="pa-4 text-center">
      <v-icon color="info" large class="mb-2">mdi-information</v-icon>
      <p class="text-h6">No compliance data available</p>
      <p class="text-subtitle-1">Adjust your filters or generate a compliance report</p>
    </v-card>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'ComplianceDashboard',
  data() {
    return {
      filters: {
        timeRange: '30d',
        resourceTypes: ['image', 'container', 'volume', 'network'],
        policyIds: [],
        severityLevels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
      },
      timeRangeOptions: [
        { text: 'Last 24 Hours', value: '24h' },
        { text: 'Last 7 Days', value: '7d' },
        { text: 'Last 30 Days', value: '30d' },
        { text: 'Last 90 Days', value: '90d' },
        { text: 'Last Year', value: '1y' }
      ],
      resourceTypeOptions: [
        { text: 'Images', value: 'image' },
        { text: 'Containers', value: 'container' },
        { text: 'Volumes', value: 'volume' },
        { text: 'Networks', value: 'network' }
      ],
      severityOptions: [
        { text: 'Critical', value: 'CRITICAL' },
        { text: 'High', value: 'HIGH' },
        { text: 'Medium', value: 'MEDIUM' },
        { text: 'Low', value: 'LOW' }
      ],
      policyHeaders: [
        { text: 'Policy', value: 'policy_name', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Violations', value: 'violations', sortable: true },
        { text: 'Last Evaluated', value: 'last_evaluated', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      reportHeaders: [
        { text: 'Report Name', value: 'name', sortable: true },
        { text: 'Generated', value: 'generated_at', sortable: true },
        { text: 'Compliance Score', value: 'compliance_score', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ]
    };
  },
  computed: {
    ...mapGetters({
      complianceData: 'security/complianceData',
      complianceLoading: 'security/isComplianceLoading',
      complianceError: 'security/complianceErrorMessage',
      complianceScore: 'security/complianceScore',
      policyComplianceStats: 'security/policyComplianceStats',
      resourceComplianceStats: 'security/resourceComplianceStats',
      recentReports: 'security/recentReports',
      policies: 'security/policies',
      storedFilters: 'security/complianceFilters'
    }),
    policyOptions() {
      return this.policies.map(policy => ({
        text: policy.name,
        value: policy.id
      }));
    }
  },
  created() {
    // Initialize filters from store if available
    if (this.storedFilters) {
      this.filters = { ...this.storedFilters };
    }
    
    // Fetch required data
    this.fetchPolicies();
    this.fetchComplianceData();
    this.fetchComplianceReports();
  },
  methods: {
    ...mapActions({
      fetchComplianceData: 'security/fetchComplianceData',
      fetchComplianceReports: 'security/fetchComplianceReports',
      fetchPolicies: 'security/fetchPolicies',
      updateComplianceFilters: 'security/updateComplianceFilters',
      exportComplianceReport: 'security/exportComplianceReport'
    }),
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getComplianceScoreColor(score) {
      if (score >= 90) {
        return 'success';
      } else if (score >= 70) {
        return 'warning';
      } else {
        return 'error';
      }
    },
    getComplianceScoreLabel(score) {
      if (score >= 90) {
        return 'Compliant';
      } else if (score >= 70) {
        return 'Needs Improvement';
      } else {
        return 'Non-Compliant';
      }
    },
    getResourceTypeColor(type) {
      switch (type) {
        case 'image':
          return 'primary';
        case 'container':
          return 'success';
        case 'volume':
          return 'warning';
        case 'network':
          return 'info';
        default:
          return 'grey';
      }
    },
    getResourceTypeIcon(type) {
      switch (type) {
        case 'image':
          return 'mdi-docker';
        case 'container':
          return 'mdi-package-variant-closed';
        case 'volume':
          return 'mdi-database';
        case 'network':
          return 'mdi-lan';
        default:
          return 'mdi-help-circle';
      }
    },
    getResourceListRoute(type) {
      switch (type) {
        case 'image':
          return '/images';
        case 'container':
          return '/containers';
        case 'volume':
          return '/volumes';
        case 'network':
          return '/networks';
        default:
          return '/';
      }
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    updateFilters() {
      this.updateComplianceFilters(this.filters);
    },
    async exportReport(reportId, format) {
      try {
        await this.exportComplianceReport({ reportId, format });
        this.$emit('show-notification', {
          type: 'success',
          message: `Report exported as ${format} successfully`
        });
      } catch (error) {
        console.error('Error exporting report:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to export report'
        });
      }
    }
  }
};
</script>

<style scoped>
.compliance-dashboard {
  padding: 16px;
}
</style>
