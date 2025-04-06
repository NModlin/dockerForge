<template>
  <div class="scan-results">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-shield-search</v-icon>
              Scan Results
              <v-spacer></v-spacer>
              <v-btn color="primary" :to="{ name: 'SecurityScan' }">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Scans
              </v-btn>
            </v-card-title>

            <v-card-text v-if="loading">
              <v-skeleton-loader type="article" />
            </v-card-text>

            <v-card-text v-else-if="!currentScan">
              <v-alert type="error">Scan not found</v-alert>
            </v-card-text>

            <template v-else>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>{{ currentScan.scan_type === 'IMAGE' ? 'mdi-image' : 'mdi-docker' }}</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Target</v-list-item-title>
                        <v-list-item-subtitle>{{ currentScan.target }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>mdi-calendar</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Scan Date</v-list-item-title>
                        <v-list-item-subtitle>{{ formatDate(currentScan.started_at) }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>mdi-timer</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Duration</v-list-item-title>
                        <v-list-item-subtitle>{{ formatDuration(currentScan.duration_seconds) }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>mdi-shield</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Status</v-list-item-title>
                        <v-list-item-subtitle>
                          <v-chip
                            :color="getStatusColor(currentScan.status)"
                            text-color="white"
                            small
                          >
                            {{ currentScan.status }}
                          </v-chip>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>mdi-bug</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Vulnerabilities</v-list-item-title>
                        <v-list-item-subtitle>
                          <v-chip
                            v-if="currentScan.vulnerability_counts.CRITICAL > 0"
                            color="red"
                            text-color="white"
                            small
                            class="mr-1"
                          >
                            {{ currentScan.vulnerability_counts.CRITICAL }} Critical
                          </v-chip>
                          <v-chip
                            v-if="currentScan.vulnerability_counts.HIGH > 0"
                            color="orange"
                            text-color="white"
                            small
                            class="mr-1"
                          >
                            {{ currentScan.vulnerability_counts.HIGH }} High
                          </v-chip>
                          <v-chip
                            v-if="currentScan.vulnerability_counts.MEDIUM > 0"
                            color="amber"
                            text-color="white"
                            small
                            class="mr-1"
                          >
                            {{ currentScan.vulnerability_counts.MEDIUM }} Medium
                          </v-chip>
                          <v-chip
                            v-if="currentScan.vulnerability_counts.LOW > 0"
                            color="blue"
                            text-color="white"
                            small
                            class="mr-1"
                          >
                            {{ currentScan.vulnerability_counts.LOW }} Low
                          </v-chip>
                          <span v-if="currentScan.total_vulnerabilities === 0" class="success--text">
                            No vulnerabilities found
                          </span>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon>mdi-scanner</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>Scanner</v-list-item-title>
                        <v-list-item-subtitle>{{ currentScan.scanner_name }} {{ currentScan.scanner_version || '' }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-col>
                </v-row>

                <v-divider class="my-4"></v-divider>

                <div v-if="currentScan.status === 'COMPLETED'">
                  <div v-if="currentScan.total_vulnerabilities === 0" class="text-center my-8">
                    <v-icon color="success" size="64">mdi-shield-check</v-icon>
                    <h3 class="text-h5 success--text mt-4">No vulnerabilities found</h3>
                    <p class="text-body-1 mt-2">The scan completed successfully and did not find any vulnerabilities.</p>
                  </div>

                  <div v-else>
                    <h3 class="text-h5 mb-4">Vulnerabilities</h3>

                    <v-row>
                      <v-col cols="12" md="3">
                        <v-card outlined>
                          <v-card-text class="text-center">
                            <v-icon color="red" size="36">mdi-alert-circle</v-icon>
                            <div class="text-h5 red--text">{{ currentScan.vulnerability_counts.CRITICAL }}</div>
                            <div class="text-subtitle-1">Critical</div>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="3">
                        <v-card outlined>
                          <v-card-text class="text-center">
                            <v-icon color="orange" size="36">mdi-alert</v-icon>
                            <div class="text-h5 orange--text">{{ currentScan.vulnerability_counts.HIGH }}</div>
                            <div class="text-subtitle-1">High</div>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="3">
                        <v-card outlined>
                          <v-card-text class="text-center">
                            <v-icon color="amber" size="36">mdi-alert-outline</v-icon>
                            <div class="text-h5 amber--text">{{ currentScan.vulnerability_counts.MEDIUM }}</div>
                            <div class="text-subtitle-1">Medium</div>
                          </v-card-text>
                        </v-card>
                      </v-col>

                      <v-col cols="12" md="3">
                        <v-card outlined>
                          <v-card-text class="text-center">
                            <v-icon color="blue" size="36">mdi-information</v-icon>
                            <div class="text-h5 blue--text">{{ currentScan.vulnerability_counts.LOW }}</div>
                            <div class="text-subtitle-1">Low</div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>

                    <v-card outlined class="mt-4">
                      <v-card-title>
                        <v-text-field
                          v-model="search"
                          append-icon="mdi-magnify"
                          label="Search vulnerabilities"
                          single-line
                          hide-details
                          clearable
                        ></v-text-field>

                        <v-spacer></v-spacer>

                        <v-select
                          v-model="severityFilter"
                          :items="severityLevels"
                          label="Severity"
                          multiple
                          chips
                          small-chips
                          dense
                          hide-details
                          class="ml-4"
                          style="max-width: 300px;"
                        ></v-select>
                      </v-card-title>

                      <v-data-table
                        :headers="vulnerabilityHeaders"
                        :items="filteredVulnerabilities"
                        :search="search"
                        :items-per-page="10"
                        :footer-props="{
                          'items-per-page-options': [5, 10, 25, 50],
                        }"
                        class="elevation-0"
                      >
                        <!-- Severity column -->
                        <template v-slot:item.severity="{ item }">
                          <v-chip
                            :color="getSeverityColor(item.severity)"
                            text-color="white"
                            small
                          >
                            {{ item.severity }}
                          </v-chip>
                        </template>

                        <!-- Fixed column -->
                        <template v-slot:item.is_fixed="{ item }">
                          <v-icon v-if="item.is_fixed" color="success">mdi-check</v-icon>
                          <v-icon v-else color="error">mdi-close</v-icon>
                        </template>

                        <!-- Actions column -->
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            icon
                            small
                            color="primary"
                            @click="showVulnerabilityDetails(item)"
                            title="View Details"
                          >
                            <v-icon>mdi-eye</v-icon>
                          </v-btn>
                          <v-btn
                            icon
                            small
                            color="success"
                            @click="showRemediationPlan(item)"
                            title="Show Remediation Plan"
                          >
                            <v-icon>mdi-wrench</v-icon>
                          </v-btn>
                          <v-btn
                            icon
                            small
                            color="info"
                            @click="resolveWithAI(item)"
                            title="Resolve with AI"
                          >
                            <v-icon>mdi-robot</v-icon>
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card>
                  </div>
                </div>

                <div v-else-if="currentScan.status === 'FAILED'" class="text-center my-8">
                  <v-icon color="error" size="64">mdi-alert-circle</v-icon>
                  <h3 class="text-h5 error--text mt-4">Scan Failed</h3>
                  <p class="text-body-1 mt-2">{{ currentScan.error_message || 'The scan failed to complete. Please try again.' }}</p>
                </div>

                <div v-else class="text-center my-8">
                  <v-progress-circular
                    indeterminate
                    color="primary"
                    size="64"
                  ></v-progress-circular>
                  <h3 class="text-h5 primary--text mt-4">Scan in Progress</h3>
                  <p class="text-body-1 mt-2">Please wait while the scan is being performed...</p>
                </div>
              </v-card-text>
            </template>
          </v-card>
        </v-col>
      </v-row>

      <!-- Vulnerability Details Dialog -->
      <v-dialog v-model="detailsDialog" max-width="800">
        <v-card>
          <v-card-title class="headline">
            <v-icon left :color="getSeverityColor(selectedVulnerability?.severity)">mdi-alert</v-icon>
            {{ selectedVulnerability?.vulnerability_id || 'Vulnerability Details' }}
          </v-card-title>

          <v-card-text v-if="selectedVulnerability">
            <v-chip
              :color="getSeverityColor(selectedVulnerability.severity)"
              text-color="white"
              class="mb-4"
            >
              {{ selectedVulnerability.severity }} Severity
            </v-chip>

            <h3 class="text-h6 mb-2">{{ selectedVulnerability.title }}</h3>

            <p class="text-body-1 mb-4">{{ selectedVulnerability.description }}</p>

            <!-- Enhanced vulnerability details display -->
            <v-expansion-panels class="mb-4">
              <v-expansion-panel>
                <v-expansion-panel-header>
                  <v-icon left>mdi-information-outline</v-icon>
                  Detailed Information
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-simple-table dense>
                    <tbody>
                      <tr v-if="selectedVulnerability.vulnerability_type">
                        <td class="font-weight-bold">Type</td>
                        <td>{{ selectedVulnerability.vulnerability_type }}</td>
                      </tr>
                      <tr v-if="selectedVulnerability.published_date">
                        <td class="font-weight-bold">Published</td>
                        <td>{{ formatDate(selectedVulnerability.published_date) }}</td>
                      </tr>
                      <tr v-if="selectedVulnerability.last_modified_date">
                        <td class="font-weight-bold">Last Modified</td>
                        <td>{{ formatDate(selectedVulnerability.last_modified_date) }}</td>
                      </tr>
                      <tr v-if="selectedVulnerability.affected_versions">
                        <td class="font-weight-bold">Affected Versions</td>
                        <td>{{ selectedVulnerability.affected_versions }}</td>
                      </tr>
                      <tr v-if="selectedVulnerability.attack_vector">
                        <td class="font-weight-bold">Attack Vector</td>
                        <td>{{ selectedVulnerability.attack_vector }}</td>
                      </tr>
                    </tbody>
                  </v-simple-table>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>

            <v-simple-table dense>
              <template v-slot:default>
                <tbody>
                  <tr>
                    <td class="font-weight-bold">Package</td>
                    <td>{{ selectedVulnerability.package_name }}</td>
                  </tr>
                  <tr>
                    <td class="font-weight-bold">Installed Version</td>
                    <td>{{ selectedVulnerability.installed_version }}</td>
                  </tr>
                  <tr>
                    <td class="font-weight-bold">Fixed Version</td>
                    <td>{{ selectedVulnerability.fixed_version || 'Not available' }}</td>
                  </tr>
                  <tr v-if="selectedVulnerability.cve_id">
                    <td class="font-weight-bold">CVE ID</td>
                    <td>
                      <a :href="`https://nvd.nist.gov/vuln/detail/${selectedVulnerability.cve_id}`" target="_blank">
                        {{ selectedVulnerability.cve_id }}
                        <v-icon small>mdi-open-in-new</v-icon>
                      </a>
                    </td>
                  </tr>
                  <tr v-if="selectedVulnerability.cvss_score">
                    <td class="font-weight-bold">CVSS Score</td>
                    <td>
                      <v-chip
                        :color="getCvssColor(selectedVulnerability.cvss_score)"
                        text-color="white"
                        small
                      >
                        {{ selectedVulnerability.cvss_score }}
                      </v-chip>
                    </td>
                  </tr>
                  <tr v-if="selectedVulnerability.cvss_vector">
                    <td class="font-weight-bold">CVSS Vector</td>
                    <td>{{ selectedVulnerability.cvss_vector }}</td>
                  </tr>
                  <!-- Add additional CVE information links -->
                  <tr v-if="selectedVulnerability.cve_id">
                    <td class="font-weight-bold">External References</td>
                    <td>
                      <div class="d-flex flex-column">
                        <a :href="`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${selectedVulnerability.cve_id}`" target="_blank" class="mb-1">
                          <v-icon small class="mr-1">mdi-link</v-icon>MITRE
                        </a>
                        <a :href="`https://www.cvedetails.com/cve/${selectedVulnerability.cve_id}`" target="_blank" class="mb-1">
                          <v-icon small class="mr-1">mdi-link</v-icon>CVE Details
                        </a>
                        <a :href="`https://vuldb.com/?id.${selectedVulnerability.cve_id}`" target="_blank" class="mb-1">
                          <v-icon small class="mr-1">mdi-link</v-icon>VulDB
                        </a>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>

            <div v-if="selectedVulnerability.references && selectedVulnerability.references.length > 0" class="mt-4">
              <h4 class="text-subtitle-1 mb-2">References</h4>
              <v-list dense>
                <v-list-item v-for="(ref, index) in selectedVulnerability.references" :key="index" :href="ref" target="_blank">
                  <v-list-item-icon>
                    <v-icon small>mdi-link</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title class="text-caption">{{ ref }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="success"
              text
              @click="showRemediationPlan(selectedVulnerability)"
            >
              <v-icon left>mdi-wrench</v-icon>
              Show Remediation
            </v-btn>
            <v-btn
              color="info"
              text
              @click="resolveWithAI(selectedVulnerability)"
            >
              <v-icon left>mdi-robot</v-icon>
              Resolve with AI
            </v-btn>
            <v-btn
              color="grey darken-1"
              text
              @click="detailsDialog = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Remediation Plan Dialog -->
      <v-dialog v-model="remediationDialog" max-width="800">
        <v-card>
          <v-card-title class="headline">
            <v-icon left>mdi-wrench</v-icon>
            Remediation Plan
          </v-card-title>

          <v-card-text v-if="loading">
            <v-skeleton-loader type="article" />
          </v-card-text>

          <v-card-text v-else-if="!remediationPlan">
            <v-alert type="error">Failed to load remediation plan</v-alert>
          </v-card-text>

          <v-card-text v-else>
            <h3 class="text-h6 mb-2">{{ selectedVulnerability?.title || 'Vulnerability' }}</h3>
            <p class="text-body-2 mb-4">{{ selectedVulnerability?.vulnerability_id || '' }}</p>

            <v-alert type="info" class="mb-4">
              {{ remediationPlan.notes || 'The following steps are recommended to remediate this vulnerability.' }}
            </v-alert>

            <v-timeline dense>
              <v-timeline-item
                v-for="(step, index) in remediationPlan.steps"
                :key="index"
                :color="getActionColor(step.action)"
                small
              >
                <div class="font-weight-bold">{{ getActionLabel(step.action) }}</div>
                <div class="text-body-2">{{ step.description }}</div>

                <v-card v-if="step.command" outlined class="mt-2">
                  <v-card-text class="pa-2">
                    <pre class="code-block">{{ step.command }}</pre>
                  </v-card-text>
                </v-card>

                <div class="mt-2 text-caption">
                  <v-chip x-small :color="getDifficultyColor(step.difficulty)" text-color="white">
                    {{ step.difficulty }} Difficulty
                  </v-chip>
                  <span v-if="step.estimated_time" class="ml-2">
                    <v-icon x-small>mdi-clock-outline</v-icon>
                    {{ step.estimated_time }}
                  </span>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="info"
              text
              @click="resolveWithAI(selectedVulnerability)"
            >
              <v-icon left>mdi-robot</v-icon>
              Resolve with AI
            </v-btn>
            <v-btn
              color="grey darken-1"
              text
              @click="remediationDialog = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import { format, parseISO } from 'date-fns';
import axios from 'axios';

export default {
  name: 'ScanResults',
  data() {
    return {
      search: '',
      severityFilter: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'],
      severityLevels: [
        { text: 'Critical', value: 'CRITICAL' },
        { text: 'High', value: 'HIGH' },
        { text: 'Medium', value: 'MEDIUM' },
        { text: 'Low', value: 'LOW' },
        { text: 'Unknown', value: 'UNKNOWN' }
      ],
      vulnerabilityHeaders: [
        { text: 'ID', value: 'vulnerability_id', sortable: true },
        { text: 'Severity', value: 'severity', sortable: true },
        { text: 'Package', value: 'package_name', sortable: true },
        { text: 'Installed Version', value: 'installed_version', sortable: true },
        { text: 'Fixed Version', value: 'fixed_version', sortable: true },
        { text: 'Fixed', value: 'is_fixed', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      detailsDialog: false,
      remediationDialog: false,
      selectedVulnerability: null,
      pollingInterval: null
    };
  },
  computed: {
    ...mapState({
      loading: state => state.security.loading,
      error: state => state.security.error,
      currentScan: state => state.security.currentScan,
      remediationPlan: state => state.security.remediationPlan
    }),
    scanId() {
      return this.$route.params.id;
    },
    filteredVulnerabilities() {
      if (!this.currentScan || !this.currentScan.vulnerabilities) {
        return [];
      }

      return this.currentScan.vulnerabilities.filter(vuln =>
        this.severityFilter.includes(vuln.severity)
      );
    }
  },
  created() {
    this.fetchScan(this.scanId);

    // Set up polling for in-progress scans
    if (this.currentScan && (this.currentScan.status === 'PENDING' || this.currentScan.status === 'IN_PROGRESS')) {
      this.pollingInterval = setInterval(() => {
        this.fetchScan(this.scanId);
      }, 5000);
    }
  },
  beforeUnmount() {
    // Clear polling interval when component is destroyed
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  watch: {
    'currentScan.status'(newStatus, oldStatus) {
      // Start or stop polling based on scan status
      if (newStatus === 'COMPLETED' || newStatus === 'FAILED') {
        if (this.pollingInterval) {
          clearInterval(this.pollingInterval);
          this.pollingInterval = null;
        }
      } else if ((newStatus === 'PENDING' || newStatus === 'IN_PROGRESS') && !this.pollingInterval) {
        this.pollingInterval = setInterval(() => {
          this.fetchScan(this.scanId);
        }, 5000);
      }
    }
  },
  methods: {
    ...mapActions({
      fetchScan: 'security/fetchScan',
      getRemediationPlan: 'security/getRemediationPlan'
    }),
    ...mapActions({
      updateContext: 'chat/updateContext',
      setActive: 'chat/SET_ACTIVE'
    }),

    getStatusColor(status) {
      switch (status) {
        case 'COMPLETED': return 'success';
        case 'IN_PROGRESS': return 'primary';
        case 'PENDING': return 'info';
        case 'FAILED': return 'error';
        default: return 'grey';
      }
    },

    getSeverityColor(severity) {
      switch (severity) {
        case 'CRITICAL': return 'red';
        case 'HIGH': return 'orange';
        case 'MEDIUM': return 'amber';
        case 'LOW': return 'blue';
        default: return 'grey';
      }
    },

    getCvssColor(score) {
      if (!score) return 'grey';

      // CVSS v3 scoring
      if (score >= 9.0) return 'red darken-4';
      if (score >= 7.0) return 'red';
      if (score >= 4.0) return 'orange';
      if (score >= 0.1) return 'blue';
      return 'grey';
    },

    getActionColor(action) {
      switch (action) {
        case 'UPDATE_PACKAGE': return 'green';
        case 'REBUILD_IMAGE': return 'blue';
        case 'REPLACE_BASE_IMAGE': return 'purple';
        case 'IGNORE_VULNERABILITY': return 'grey';
        default: return 'primary';
      }
    },

    getActionLabel(action) {
      switch (action) {
        case 'UPDATE_PACKAGE': return 'Update Package';
        case 'REBUILD_IMAGE': return 'Rebuild Image';
        case 'REPLACE_BASE_IMAGE': return 'Replace Base Image';
        case 'IGNORE_VULNERABILITY': return 'Ignore Vulnerability';
        default: return action;
      }
    },

    getDifficultyColor(difficulty) {
      switch (difficulty) {
        case 'EASY': return 'green';
        case 'MEDIUM': return 'amber';
        case 'HARD': return 'red';
        default: return 'grey';
      }
    },

    formatDate(dateString) {
      if (!dateString) return '-';
      try {
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm:ss');
      } catch (error) {
        return dateString;
      }
    },

    formatDuration(seconds) {
      if (!seconds) return '-';

      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;

      if (minutes === 0) {
        return `${remainingSeconds}s`;
      } else {
        return `${minutes}m ${remainingSeconds}s`;
      }
    },

    showVulnerabilityDetails(vulnerability) {
      this.selectedVulnerability = vulnerability;
      this.detailsDialog = true;
    },

    async showRemediationPlan(vulnerability) {
      this.selectedVulnerability = vulnerability;

      try {
        await this.getRemediationPlan({
          scanId: this.scanId,
          vulnerabilityId: vulnerability.vulnerability_id
        });
        this.remediationDialog = true;
      } catch (error) {
        console.error('Error getting remediation plan:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to get remediation plan: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
      }
    },

    async resolveWithAI(vulnerability) {
      try {
        // Start a security workflow for the vulnerability
        const response = await axios.post(`/api/chat/security/start-workflow?vulnerability_id=${vulnerability.vulnerability_id}`);

        // Set context data for chat
        this.updateContext({
          currentPage: 'security',
          currentScanId: this.scanId,
          vulnerability_id: vulnerability.vulnerability_id,
          vulnerability_severity: vulnerability.severity,
          vulnerability_description: vulnerability.description,
          affected_package: vulnerability.package_name,
          current_version: vulnerability.installed_version,
          fixed_version: vulnerability.fixed_version,
          cve_id: vulnerability.cve_id,
          workflow_id: response.data.message?.context?.workflow_id
        });

        // Open chat sidebar
        this.setActive(true);

        // Close the dialogs
        this.detailsDialog = false;
        this.remediationDialog = false;

        // Show success notification
        this.$store.dispatch('showSnackbar', {
          text: 'AI-assisted resolution workflow started. Check the chat sidebar.',
          color: 'info'
        });
      } catch (error) {
        console.error('Error starting security workflow:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to start AI resolution workflow: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
      }
    }
  }
};
</script>

<style scoped>
.scan-results {
  height: 100%;
}

.code-block {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>
