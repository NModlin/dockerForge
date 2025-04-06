<template>
  <div class="compliance-report">
    <v-container fluid>
      <!-- Report Generation Form -->
      <v-card v-if="!reportId" class="mb-4">
        <v-card-title class="headline">
          <v-icon left>mdi-file-document</v-icon>
          Generate Compliance Report
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="reportForm.name"
                  label="Report Name"
                  required
                  :rules="[v => !!v || 'Report name is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="reportForm.format"
                  label="Report Format"
                  :items="reportFormats"
                  required
                  :rules="[v => !!v || 'Report format is required']"
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="reportForm.resourceTypes"
                  label="Resource Types"
                  :items="resourceTypeOptions"
                  multiple
                  chips
                  required
                  :rules="[v => v.length > 0 || 'At least one resource type is required']"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="reportForm.severityLevels"
                  label="Severity Levels"
                  :items="severityLevelOptions"
                  multiple
                  chips
                  required
                  :rules="[v => v.length > 0 || 'At least one severity level is required']"
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="reportForm.policyIds"
                  label="Policies"
                  :items="policyOptions"
                  item-text="text"
                  item-value="value"
                  multiple
                  chips
                  hint="Leave empty to include all policies"
                  persistent-hint
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-checkbox
                  v-model="reportForm.includeRemediation"
                  label="Include Remediation Steps"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            :disabled="!formValid || complianceLoading"
            :loading="complianceLoading"
            @click="generateReport"
          >
            <v-icon left>mdi-file-document-outline</v-icon>
            Generate Report
          </v-btn>
        </v-card-actions>
      </v-card>

      <!-- Report List -->
      <v-card v-if="!reportId" class="mb-4">
        <v-card-title class="headline">
          <v-icon left>mdi-file-document-multiple</v-icon>
          Compliance Reports
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
          :headers="reportHeaders"
          :items="complianceReports"
          :search="search"
          :loading="complianceLoading"
          :items-per-page="10"
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
            <v-btn
              icon
              small
              @click="confirmDeleteReport(item)"
              title="Delete Report"
              color="grey"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>

          <!-- No Data Template -->
          <template v-slot:no-data>
            <div class="text-center pa-4">
              <p>No compliance reports found.</p>
              <p class="text-caption">Generate a new report using the form above.</p>
            </div>
          </template>
        </v-data-table>
      </v-card>

      <!-- Report Detail View -->
      <div v-if="reportId && currentReport">
        <div class="d-flex align-center mb-4">
          <h1 class="text-h4">
            <v-icon large left>mdi-file-document</v-icon>
            {{ currentReport.name }}
          </h1>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            class="mr-2"
            :to="{ name: 'ComplianceReports' }"
          >
            <v-icon left>mdi-arrow-left</v-icon>
            Back to Reports
          </v-btn>
          <v-btn
            color="error"
            class="mr-2"
            @click="exportReport(reportId, 'PDF')"
          >
            <v-icon left>mdi-file-pdf-box</v-icon>
            Export as PDF
          </v-btn>
          <v-btn
            color="success"
            @click="exportReport(reportId, 'CSV')"
          >
            <v-icon left>mdi-file-excel</v-icon>
            Export as CSV
          </v-btn>
        </div>

        <!-- Report Overview -->
        <v-card class="mb-4">
          <v-card-title class="headline">
            Report Overview
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-text class="text-center">
                    <div class="text-h6">Compliance Score</div>
                    <v-progress-circular
                      :rotate="-90"
                      :size="100"
                      :width="15"
                      :value="currentReport.compliance_score"
                      :color="getComplianceScoreColor(currentReport.compliance_score)"
                    >
                      <span class="text-h5">{{ currentReport.compliance_score }}%</span>
                    </v-progress-circular>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h6">Report Details</div>
                    <v-list-item two-line>
                      <v-list-item-content>
                        <v-list-item-title>Generated</v-list-item-title>
                        <v-list-item-subtitle>{{ formatDate(currentReport.generated_at) }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item two-line>
                      <v-list-item-content>
                        <v-list-item-title>Format</v-list-item-title>
                        <v-list-item-subtitle>{{ currentReport.format }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-text>
                    <div class="text-h6">Compliance Summary</div>
                    <v-list-item two-line>
                      <v-list-item-content>
                        <v-list-item-title>Compliant Policies</v-list-item-title>
                        <v-list-item-subtitle>
                          <v-chip color="success" text-color="white" small>
                            {{ currentReport.compliant_policies }} / {{ currentReport.total_policies }}
                          </v-chip>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item two-line>
                      <v-list-item-content>
                        <v-list-item-title>Compliant Resources</v-list-item-title>
                        <v-list-item-subtitle>
                          <v-chip color="success" text-color="white" small>
                            {{ currentReport.compliant_resources }} / {{ currentReport.total_resources }}
                          </v-chip>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Policy Compliance -->
        <v-card class="mb-4">
          <v-card-title class="headline">
            Policy Compliance
          </v-card-title>
          <v-data-table
            :headers="policyHeaders"
            :items="currentReport.policy_results"
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

            <!-- Status Column -->
            <template v-slot:item.compliant="{ item }">
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
          </v-data-table>
        </v-card>

        <!-- Resource Compliance -->
        <v-card class="mb-4">
          <v-card-title class="headline">
            Resource Compliance
          </v-card-title>
          <v-data-table
            :headers="resourceHeaders"
            :items="currentReport.resource_results"
            :items-per-page="10"
            class="elevation-1"
          >
            <!-- Resource Name Column -->
            <template v-slot:item.resource_name="{ item }">
              <router-link
                :to="getResourceRoute(item)"
                class="text-decoration-none"
              >
                {{ item.resource_name }}
              </router-link>
            </template>

            <!-- Resource Type Column -->
            <template v-slot:item.resource_type="{ item }">
              <v-chip small>
                {{ item.resource_type }}
              </v-chip>
            </template>

            <!-- Status Column -->
            <template v-slot:item.compliant="{ item }">
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
          </v-data-table>
        </v-card>

        <!-- Remediation Steps -->
        <v-card v-if="currentReport.remediation_steps && currentReport.remediation_steps.length > 0" class="mb-4">
          <v-card-title class="headline">
            Remediation Steps
          </v-card-title>
          <v-expansion-panels>
            <v-expansion-panel
              v-for="(step, index) in currentReport.remediation_steps"
              :key="index"
            >
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-chip
                    :color="getSeverityColor(step.severity)"
                    text-color="white"
                    small
                    class="mr-2"
                  >
                    {{ step.severity }}
                  </v-chip>
                  {{ step.title }}
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div class="mb-2">{{ step.description }}</div>
                <v-card outlined class="pa-2 mb-2">
                  <pre class="ma-0">{{ step.command }}</pre>
                </v-card>
                <div v-if="step.additional_info" class="text-caption">
                  {{ step.additional_info }}
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card>
      </div>

      <!-- Loading State -->
      <div v-else-if="reportId && complianceLoading" class="text-center pa-4">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4">Loading report...</div>
      </div>

      <!-- Error State -->
      <v-alert
        v-if="complianceError"
        type="error"
        dismissible
        class="mt-4"
      >
        {{ complianceError }}
      </v-alert>
    </v-container>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Report</v-card-title>
        <v-card-text>
          Are you sure you want to delete the report "{{ reportToDelete ? reportToDelete.name : '' }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteReport">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { format, parseISO } from 'date-fns';

export default {
  name: 'ComplianceReport',
  
  props: {
    reportId: {
      type: String,
      default: null
    }
  },
  
  data() {
    return {
      formValid: false,
      search: '',
      deleteDialog: false,
      reportToDelete: null,
      reportForm: {
        name: '',
        format: 'PDF',
        resourceTypes: ['image', 'container', 'volume', 'network'],
        severityLevels: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        policyIds: [],
        includeRemediation: true
      },
      reportFormats: ['PDF', 'CSV', 'JSON'],
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
      reportHeaders: [
        { text: 'Report Name', value: 'name', sortable: true },
        { text: 'Generated', value: 'generated_at', sortable: true },
        { text: 'Compliance Score', value: 'compliance_score', sortable: true },
        { text: 'Format', value: 'format', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      policyHeaders: [
        { text: 'Policy Name', value: 'policy_name', sortable: true },
        { text: 'Status', value: 'compliant', sortable: true },
        { text: 'Violations', value: 'violations', sortable: true },
        { text: 'Last Evaluated', value: 'evaluated_at', sortable: true }
      ],
      resourceHeaders: [
        { text: 'Resource Name', value: 'resource_name', sortable: true },
        { text: 'Type', value: 'resource_type', sortable: true },
        { text: 'Status', value: 'compliant', sortable: true },
        { text: 'Violations', value: 'violations', sortable: true }
      ]
    };
  },
  
  computed: {
    ...mapState('security', [
      'complianceLoading',
      'complianceError',
      'complianceReports',
      'currentReport',
      'policies'
    ]),
    
    policyOptions() {
      return this.policies.map(policy => ({
        text: policy.name,
        value: policy.id
      }));
    }
  },
  
  created() {
    this.fetchPolicies();
    this.fetchComplianceReports();
    
    if (this.reportId) {
      this.fetchComplianceReport(this.reportId);
    }
  },
  
  methods: {
    ...mapActions('security', [
      'fetchComplianceReports',
      'fetchComplianceReport',
      'generateComplianceReport',
      'exportComplianceReport',
      'deleteComplianceReport',
      'fetchPolicies'
    ]),
    
    formatDate(dateString) {
      if (!dateString) return '';
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
    
    getSeverityColor(severity) {
      switch (severity.toUpperCase()) {
        case 'CRITICAL':
          return 'deep-purple';
        case 'HIGH':
          return 'error';
        case 'MEDIUM':
          return 'warning';
        case 'LOW':
          return 'info';
        default:
          return 'grey';
      }
    },
    
    getResourceRoute(resource) {
      switch (resource.resource_type) {
        case 'image':
          return { name: 'ImageDetail', params: { id: resource.resource_id } };
        case 'container':
          return { name: 'ContainerDetail', params: { id: resource.resource_id } };
        case 'volume':
          return { name: 'VolumeDetail', params: { id: resource.resource_id } };
        case 'network':
          return { name: 'NetworkDetail', params: { id: resource.resource_id } };
        default:
          return { name: 'Dashboard' };
      }
    },
    
    async generateReport() {
      if (!this.$refs.form.validate()) return;
      
      try {
        const report = await this.generateComplianceReport({
          name: this.reportForm.name,
          format: this.reportForm.format,
          include_remediation: this.reportForm.includeRemediation
        });
        
        // Reset form
        this.$refs.form.reset();
        
        // Navigate to the report detail view
        this.$router.push({
          name: 'ComplianceReportDetail',
          params: { id: report.id }
        });
      } catch (error) {
        console.error('Failed to generate report:', error);
      }
    },
    
    async exportReport(reportId, format) {
      try {
        await this.exportComplianceReport({ reportId, format });
      } catch (error) {
        console.error('Failed to export report:', error);
      }
    },
    
    confirmDeleteReport(report) {
      this.reportToDelete = report;
      this.deleteDialog = true;
    },
    
    async deleteReport() {
      if (!this.reportToDelete) return;
      
      try {
        await this.deleteComplianceReport(this.reportToDelete.id);
        this.deleteDialog = false;
        this.reportToDelete = null;
      } catch (error) {
        console.error('Failed to delete report:', error);
      }
    }
  }
};
</script>

<style scoped>
.compliance-report {
  margin-bottom: 2rem;
}
</style>
