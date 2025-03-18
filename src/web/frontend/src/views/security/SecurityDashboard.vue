<template>
  <div class="security-dashboard">
    <h1 class="text-h4 mb-4">Security Dashboard</h1>

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
      <!-- Security Overview -->
      <v-row>
        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left :color="getSecurityScoreColor(securityScore)">
                mdi-shield
              </v-icon>
              Security Score
            </v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :rotate="-90"
                :size="150"
                :width="15"
                :value="securityScore"
                :color="getSecurityScoreColor(securityScore)"
              >
                <span class="text-h4">{{ securityScore }}</span>
              </v-progress-circular>
              <div class="mt-4">
                <v-chip
                  :color="getSecurityScoreColor(securityScore)"
                  text-color="white"
                >
                  {{ getSecurityScoreLabel(securityScore) }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="error">mdi-alert</v-icon>
              Vulnerabilities
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="4" class="text-center">
                  <div class="text-h4 red--text">{{ vulnerabilityCounts.critical }}</div>
                  <div class="text-subtitle-1">Critical</div>
                </v-col>
                <v-col cols="4" class="text-center">
                  <div class="text-h4 orange--text">{{ vulnerabilityCounts.high }}</div>
                  <div class="text-subtitle-1">High</div>
                </v-col>
                <v-col cols="4" class="text-center">
                  <div class="text-h4 blue--text">{{ vulnerabilityCounts.medium + vulnerabilityCounts.low }}</div>
                  <div class="text-subtitle-1">Other</div>
                </v-col>
              </v-row>
              <v-btn
                color="primary"
                block
                class="mt-4"
                :to="'/security/vulnerabilities'"
              >
                View All Vulnerabilities
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="warning">mdi-check-decagram</v-icon>
              Compliance
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h4">{{ complianceStats.passed }}</div>
                  <div class="text-subtitle-1 success--text">Passed</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h4">{{ complianceStats.failed }}</div>
                  <div class="text-subtitle-1 error--text">Failed</div>
                </v-col>
              </v-row>
              <v-progress-linear
                :value="(complianceStats.passed / (complianceStats.passed + complianceStats.failed)) * 100"
                color="success"
                height="20"
                class="mt-2"
              >
                <template v-slot:default>
                  {{ Math.round((complianceStats.passed / (complianceStats.passed + complianceStats.failed)) * 100) }}%
                </template>
              </v-progress-linear>
              <v-btn
                color="primary"
                block
                class="mt-4"
                :to="'/security/compliance'"
              >
                View Compliance Report
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Recent Security Scans -->
      <h2 class="text-h5 mb-3">Recent Security Scans</h2>
      <v-card class="mb-4">
        <v-data-table
          :headers="scanHeaders"
          :items="recentScans"
          :items-per-page="5"
          class="elevation-1"
        >
          <!-- Resource Column -->
          <template v-slot:item.resource="{ item }">
            <router-link
              :to="getResourceLink(item)"
              class="text-decoration-none"
            >
              {{ item.resource_name }}
            </router-link>
            <v-chip
              x-small
              class="ml-2"
              :color="getResourceTypeColor(item.resource_type)"
            >
              {{ item.resource_type }}
            </v-chip>
          </template>

          <!-- Status Column -->
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getScanStatusColor(item.status)"
              text-color="white"
              small
            >
              {{ item.status }}
            </v-chip>
          </template>

          <!-- Findings Column -->
          <template v-slot:item.findings="{ item }">
            <v-chip
              v-if="item.critical_count > 0"
              color="error"
              x-small
              class="mr-1"
            >
              {{ item.critical_count }} Critical
            </v-chip>
            <v-chip
              v-if="item.high_count > 0"
              color="warning"
              x-small
              class="mr-1"
            >
              {{ item.high_count }} High
            </v-chip>
            <v-chip
              v-if="item.medium_count > 0"
              color="info"
              x-small
              class="mr-1"
            >
              {{ item.medium_count }} Medium
            </v-chip>
            <span v-if="item.critical_count === 0 && item.high_count === 0 && item.medium_count === 0">
              No significant findings
            </span>
          </template>

          <!-- Date Column -->
          <template v-slot:item.scan_date="{ item }">
            {{ formatDate(item.scan_date) }}
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              :to="getScanDetailsLink(item)"
              title="View Details"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="runNewScan(item)"
              title="Run New Scan"
              :disabled="item.status === 'in-progress'"
            >
              <v-icon small>mdi-refresh</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="resolveWithAI(item)"
              title="Resolve with AI"
              :disabled="item.status === 'in-progress' || item.critical_count === 0 && item.high_count === 0"
              color="primary"
            >
              <v-icon small>mdi-robot</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- Security Recommendations -->
      <h2 class="text-h5 mb-3">Security Recommendations</h2>
      <v-row>
        <v-col cols="12">
          <v-expansion-panels>
            <v-expansion-panel
              v-for="(recommendation, i) in recommendations"
              :key="i"
            >
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon
                    :color="getRecommendationPriorityColor(recommendation.priority)"
                    class="mr-2"
                  >
                    mdi-alert-circle
                  </v-icon>
                  <span>{{ recommendation.title }}</span>
                  <v-chip
                    class="ml-2"
                    x-small
                    :color="getRecommendationPriorityColor(recommendation.priority)"
                    text-color="white"
                  >
                    {{ recommendation.priority }}
                  </v-chip>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <p>{{ recommendation.description }}</p>
                <div v-if="recommendation.affected_resources.length > 0">
                  <strong>Affected Resources:</strong>
                  <ul>
                    <li v-for="(resource, j) in recommendation.affected_resources" :key="j">
                      {{ resource.name }} ({{ resource.type }})
                    </li>
                  </ul>
                </div>
                <div class="d-flex mt-2">
                  <v-btn
                    color="primary"
                    text
                    class="mr-2"
                    @click="applyRecommendation(recommendation)"
                  >
                    Apply Recommendation
                  </v-btn>
                  <v-btn
                    color="info"
                    text
                    @click="resolveRecommendationWithAI(recommendation)"
                  >
                    <v-icon left small>mdi-robot</v-icon>
                    Resolve with AI
                  </v-btn>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import axios from 'axios';

export default {
  name: 'SecurityDashboard',
  data() {
    return {
      loading: true,
      error: null,
      securityScore: 0,
      vulnerabilityCounts: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      complianceStats: {
        passed: 0,
        failed: 0,
      },
      scanHeaders: [
        { text: 'Resource', value: 'resource', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Findings', value: 'findings', sortable: false },
        { text: 'Scan Date', value: 'scan_date', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      recentScans: [],
      recommendations: [],
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchSecurityData();
  },
  methods: {
    ...mapActions({
      setActive: 'chat/SET_ACTIVE',
      updateContext: 'chat/updateContext'
    }),
    async fetchSecurityData() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/security/dashboard', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.securityScore = response.data.security_score;
        // this.vulnerabilityCounts = response.data.vulnerability_counts;
        // this.complianceStats = response.data.compliance_stats;
        // this.recentScans = response.data.recent_scans;
        // this.recommendations = response.data.recommendations;
        
        // Mock data for development
        setTimeout(() => {
          this.securityScore = 78;
          
          this.vulnerabilityCounts = {
            critical: 2,
            high: 5,
            medium: 12,
            low: 23,
          };
          
          this.complianceStats = {
            passed: 42,
            failed: 8,
          };
          
          this.recentScans = [
            {
              id: 's1',
              resource_type: 'image',
              resource_id: 'i1',
              resource_name: 'nginx:latest',
              status: 'completed',
              critical_count: 0,
              high_count: 2,
              medium_count: 5,
              scan_date: '2025-03-16T10:00:00Z',
            },
            {
              id: 's2',
              resource_type: 'image',
              resource_id: 'i2',
              resource_name: 'postgres:13',
              status: 'completed',
              critical_count: 1,
              high_count: 3,
              medium_count: 7,
              scan_date: '2025-03-16T09:30:00Z',
            },
            {
              id: 's3',
              resource_type: 'container',
              resource_id: 'c1',
              resource_name: 'web-server',
              status: 'completed',
              critical_count: 0,
              high_count: 0,
              medium_count: 0,
              scan_date: '2025-03-16T09:00:00Z',
            },
            {
              id: 's4',
              resource_type: 'image',
              resource_id: 'i3',
              resource_name: 'node:14-alpine',
              status: 'in-progress',
              critical_count: 0,
              high_count: 0,
              medium_count: 0,
              scan_date: '2025-03-16T08:45:00Z',
            },
            {
              id: 's5',
              resource_type: 'container',
              resource_id: 'c3',
              resource_name: 'database',
              status: 'failed',
              critical_count: 0,
              high_count: 0,
              medium_count: 0,
              scan_date: '2025-03-16T08:30:00Z',
            },
          ];
          
          this.recommendations = [
            {
              id: 'r1',
              title: 'Update nginx image to fix critical vulnerabilities',
              description: 'The current nginx image has 2 critical vulnerabilities that can be fixed by updating to the latest version.',
              priority: 'high',
              affected_resources: [
                { name: 'nginx:latest', type: 'image' },
                { name: 'web-server', type: 'container' },
              ],
            },
            {
              id: 'r2',
              title: 'Enable user namespace remapping',
              description: 'User namespace remapping provides an additional layer of security by mapping container user IDs to a different range on the host.',
              priority: 'medium',
              affected_resources: [],
            },
            {
              id: 'r3',
              title: 'Apply security policy to restrict privileged containers',
              description: 'Privileged containers have access to all host devices and can pose a security risk. Apply a security policy to restrict their usage.',
              priority: 'high',
              affected_resources: [
                { name: 'database', type: 'container' },
              ],
            },
            {
              id: 'r4',
              title: 'Configure network policies to restrict container communication',
              description: 'Implement network policies to restrict communication between containers and limit exposure to potential attacks.',
              priority: 'medium',
              affected_resources: [],
            },
            {
              id: 'r5',
              title: 'Enable content trust for image verification',
              description: 'Content trust ensures that the images you pull are signed and verified, reducing the risk of using compromised images.',
              priority: 'medium',
              affected_resources: [],
            },
          ];
          
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load security data. Please try again.';
        this.loading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getSecurityScoreColor(score) {
      if (score >= 90) {
        return 'success';
      } else if (score >= 70) {
        return 'warning';
      } else {
        return 'error';
      }
    },
    getSecurityScoreLabel(score) {
      if (score >= 90) {
        return 'Good';
      } else if (score >= 70) {
        return 'Needs Improvement';
      } else {
        return 'At Risk';
      }
    },
    getScanStatusColor(status) {
      switch (status) {
        case 'completed':
          return 'success';
        case 'in-progress':
          return 'info';
        case 'failed':
          return 'error';
        default:
          return 'grey';
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
    getRecommendationPriorityColor(priority) {
      switch (priority) {
        case 'critical':
          return 'error';
        case 'high':
          return 'deep-orange';
        case 'medium':
          return 'warning';
        case 'low':
          return 'info';
        default:
          return 'grey';
      }
    },
    getResourceLink(scan) {
      switch (scan.resource_type) {
        case 'image':
          return `/images/${scan.resource_id}`;
        case 'container':
          return `/containers/${scan.resource_id}`;
        case 'volume':
          return `/volumes/${scan.resource_id}`;
        case 'network':
          return `/networks/${scan.resource_id}`;
        default:
          return '#';
      }
    },
    getScanDetailsLink(scan) {
      if (scan.resource_type === 'image') {
        return `/images/${scan.resource_id}/security/${scan.id}`;
      }
      return `/security/scans/${scan.id}`;
    },
    runNewScan(scan) {
      // In a real implementation, this would call the API to start a new scan
      // await axios.post(`/api/security/scan`, {
      //   resource_type: scan.resource_type,
      //   resource_id: scan.resource_id,
      // }, {
      //   headers: { Authorization: `Bearer ${this.token}` },
      // });
      
      // Mock implementation
      this.$set(scan, 'status', 'in-progress');
      this.$set(scan, 'scan_date', new Date().toISOString());
      
      // Simulate scan completion after 3 seconds
      setTimeout(() => {
        this.$set(scan, 'status', 'completed');
      }, 3000);
    },
    async resolveWithAI(scan) {
      try {
        // Start a security workflow for the vulnerability
        const response = await axios.post(`/api/chat/security/start-workflow?vulnerability_id=${scan.id}`);
        
        // Set context data for chat
        this.updateContext({
          currentPage: 'security',
          currentContainerId: scan.resource_type === 'container' ? scan.resource_id : null,
          currentImageId: scan.resource_type === 'image' ? scan.resource_id : null,
          vulnerability_id: scan.id,
          workflow_id: response.data.message.context?.workflow_id
        });
        
        // Open chat sidebar
        this.setActive(true);
        
        // Show notification
        this.$emit('show-notification', {
          type: 'info',
          message: 'AI-assisted resolution workflow started. Check the chat sidebar.',
        });
      } catch (error) {
        console.error('Error starting security workflow:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to start AI resolution workflow.',
        });
      }
    },
    
    async resolveRecommendationWithAI(recommendation) {
      try {
        // Start a security workflow for the recommendation
        const response = await axios.post(`/api/chat/security/start-workflow?vulnerability_id=${recommendation.id}`);
        
        // Prepare context with recommendation data
        this.updateContext({
          currentPage: 'security',
          recommendation_id: recommendation.id,
          workflow_id: response.data.message.context?.workflow_id
        });
        
        // Open chat sidebar
        this.setActive(true);
        
        // Show notification
        this.$emit('show-notification', {
          type: 'info',
          message: 'AI-assisted resolution workflow started. Check the chat sidebar.',
        });
      } catch (error) {
        console.error('Error starting recommendation workflow:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to start AI resolution workflow.',
        });
      }
    },
    
    applyRecommendation(recommendation) {
      // In a real implementation, this would call the API to apply the recommendation
      // await axios.post(`/api/security/recommendations/${recommendation.id}/apply`, {}, {
      //   headers: { Authorization: `Bearer ${this.token}` },
      // });
      
      // Mock implementation - just show a notification
      this.$emit('show-notification', {
        type: 'success',
        message: `Applied recommendation: ${recommendation.title}`,
      });
      
      // Remove the recommendation from the list
      this.recommendations = this.recommendations.filter(r => r.id !== recommendation.id);
      
      // Update security score
      this.securityScore += 5;
      if (this.securityScore > 100) {
        this.securityScore = 100;
      }
    },
  },
};
</script>

<style scoped>
.security-dashboard {
  padding: 16px;
}
</style>
