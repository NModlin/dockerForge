<template>
  <div class="image-security">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-shield-search</v-icon>
              Security Scan Results
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Image
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
                    <v-list dense>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Scan ID</v-list-item-title>
                          <v-list-item-subtitle>{{ currentScan.scan.id }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Scan Type</v-list-item-title>
                          <v-list-item-subtitle>{{ currentScan.scan.scan_type }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Status</v-list-item-title>
                          <v-list-item-subtitle>
                            <v-chip
                              small
                              :color="getScanStatusColor(currentScan.scan.status)"
                              text-color="white"
                            >
                              {{ currentScan.scan.status }}
                            </v-chip>
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-list dense>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Started</v-list-item-title>
                          <v-list-item-subtitle>{{ formatDate(currentScan.scan.started_at) }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Completed</v-list-item-title>
                          <v-list-item-subtitle>{{ formatDate(currentScan.scan.completed_at) }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Total Vulnerabilities</v-list-item-title>
                          <v-list-item-subtitle>{{ currentScan.scan.vulnerabilities_count || 0 }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
                
                <v-row class="mt-4">
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title>Vulnerability Summary</v-card-title>
                      <v-card-text>
                        <v-row>
                          <v-col cols="12" sm="6" md="3">
                            <v-card color="red" dark>
                              <v-card-text class="text-center">
                                <div class="text-h4">{{ currentScan.scan.critical_count || 0 }}</div>
                                <div>Critical</div>
                              </v-card-text>
                            </v-card>
                          </v-col>
                          
                          <v-col cols="12" sm="6" md="3">
                            <v-card color="orange" dark>
                              <v-card-text class="text-center">
                                <div class="text-h4">{{ currentScan.scan.high_count || 0 }}</div>
                                <div>High</div>
                              </v-card-text>
                            </v-card>
                          </v-col>
                          
                          <v-col cols="12" sm="6" md="3">
                            <v-card color="yellow" dark>
                              <v-card-text class="text-center">
                                <div class="text-h4 black--text">{{ currentScan.scan.medium_count || 0 }}</div>
                                <div class="black--text">Medium</div>
                              </v-card-text>
                            </v-card>
                          </v-col>
                          
                          <v-col cols="12" sm="6" md="3">
                            <v-card color="blue" dark>
                              <v-card-text class="text-center">
                                <div class="text-h4">{{ currentScan.scan.low_count || 0 }}</div>
                                <div>Low</div>
                              </v-card-text>
                            </v-card>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
              
              <v-divider></v-divider>
              
              <v-card-title>
                Vulnerabilities
                <v-spacer></v-spacer>
                <v-text-field
                  v-model="search"
                  append-icon="mdi-magnify"
                  label="Search"
                  single-line
                  hide-details
                  class="mx-4"
                ></v-text-field>
                <v-select
                  v-model="severityFilter"
                  :items="severityOptions"
                  label="Severity"
                  hide-details
                  class="mx-4"
                  style="max-width: 150px"
                ></v-select>
              </v-card-title>
              
              <v-data-table
                :headers="headers"
                :items="filteredVulnerabilities"
                :search="search"
                :items-per-page="10"
                :footer-props="{
                  'items-per-page-options': [5, 10, 15, 20, 50],
                }"
                class="elevation-1"
              >
                <template v-slot:item.severity="{ item }">
                  <v-chip
                    small
                    :color="getSeverityColor(item.severity)"
                    :text-color="item.severity === 'medium' ? 'black' : 'white'"
                  >
                    {{ item.severity }}
                  </v-chip>
                </template>
                
                <template v-slot:item.reference_urls="{ item }">
                  <div v-if="item.reference_urls && item.reference_urls.length > 0">
                    <v-btn
                      v-for="(url, index) in item.reference_urls"
                      :key="index"
                      x-small
                      text
                      color="primary"
                      :href="url"
                      target="_blank"
                      class="mr-1"
                    >
                      <v-icon x-small left>mdi-open-in-new</v-icon>
                      Link {{ index + 1 }}
                    </v-btn>
                  </div>
                  <span v-else>-</span>
                </template>
                
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    icon
                    small
                    @click="showVulnerabilityDetails(item)"
                  >
                    <v-icon small>mdi-information-outline</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Vulnerability Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="700px">
      <v-card v-if="selectedVulnerability">
        <v-card-title class="headline">
          <v-chip
            small
            :color="getSeverityColor(selectedVulnerability.severity)"
            :text-color="selectedVulnerability.severity === 'medium' ? 'black' : 'white'"
            class="mr-2"
          >
            {{ selectedVulnerability.severity }}
          </v-chip>
          {{ selectedVulnerability.name }}
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="subtitle-1 font-weight-bold">Description</div>
              <div>{{ selectedVulnerability.description }}</div>
            </v-col>
            
            <v-col cols="12" sm="6">
              <div class="subtitle-1 font-weight-bold">Package</div>
              <div>{{ selectedVulnerability.package_name || 'N/A' }}</div>
            </v-col>
            
            <v-col cols="12" sm="6">
              <div class="subtitle-1 font-weight-bold">Current Version</div>
              <div>{{ selectedVulnerability.package_version || 'N/A' }}</div>
            </v-col>
            
            <v-col cols="12" sm="6">
              <div class="subtitle-1 font-weight-bold">Fixed Version</div>
              <div>{{ selectedVulnerability.fixed_version || 'N/A' }}</div>
            </v-col>
            
            <v-col cols="12" sm="6">
              <div class="subtitle-1 font-weight-bold">CVE ID</div>
              <div>{{ selectedVulnerability.cve_id || 'N/A' }}</div>
            </v-col>
            
            <v-col cols="12">
              <div class="subtitle-1 font-weight-bold">References</div>
              <div v-if="selectedVulnerability.reference_urls && selectedVulnerability.reference_urls.length > 0">
                <v-btn
                  v-for="(url, index) in selectedVulnerability.reference_urls"
                  :key="index"
                  small
                  text
                  color="primary"
                  :href="url"
                  target="_blank"
                  class="mr-1 mb-1"
                >
                  <v-icon small left>mdi-open-in-new</v-icon>
                  Reference {{ index + 1 }}
                </v-btn>
              </div>
              <div v-else>No references available</div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            color="info"
            text
            @click="resolveWithAI(selectedVulnerability)"
            :disabled="!selectedVulnerability.fixed_version"
          >
            <v-icon left>mdi-robot</v-icon>
            Resolve with AI
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapActions, mapMutations } from 'vuex';
import axios from 'axios';
import { format, parseISO } from 'date-fns';

export default {
  name: 'ImageSecurity',
  
  data() {
    return {
      loading: false,
      search: '',
      severityFilter: 'all',
      severityOptions: [
        { text: 'All Severities', value: 'all' },
        { text: 'Critical', value: 'critical' },
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Severity', value: 'severity' },
        { text: 'Package', value: 'package_name' },
        { text: 'Current Version', value: 'package_version' },
        { text: 'Fixed Version', value: 'fixed_version' },
        { text: 'CVE ID', value: 'cve_id' },
        { text: 'References', value: 'reference_urls' },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      detailsDialog: false,
      selectedVulnerability: null,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },
  
  computed: {
    ...mapState('images', ['currentScan']),
    
    imageId() {
      return this.$route.params.id;
    },
    
    scanId() {
      return parseInt(this.$route.params.scanId);
    },
    
    filteredVulnerabilities() {
      if (!this.currentScan || !this.currentScan.vulnerabilities) {
        return [];
      }
      
      if (this.severityFilter === 'all') {
        return this.currentScan.vulnerabilities;
      }
      
      return this.currentScan.vulnerabilities.filter(v => v.severity === this.severityFilter);
    },
  },
  
  created() {
    this.fetchScanDetails();
  },
  
  methods: {
    ...mapActions('images', ['getImageScan']),
    ...mapActions({
      updateContext: 'chat/updateContext'
    }),
    ...mapMutations({
      setActive: 'chat/SET_ACTIVE'
    }),
    
    async fetchScanDetails() {
      this.loading = true;
      try {
        await this.getImageScan({ imageId: this.imageId, scanId: this.scanId });
      } catch (error) {
        this.showError('Failed to fetch scan details: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    goBack() {
      this.$router.push({ name: 'ImageDetail', params: { id: this.imageId } });
    },
    
    showVulnerabilityDetails(vulnerability) {
      this.selectedVulnerability = vulnerability;
      this.detailsDialog = true;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      try {
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
      } catch (error) {
        return dateString;
      }
    },
    
    getScanStatusColor(status) {
      switch (status) {
        case 'completed':
          return 'success';
        case 'running':
          return 'info';
        case 'failed':
          return 'error';
        default:
          return 'grey';
      }
    },
    
    getSeverityColor(severity) {
      switch (severity) {
        case 'critical':
          return 'red';
        case 'high':
          return 'orange';
        case 'medium':
          return 'yellow';
        case 'low':
          return 'blue';
        default:
          return 'grey';
      }
    },
    
    showSuccess(message) {
      this.snackbarText = message;
      this.snackbarColor = 'success';
      this.snackbar = true;
    },
    
    async resolveWithAI(vulnerability) {
      try {
        // Start a security workflow for the vulnerability
        const response = await axios.post(`/api/chat/security/start-workflow?vulnerability_id=${vulnerability.cve_id || vulnerability.name}`);
        
        // Set context data for chat
        this.updateContext({
          currentPage: 'security',
          currentImageId: this.imageId,
          vulnerability_id: vulnerability.cve_id || vulnerability.name,
          vulnerability_severity: vulnerability.severity,
          vulnerability_description: vulnerability.description,
          affected_package: vulnerability.package_name,
          current_version: vulnerability.package_version,
          fixed_version: vulnerability.fixed_version,
          cve_id: vulnerability.cve_id,
          workflow_id: response.data.message.context?.workflow_id
        });
        
        // Open chat sidebar
        this.setActive(true);
        
        // Close the details dialog
        this.detailsDialog = false;
        
        // Show success notification
        this.showSuccess('AI-assisted resolution workflow started. Check the chat sidebar.');
      } catch (error) {
        console.error('Error starting security workflow:', error);
        this.showError('Failed to start AI resolution workflow.');
      }
    },
    
    showError(message) {
      this.snackbarText = message;
      this.snackbarColor = 'error';
      this.snackbar = true;
    },
  },
};
</script>

<style scoped>
.image-security {
  height: 100%;
}
</style>
