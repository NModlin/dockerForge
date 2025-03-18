<template>
  <div class="image-detail">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-docker</v-icon>
              Image Details
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Images
              </v-btn>
            </v-card-title>
            
            <v-card-text v-if="loading">
              <v-skeleton-loader type="article" />
            </v-card-text>
            
            <v-card-text v-else-if="!image">
              <v-alert type="error">Image not found</v-alert>
            </v-card-text>
            
            <template v-else>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-list dense>
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>ID</v-list-item-title>
                          <v-list-item-subtitle>{{ image.id }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Short ID</v-list-item-title>
                          <v-list-item-subtitle>{{ image.short_id }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Tags</v-list-item-title>
                          <v-list-item-subtitle>
                            <v-chip
                              v-for="tag in image.tags"
                              :key="tag"
                              class="ma-1"
                              small
                              color="primary"
                              text-color="white"
                            >
                              {{ tag }}
                            </v-chip>
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Size</v-list-item-title>
                          <v-list-item-subtitle>{{ formatSize(image.size) }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title>Created</v-list-item-title>
                          <v-list-item-subtitle>{{ formatDate(image.created_at) }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-list dense>
                      <v-list-item v-if="image.author">
                        <v-list-item-content>
                          <v-list-item-title>Author</v-list-item-title>
                          <v-list-item-subtitle>{{ image.author }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item v-if="image.architecture">
                        <v-list-item-content>
                          <v-list-item-title>Architecture</v-list-item-title>
                          <v-list-item-subtitle>{{ image.architecture }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item v-if="image.os">
                        <v-list-item-content>
                          <v-list-item-title>OS</v-list-item-title>
                          <v-list-item-subtitle>{{ image.os }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      
                      <v-list-item v-if="image.digest">
                        <v-list-item-content>
                          <v-list-item-title>Digest</v-list-item-title>
                          <v-list-item-subtitle>{{ image.digest }}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
              </v-card-text>
              
              <v-divider></v-divider>
              
              <v-tabs v-model="activeTab" background-color="primary" dark>
                <v-tab>Labels</v-tab>
                <v-tab>Environment</v-tab>
                <v-tab>Ports</v-tab>
                <v-tab>Volumes</v-tab>
                <v-tab>Security</v-tab>
              </v-tabs>
              
              <v-tabs-items v-model="activeTab">
                <!-- Labels Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-simple-table v-if="image.labels && Object.keys(image.labels).length > 0">
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th>Key</th>
                              <th>Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(value, key) in image.labels" :key="key">
                              <td>{{ key }}</td>
                              <td>{{ value }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                      <v-alert v-else type="info">No labels found</v-alert>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Environment Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-simple-table v-if="image.env && image.env.length > 0">
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th>Key</th>
                              <th>Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="env in image.env" :key="env.key">
                              <td>{{ env.key }}</td>
                              <td>{{ env.value }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                      <v-alert v-else type="info">No environment variables found</v-alert>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Ports Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-simple-table v-if="image.exposed_ports && image.exposed_ports.length > 0">
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th>Container Port</th>
                              <th>Protocol</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="port in image.exposed_ports" :key="`${port.container_port}-${port.protocol}`">
                              <td>{{ port.container_port }}</td>
                              <td>{{ port.protocol }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                      <v-alert v-else type="info">No exposed ports found</v-alert>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Volumes Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-simple-table v-if="image.volumes && image.volumes.length > 0">
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th>Container Path</th>
                              <th>Mode</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="volume in image.volumes" :key="volume.container_path">
                              <td>{{ volume.container_path }}</td>
                              <td>{{ volume.mode || 'rw' }}</td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                      <v-alert v-else type="info">No volumes found</v-alert>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Security Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12">
                          <v-btn color="primary" @click="scanImage" :loading="scanning">
                            <v-icon left>mdi-shield-search</v-icon>
                            Scan for Vulnerabilities
                          </v-btn>
                        </v-col>
                      </v-row>
                      
                      <v-row v-if="scans.length > 0">
                        <v-col cols="12">
                          <h3>Scan History</h3>
                          <v-simple-table>
                            <template v-slot:default>
                              <thead>
                                <tr>
                                  <th>ID</th>
                                  <th>Type</th>
                                  <th>Status</th>
                                  <th>Started</th>
                                  <th>Completed</th>
                                  <th>Vulnerabilities</th>
                                  <th>Actions</th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr v-for="scan in scans" :key="scan.id">
                                  <td>{{ scan.id }}</td>
                                  <td>{{ scan.scan_type }}</td>
                                  <td>
                                    <v-chip
                                      small
                                      :color="getScanStatusColor(scan.status)"
                                      text-color="white"
                                    >
                                      {{ scan.status }}
                                    </v-chip>
                                  </td>
                                  <td>{{ formatDate(scan.started_at) }}</td>
                                  <td>{{ formatDate(scan.completed_at) }}</td>
                                  <td>
                                    <v-chip
                                      v-if="scan.critical_count > 0"
                                      small
                                      color="red"
                                      text-color="white"
                                      class="mr-1"
                                    >
                                      {{ scan.critical_count }} Critical
                                    </v-chip>
                                    <v-chip
                                      v-if="scan.high_count > 0"
                                      small
                                      color="orange"
                                      text-color="white"
                                      class="mr-1"
                                    >
                                      {{ scan.high_count }} High
                                    </v-chip>
                                    <v-chip
                                      v-if="scan.medium_count > 0"
                                      small
                                      color="yellow"
                                      text-color="black"
                                      class="mr-1"
                                    >
                                      {{ scan.medium_count }} Medium
                                    </v-chip>
                                    <v-chip
                                      v-if="scan.low_count > 0"
                                      small
                                      color="blue"
                                      text-color="white"
                                    >
                                      {{ scan.low_count }} Low
                                    </v-chip>
                                  </td>
                                  <td>
                                    <v-btn
                                      icon
                                      small
                                      @click="viewScanDetails(scan.id)"
                                      :disabled="scan.status !== 'completed'"
                                    >
                                      <v-icon small>mdi-eye</v-icon>
                                    </v-btn>
                                  </td>
                                </tr>
                              </tbody>
                            </template>
                          </v-simple-table>
                        </v-col>
                      </v-row>
                      
                      <v-row v-else>
                        <v-col cols="12">
                          <v-alert type="info">No security scans have been performed on this image</v-alert>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
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
import { mapState, mapActions } from 'vuex';
import { format, parseISO } from 'date-fns';

export default {
  name: 'ImageDetail',
  
  data() {
    return {
      activeTab: 0,
      loading: false,
      scanning: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },
  
  computed: {
    ...mapState('images', ['image', 'scans']),
    
    imageId() {
      return this.$route.params.id;
    },
  },
  
  created() {
    this.fetchImageDetails();
    this.fetchImageScans();
  },
  
  methods: {
    ...mapActions('images', ['getImage', 'getImageScans', 'scanImageVulnerabilities']),
    
    async fetchImageDetails() {
      this.loading = true;
      try {
        await this.getImage(this.imageId);
      } catch (error) {
        this.showError('Failed to fetch image details: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchImageScans() {
      try {
        await this.getImageScans(this.imageId);
      } catch (error) {
        this.showError('Failed to fetch image scans: ' + error.message);
      }
    },
    
    async scanImage() {
      this.scanning = true;
      try {
        await this.scanImageVulnerabilities(this.imageId);
        this.showSuccess('Security scan initiated');
        await this.fetchImageScans();
      } catch (error) {
        this.showError('Failed to scan image: ' + error.message);
      } finally {
        this.scanning = false;
      }
    },
    
    viewScanDetails(scanId) {
      this.$router.push({
        name: 'ImageSecurity',
        params: { id: this.imageId, scanId: scanId },
      });
    },
    
    goBack() {
      this.$router.push({ name: 'Images' });
    },
    
    formatSize(size) {
      if (!size) return 'Unknown';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let formattedSize = size;
      let unitIndex = 0;
      
      while (formattedSize >= 1024 && unitIndex < units.length - 1) {
        formattedSize /= 1024;
        unitIndex++;
      }
      
      return `${formattedSize.toFixed(2)} ${units[unitIndex]}`;
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
    
    showSuccess(message) {
      this.snackbarText = message;
      this.snackbarColor = 'success';
      this.snackbar = true;
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
.image-detail {
  height: 100%;
}
</style>
