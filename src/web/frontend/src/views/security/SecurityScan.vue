<template>
  <div class="security-scan">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-shield-search</v-icon>
              Vulnerability Scanning
              <v-spacer></v-spacer>
              <v-btn color="primary" :to="{ name: 'Security' }">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Dashboard
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <p class="text-body-1 mb-4">
                Scan your Docker images and containers for vulnerabilities. The scanner will check for known security issues in the packages and dependencies.
              </p>
              
              <v-tabs v-model="activeTab" grow>
                <v-tab>
                  <v-icon left>mdi-image</v-icon>
                  Image Scan
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-docker</v-icon>
                  Container Scan
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-history</v-icon>
                  Scan History
                </v-tab>
              </v-tabs>
              
              <v-tabs-items v-model="activeTab">
                <!-- Image Scan Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-form ref="imageScanForm" v-model="imageScanFormValid" @submit.prevent="scanImage">
                        <v-autocomplete
                          v-model="imageScan.imageName"
                          :items="availableImages"
                          label="Select Image"
                          item-text="name"
                          item-value="name"
                          :rules="[v => !!v || 'Image is required']"
                          required
                          clearable
                          return-object
                          :loading="imagesLoading"
                          :disabled="scanning"
                        >
                          <template v-slot:selection="{ item }">
                            <span>{{ item.name }}</span>
                          </template>
                          <template v-slot:item="{ item }">
                            <v-list-item-avatar>
                              <v-icon>mdi-image</v-icon>
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title>{{ item.name }}</v-list-item-title>
                              <v-list-item-subtitle>{{ item.id.substring(0, 12) }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </template>
                        </v-autocomplete>
                        
                        <v-select
                          v-model="imageScan.severityFilter"
                          :items="severityLevels"
                          label="Severity Filter"
                          multiple
                          chips
                          hint="Select severity levels to include in the scan results"
                          persistent-hint
                          :disabled="scanning"
                        ></v-select>
                        
                        <v-switch
                          v-model="imageScan.ignoreUnfixed"
                          label="Ignore Unfixed Vulnerabilities"
                          hint="Only show vulnerabilities that have a fix available"
                          persistent-hint
                          :disabled="scanning"
                        ></v-switch>
                        
                        <v-btn
                          color="primary"
                          type="submit"
                          class="mt-4"
                          :loading="scanning"
                          :disabled="!imageScanFormValid || scanning"
                        >
                          <v-icon left>mdi-shield-search</v-icon>
                          Start Scan
                        </v-btn>
                      </v-form>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Container Scan Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-form ref="containerScanForm" v-model="containerScanFormValid" @submit.prevent="scanContainer">
                        <v-autocomplete
                          v-model="containerScan.container"
                          :items="availableContainers"
                          label="Select Container"
                          item-text="name"
                          item-value="id"
                          :rules="[v => !!v || 'Container is required']"
                          required
                          clearable
                          return-object
                          :loading="containersLoading"
                          :disabled="scanning"
                        >
                          <template v-slot:selection="{ item }">
                            <span>{{ item.name }}</span>
                          </template>
                          <template v-slot:item="{ item }">
                            <v-list-item-avatar>
                              <v-icon>mdi-docker</v-icon>
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title>{{ item.name }}</v-list-item-title>
                              <v-list-item-subtitle>{{ item.id.substring(0, 12) }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </template>
                        </v-autocomplete>
                        
                        <v-select
                          v-model="containerScan.severityFilter"
                          :items="severityLevels"
                          label="Severity Filter"
                          multiple
                          chips
                          hint="Select severity levels to include in the scan results"
                          persistent-hint
                          :disabled="scanning"
                        ></v-select>
                        
                        <v-switch
                          v-model="containerScan.ignoreUnfixed"
                          label="Ignore Unfixed Vulnerabilities"
                          hint="Only show vulnerabilities that have a fix available"
                          persistent-hint
                          :disabled="scanning"
                        ></v-switch>
                        
                        <v-btn
                          color="primary"
                          type="submit"
                          class="mt-4"
                          :loading="scanning"
                          :disabled="!containerScanFormValid || scanning"
                        >
                          <v-icon left>mdi-shield-search</v-icon>
                          Start Scan
                        </v-btn>
                      </v-form>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Scan History Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-data-table
                        :headers="scanHistoryHeaders"
                        :items="scans"
                        :loading="loading"
                        :items-per-page="10"
                        :footer-props="{
                          'items-per-page-options': [5, 10, 15, 20],
                        }"
                        class="elevation-1"
                      >
                        <!-- Target column -->
                        <template v-slot:item.target="{ item }">
                          <span>{{ item.target }}</span>
                        </template>
                        
                        <!-- Scan Type column -->
                        <template v-slot:item.scan_type="{ item }">
                          <v-chip
                            :color="item.scan_type === 'IMAGE' ? 'blue' : 'green'"
                            text-color="white"
                            small
                          >
                            {{ item.scan_type }}
                          </v-chip>
                        </template>
                        
                        <!-- Status column -->
                        <template v-slot:item.status="{ item }">
                          <v-chip
                            :color="getStatusColor(item.status)"
                            text-color="white"
                            small
                          >
                            {{ item.status }}
                          </v-chip>
                        </template>
                        
                        <!-- Vulnerabilities column -->
                        <template v-slot:item.total_vulnerabilities="{ item }">
                          <template v-if="item.status === 'COMPLETED'">
                            <v-chip
                              v-if="item.vulnerability_counts.CRITICAL > 0"
                              color="red"
                              text-color="white"
                              small
                              class="mr-1"
                            >
                              {{ item.vulnerability_counts.CRITICAL }} Critical
                            </v-chip>
                            <v-chip
                              v-if="item.vulnerability_counts.HIGH > 0"
                              color="orange"
                              text-color="white"
                              small
                              class="mr-1"
                            >
                              {{ item.vulnerability_counts.HIGH }} High
                            </v-chip>
                            <v-chip
                              v-if="item.vulnerability_counts.MEDIUM > 0"
                              color="amber"
                              text-color="white"
                              small
                              class="mr-1"
                            >
                              {{ item.vulnerability_counts.MEDIUM }} Medium
                            </v-chip>
                            <v-chip
                              v-if="item.vulnerability_counts.LOW > 0"
                              color="blue"
                              text-color="white"
                              small
                              class="mr-1"
                            >
                              {{ item.vulnerability_counts.LOW }} Low
                            </v-chip>
                            <span v-if="item.total_vulnerabilities === 0" class="success--text">
                              No vulnerabilities found
                            </span>
                          </template>
                          <v-progress-circular
                            v-else-if="item.status === 'IN_PROGRESS'"
                            indeterminate
                            color="primary"
                            size="24"
                          ></v-progress-circular>
                          <span v-else>-</span>
                        </template>
                        
                        <!-- Started At column -->
                        <template v-slot:item.started_at="{ item }">
                          {{ formatDate(item.started_at) }}
                        </template>
                        
                        <!-- Duration column -->
                        <template v-slot:item.duration_seconds="{ item }">
                          <span v-if="item.duration_seconds">
                            {{ formatDuration(item.duration_seconds) }}
                          </span>
                          <span v-else-if="item.status === 'IN_PROGRESS'">
                            In progress
                          </span>
                          <span v-else>-</span>
                        </template>
                        
                        <!-- Actions column -->
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            icon
                            small
                            color="primary"
                            :disabled="item.status !== 'COMPLETED'"
                            @click="viewScanResults(item)"
                            :title="item.status === 'COMPLETED' ? 'View Results' : 'Scan not completed'"
                          >
                            <v-icon>mdi-eye</v-icon>
                          </v-btn>
                          <v-btn
                            icon
                            small
                            color="info"
                            :disabled="item.status !== 'IN_PROGRESS'"
                            @click="refreshScan(item)"
                            :title="item.status === 'IN_PROGRESS' ? 'Refresh Status' : 'Scan not in progress'"
                          >
                            <v-icon>mdi-refresh</v-icon>
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Scan Progress Dialog -->
      <v-dialog v-model="scanProgressDialog" persistent max-width="500">
        <v-card>
          <v-card-title class="headline">
            <v-icon left color="primary">mdi-shield-search</v-icon>
            Scan in Progress
          </v-card-title>
          <v-card-text>
            <v-progress-linear
              indeterminate
              color="primary"
              class="mb-4"
            ></v-progress-linear>
            <p>Scanning {{ currentScan?.target || 'target' }} for vulnerabilities...</p>
            <p class="text-caption">This may take a few minutes depending on the size of the image or container.</p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              text
              @click="viewScanResults(currentScan)"
              :disabled="!currentScan || currentScan.status !== 'COMPLETED'"
            >
              View Results
            </v-btn>
            <v-btn
              color="grey darken-1"
              text
              @click="scanProgressDialog = false"
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

export default {
  name: 'SecurityScan',
  data() {
    return {
      activeTab: 0,
      imageScanFormValid: false,
      containerScanFormValid: false,
      scanning: false,
      scanProgressDialog: false,
      currentScan: null,
      imageScan: {
        imageName: null,
        severityFilter: ['CRITICAL', 'HIGH'],
        ignoreUnfixed: false
      },
      containerScan: {
        container: null,
        severityFilter: ['CRITICAL', 'HIGH'],
        ignoreUnfixed: false
      },
      severityLevels: [
        { text: 'Critical', value: 'CRITICAL' },
        { text: 'High', value: 'HIGH' },
        { text: 'Medium', value: 'MEDIUM' },
        { text: 'Low', value: 'LOW' },
        { text: 'Unknown', value: 'UNKNOWN' }
      ],
      scanHistoryHeaders: [
        { text: 'Target', value: 'target', sortable: true },
        { text: 'Type', value: 'scan_type', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Vulnerabilities', value: 'total_vulnerabilities', sortable: true },
        { text: 'Started', value: 'started_at', sortable: true },
        { text: 'Duration', value: 'duration_seconds', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      imagesLoading: false,
      containersLoading: false,
      availableImages: [],
      availableContainers: [],
      pollingInterval: null
    };
  },
  computed: {
    ...mapState({
      loading: state => state.security.loading,
      error: state => state.security.error
    }),
    ...mapGetters({
      scans: 'security/scans',
      pendingScans: 'security/pendingScans'
    })
  },
  created() {
    this.fetchScans();
    this.loadImages();
    this.loadContainers();
    
    // Set up polling for pending scans
    this.pollingInterval = setInterval(this.pollPendingScans, 5000);
  },
  beforeUnmount() {
    // Clear polling interval when component is destroyed
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  methods: {
    ...mapActions({
      fetchScans: 'security/fetchScans',
      fetchScan: 'security/fetchScan',
      scanImageAction: 'security/scanImage',
      scanContainerAction: 'security/scanContainer',
      pollScanStatus: 'security/pollScanStatus'
    }),
    
    async loadImages() {
      this.imagesLoading = true;
      try {
        const response = await this.$axios.get('/api/images');
        this.availableImages = response.data.map(image => ({
          id: image.id,
          name: image.tags && image.tags.length > 0 ? image.tags[0] : image.id.substring(0, 12),
          tags: image.tags
        }));
      } catch (error) {
        console.error('Error loading images:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to load images: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
      } finally {
        this.imagesLoading = false;
      }
    },
    
    async loadContainers() {
      this.containersLoading = true;
      try {
        const response = await this.$axios.get('/api/containers');
        this.availableContainers = response.data.map(container => ({
          id: container.id,
          name: container.name,
          status: container.status
        }));
      } catch (error) {
        console.error('Error loading containers:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to load containers: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
      } finally {
        this.containersLoading = false;
      }
    },
    
    async scanImage() {
      if (!this.imageScanFormValid) return;
      
      this.scanning = true;
      this.scanProgressDialog = true;
      
      try {
        const scanId = await this.scanImageAction({
          imageName: this.imageScan.imageName.name,
          severityFilter: this.imageScan.severityFilter,
          ignoreUnfixed: this.imageScan.ignoreUnfixed
        });
        
        // Poll for scan status
        this.currentScan = { scan_id: scanId, target: this.imageScan.imageName.name };
        this.pollScanStatus({ 
          scanId, 
          interval: 2000,
          maxAttempts: 60
        }).then(scan => {
          this.currentScan = scan;
          this.$store.dispatch('showSnackbar', {
            text: 'Scan completed successfully',
            color: 'success'
          });
        }).catch(error => {
          console.error('Error polling scan status:', error);
          this.$store.dispatch('showSnackbar', {
            text: 'Error monitoring scan progress: ' + error.message,
            color: 'error'
          });
        });
      } catch (error) {
        console.error('Error scanning image:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to start image scan: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
        this.scanProgressDialog = false;
      } finally {
        this.scanning = false;
      }
    },
    
    async scanContainer() {
      if (!this.containerScanFormValid) return;
      
      this.scanning = true;
      this.scanProgressDialog = true;
      
      try {
        const scanId = await this.scanContainerAction({
          containerId: this.containerScan.container.id,
          containerName: this.containerScan.container.name,
          severityFilter: this.containerScan.severityFilter,
          ignoreUnfixed: this.containerScan.ignoreUnfixed
        });
        
        // Poll for scan status
        this.currentScan = { scan_id: scanId, target: this.containerScan.container.name };
        this.pollScanStatus({ 
          scanId, 
          interval: 2000,
          maxAttempts: 60
        }).then(scan => {
          this.currentScan = scan;
          this.$store.dispatch('showSnackbar', {
            text: 'Scan completed successfully',
            color: 'success'
          });
        }).catch(error => {
          console.error('Error polling scan status:', error);
          this.$store.dispatch('showSnackbar', {
            text: 'Error monitoring scan progress: ' + error.message,
            color: 'error'
          });
        });
      } catch (error) {
        console.error('Error scanning container:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to start container scan: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
        this.scanProgressDialog = false;
      } finally {
        this.scanning = false;
      }
    },
    
    async viewScanResults(scan) {
      this.scanProgressDialog = false;
      this.$router.push({ 
        name: 'ScanResults', 
        params: { id: scan.scan_id } 
      });
    },
    
    async refreshScan(scan) {
      try {
        await this.fetchScan(scan.scan_id);
        this.$store.dispatch('showSnackbar', {
          text: 'Scan status refreshed',
          color: 'info'
        });
      } catch (error) {
        console.error('Error refreshing scan:', error);
        this.$store.dispatch('showSnackbar', {
          text: 'Failed to refresh scan status: ' + (error.response?.data?.detail || error.message),
          color: 'error'
        });
      }
    },
    
    async pollPendingScans() {
      if (this.pendingScans.length === 0) return;
      
      for (const scan of this.pendingScans) {
        try {
          await this.fetchScan(scan.scan_id);
        } catch (error) {
          console.error(`Error polling scan ${scan.scan_id}:`, error);
        }
      }
    },
    
    getStatusColor(status) {
      switch (status) {
        case 'COMPLETED': return 'success';
        case 'IN_PROGRESS': return 'primary';
        case 'PENDING': return 'info';
        case 'FAILED': return 'error';
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
    }
  }
};
</script>

<style scoped>
.security-scan {
  height: 100%;
}
</style>
