<template>
  <v-dialog
    v-model="dialog"
    max-width="900px"
    scrollable
    persistent
  >
    <v-card>
      <v-card-title class="headline">
        <v-icon left>mdi-tune</v-icon>
        Compose Control Panel: {{ project.name }}
        <v-chip
          small
          :color="getStatusColor(project.status)"
          text-color="white"
          class="ml-2"
        >
          {{ project.status }}
        </v-chip>
        <v-spacer></v-spacer>
        <v-btn icon @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-0">
        <v-tabs v-model="activeTab" background-color="primary" dark>
          <v-tab>
            <v-icon left>mdi-play-pause</v-icon>
            Controls
          </v-tab>
          <v-tab>
            <v-icon left>mdi-scale-balance</v-icon>
            Scaling
          </v-tab>
          <v-tab>
            <v-icon left>mdi-text-box-outline</v-icon>
            Logs
          </v-tab>
          <v-tab>
            <v-icon left>mdi-information-outline</v-icon>
            Info
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <!-- Controls Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <v-alert
                  v-if="error"
                  type="error"
                  dense
                  dismissible
                  class="mb-4"
                >
                  {{ error }}
                </v-alert>

                <h3 class="text-h6 mb-3">Project Controls</h3>
                <v-card outlined class="mb-4">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" sm="6" md="3">
                        <v-btn
                          block
                          color="success"
                          :loading="loading"
                          :disabled="project.status === 'running'"
                          @click="startProject"
                        >
                          <v-icon left>mdi-play</v-icon>
                          Up
                        </v-btn>
                      </v-col>
                      <v-col cols="12" sm="6" md="3">
                        <v-btn
                          block
                          color="error"
                          :loading="loading"
                          :disabled="project.status === 'stopped'"
                          @click="stopProject"
                        >
                          <v-icon left>mdi-stop</v-icon>
                          Down
                        </v-btn>
                      </v-col>
                      <v-col cols="12" sm="6" md="3">
                        <v-btn
                          block
                          color="warning"
                          :loading="loading"
                          @click="restartProject"
                        >
                          <v-icon left>mdi-restart</v-icon>
                          Restart
                        </v-btn>
                      </v-col>
                      <v-col cols="12" sm="6" md="3">
                        <v-btn
                          block
                          color="info"
                          :loading="loading"
                          @click="pullImages"
                        >
                          <v-icon left>mdi-cloud-download</v-icon>
                          Pull
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>

                <h3 class="text-h6 mb-3">Advanced Options</h3>
                <v-card outlined>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" sm="6">
                        <v-checkbox
                          v-model="options.removeVolumes"
                          label="Remove volumes when stopping"
                          hint="This will delete all data in volumes when stopping the project"
                          persistent-hint
                        ></v-checkbox>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-checkbox
                          v-model="options.removeOrphans"
                          label="Remove orphaned containers"
                          hint="Remove containers for services not defined in the Compose file"
                          persistent-hint
                        ></v-checkbox>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-checkbox
                          v-model="options.forceRecreate"
                          label="Force recreate containers"
                          hint="Recreate containers even if their configuration hasn't changed"
                          persistent-hint
                        ></v-checkbox>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-checkbox
                          v-model="options.noCache"
                          label="No cache"
                          hint="Do not use cache when building the images"
                          persistent-hint
                        ></v-checkbox>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- Scaling Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h6 mb-3">Service Scaling</h3>
                <v-alert
                  v-if="!project.services || project.services.length === 0"
                  type="info"
                  outlined
                  class="mb-4"
                >
                  No services found in this project.
                </v-alert>

                <v-card
                  v-for="service in project.services"
                  :key="service.name"
                  outlined
                  class="mb-3"
                >
                  <v-card-text>
                    <v-row align="center">
                      <v-col cols="12" sm="4">
                        <div class="d-flex align-center">
                          <v-icon
                            :color="service.status === 'running' ? 'success' : 'grey'"
                            class="mr-2"
                          >
                            {{ service.status === 'running' ? 'mdi-circle' : 'mdi-circle-outline' }}
                          </v-icon>
                          <strong>{{ service.name }}</strong>
                        </div>
                        <div class="text-caption grey--text">
                          {{ service.image || 'Custom build' }}
                        </div>
                      </v-col>
                      <v-col cols="12" sm="5">
                        <v-slider
                          v-model="serviceScales[service.name]"
                          :label="`Instances: ${serviceScales[service.name]}`"
                          min="0"
                          max="10"
                          thumb-label
                          :disabled="project.status !== 'running'"
                        ></v-slider>
                      </v-col>
                      <v-col cols="12" sm="3" class="text-right">
                        <v-btn
                          small
                          color="primary"
                          :disabled="project.status !== 'running' || serviceScales[service.name] === service.replicas"
                          @click="scaleService(service.name, serviceScales[service.name])"
                        >
                          Apply Scale
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>

                <v-btn
                  color="primary"
                  class="mt-3"
                  :disabled="!hasScaleChanges || project.status !== 'running'"
                  @click="applyAllScaling"
                >
                  <v-icon left>mdi-scale-balance</v-icon>
                  Apply All Scaling Changes
                </v-btn>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- Logs Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <div class="d-flex align-center mb-3">
                  <h3 class="text-h6 mr-3">Service Logs</h3>
                  <v-select
                    v-model="selectedService"
                    :items="serviceItems"
                    label="Select Service"
                    dense
                    outlined
                    hide-details
                    class="mx-2"
                    style="max-width: 200px"
                  ></v-select>
                  <v-spacer></v-spacer>
                  <v-checkbox
                    v-model="followLogs"
                    label="Follow logs"
                    hide-details
                    dense
                    class="mr-2"
                  ></v-checkbox>
                  <v-btn
                    small
                    color="primary"
                    @click="fetchLogs"
                    :loading="logsLoading"
                  >
                    <v-icon left>mdi-refresh</v-icon>
                    Refresh
                  </v-btn>
                </div>

                <v-card
                  outlined
                  height="400px"
                  class="log-container"
                >
                  <v-card-text class="pa-2">
                    <div v-if="logsLoading" class="d-flex justify-center align-center" style="height: 100%">
                      <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    </div>
                    <div v-else-if="logs.length === 0" class="d-flex justify-center align-center" style="height: 100%">
                      <v-alert type="info" outlined>
                        No logs available. Select a service and click Refresh.
                      </v-alert>
                    </div>
                    <pre v-else class="logs-pre">{{ logs.join('\n') }}</pre>
                  </v-card-text>
                </v-card>

                <div class="d-flex mt-3">
                  <v-spacer></v-spacer>
                  <v-btn
                    color="secondary"
                    text
                    @click="clearLogs"
                  >
                    <v-icon left>mdi-delete</v-icon>
                    Clear Logs
                  </v-btn>
                  <v-btn
                    color="primary"
                    text
                    @click="downloadLogs"
                    :disabled="logs.length === 0"
                  >
                    <v-icon left>mdi-download</v-icon>
                    Download Logs
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- Info Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h6 mb-3">Project Information</h3>
                <v-simple-table>
                  <template v-slot:default>
                    <tbody>
                      <tr>
                        <td><strong>Name</strong></td>
                        <td>{{ project.name }}</td>
                      </tr>
                      <tr>
                        <td><strong>Status</strong></td>
                        <td>
                          <v-chip
                            small
                            :color="getStatusColor(project.status)"
                            text-color="white"
                          >
                            {{ project.status }}
                          </v-chip>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Location</strong></td>
                        <td>{{ project.location }}</td>
                      </tr>
                      <tr>
                        <td><strong>Services</strong></td>
                        <td>{{ project.services ? project.services.length : 0 }}</td>
                      </tr>
                      <tr>
                        <td><strong>Created</strong></td>
                        <td>{{ formatDate(project.created_at) }}</td>
                      </tr>
                      <tr>
                        <td><strong>Last Updated</strong></td>
                        <td>{{ formatDate(project.updated_at) }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>

                <h3 class="text-h6 mt-4 mb-3">Services</h3>
                <v-expansion-panels>
                  <v-expansion-panel
                    v-for="service in project.services"
                    :key="service.name"
                  >
                    <v-expansion-panel-header>
                      <div class="d-flex align-center">
                        <v-icon
                          :color="service.status === 'running' ? 'success' : 'grey'"
                          class="mr-2"
                        >
                          {{ service.status === 'running' ? 'mdi-circle' : 'mdi-circle-outline' }}
                        </v-icon>
                        {{ service.name }}
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <v-simple-table dense>
                        <template v-slot:default>
                          <tbody>
                            <tr>
                              <td><strong>Image</strong></td>
                              <td>{{ service.image || 'Custom build' }}</td>
                            </tr>
                            <tr v-if="service.ports && service.ports.length">
                              <td><strong>Ports</strong></td>
                              <td>
                                <v-chip
                                  v-for="(port, index) in service.ports"
                                  :key="index"
                                  small
                                  class="mr-1 mb-1"
                                >
                                  {{ port }}
                                </v-chip>
                              </td>
                            </tr>
                            <tr v-if="service.volumes && service.volumes.length">
                              <td><strong>Volumes</strong></td>
                              <td>
                                <div v-for="(volume, index) in service.volumes" :key="index" class="text-caption">
                                  {{ volume }}
                                </div>
                              </td>
                            </tr>
                            <tr v-if="service.environment && Object.keys(service.environment).length">
                              <td><strong>Environment</strong></td>
                              <td>
                                <div v-for="(value, key) in service.environment" :key="key" class="text-caption">
                                  {{ key }}={{ value }}
                                </div>
                              </td>
                            </tr>
                            <tr v-if="service.depends_on && service.depends_on.length">
                              <td><strong>Depends On</strong></td>
                              <td>
                                <v-chip
                                  v-for="(dep, index) in service.depends_on"
                                  :key="index"
                                  small
                                  class="mr-1 mb-1"
                                >
                                  {{ dep }}
                                </v-chip>
                              </td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="grey darken-1"
          text
          @click="close"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'ComposeControlPanel',
  
  props: {
    value: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      activeTab: 0,
      loading: false,
      error: null,
      options: {
        removeVolumes: false,
        removeOrphans: true,
        forceRecreate: false,
        noCache: false
      },
      serviceScales: {},
      selectedService: null,
      logs: [],
      logsLoading: false,
      followLogs: false,
      logsInterval: null
    };
  },
  
  computed: {
    dialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit('input', value);
      }
    },
    
    serviceItems() {
      if (!this.project.services) return [];
      return [
        { text: 'All Services', value: null },
        ...this.project.services.map(service => ({
          text: service.name,
          value: service.name
        }))
      ];
    },
    
    hasScaleChanges() {
      if (!this.project.services) return false;
      
      return this.project.services.some(service => 
        this.serviceScales[service.name] !== service.replicas
      );
    }
  },
  
  watch: {
    project: {
      immediate: true,
      handler(newProject) {
        if (newProject && newProject.services) {
          // Initialize service scales
          this.serviceScales = {};
          newProject.services.forEach(service => {
            this.serviceScales[service.name] = service.replicas || 1;
          });
        }
      }
    },
    
    followLogs(newValue) {
      if (newValue) {
        this.startLogPolling();
      } else {
        this.stopLogPolling();
      }
    },
    
    dialog(newValue) {
      if (!newValue) {
        this.stopLogPolling();
      }
    }
  },
  
  beforeDestroy() {
    this.stopLogPolling();
  },
  
  methods: {
    ...mapActions('compose', [
      'startComposeProject',
      'stopComposeProject',
      'restartComposeProject',
      'pullComposeImages',
      'getComposeLogs'
    ]),
    
    close() {
      this.dialog = false;
    },
    
    getStatusColor(status) {
      switch (status) {
        case 'running':
          return 'success';
        case 'stopped':
          return 'error';
        case 'partial':
          return 'warning';
        default:
          return 'grey';
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    
    async startProject() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.startComposeProject({
          fileId: this.project.id,
          options: {
            forceRecreate: this.options.forceRecreate,
            noCache: this.options.noCache
          }
        });
        
        this.$emit('success', `Project ${this.project.name} started successfully`);
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to start project: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async stopProject() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.stopComposeProject({
          fileId: this.project.id,
          options: {
            removeVolumes: this.options.removeVolumes,
            removeOrphans: this.options.removeOrphans
          }
        });
        
        this.$emit('success', `Project ${this.project.name} stopped successfully`);
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to stop project: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async restartProject() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.restartComposeProject({
          fileId: this.project.id,
          options: {
            forceRecreate: this.options.forceRecreate
          }
        });
        
        this.$emit('success', `Project ${this.project.name} restarted successfully`);
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to restart project: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async pullImages() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.pullComposeImages({
          fileId: this.project.id
        });
        
        this.$emit('success', `Images for project ${this.project.name} pulled successfully`);
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to pull images: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async scaleService(serviceName, scale) {
      this.loading = true;
      this.error = null;
      
      try {
        // In a real implementation, this would call an API endpoint
        // For now, we'll just simulate success
        console.log(`Scaling service ${serviceName} to ${scale} instances`);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        this.$emit('success', `Service ${serviceName} scaled to ${scale} instances`);
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to scale service: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async applyAllScaling() {
      this.loading = true;
      this.error = null;
      
      try {
        // In a real implementation, this would call an API endpoint
        // For now, we'll just simulate success
        const scalingChanges = {};
        
        this.project.services.forEach(service => {
          if (this.serviceScales[service.name] !== service.replicas) {
            scalingChanges[service.name] = this.serviceScales[service.name];
          }
        });
        
        console.log('Applying scaling changes:', scalingChanges);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        this.$emit('success', 'Service scaling applied successfully');
        this.$emit('refresh');
      } catch (error) {
        this.error = `Failed to apply scaling: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchLogs() {
      this.logsLoading = true;
      this.error = null;
      
      try {
        const response = await this.getComposeLogs({
          fileId: this.project.id,
          service: this.selectedService,
          tail: 100
        });
        
        this.logs = response.logs || [];
        
        if (this.followLogs) {
          this.startLogPolling();
        }
      } catch (error) {
        this.error = `Failed to fetch logs: ${error.message || 'Unknown error'}`;
        this.$emit('error', this.error);
      } finally {
        this.logsLoading = false;
      }
    },
    
    startLogPolling() {
      this.stopLogPolling(); // Clear any existing interval
      
      this.logsInterval = setInterval(() => {
        if (this.dialog && this.followLogs && this.activeTab === 2) {
          this.fetchLogs();
        } else {
          this.stopLogPolling();
        }
      }, 5000); // Poll every 5 seconds
    },
    
    stopLogPolling() {
      if (this.logsInterval) {
        clearInterval(this.logsInterval);
        this.logsInterval = null;
      }
    },
    
    clearLogs() {
      this.logs = [];
    },
    
    downloadLogs() {
      if (this.logs.length === 0) return;
      
      const logText = this.logs.join('\n');
      const blob = new Blob([logText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.project.name}-${this.selectedService || 'all'}-logs.txt`;
      document.body.appendChild(a);
      a.click();
      
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 100);
    }
  }
};
</script>

<style scoped>
.log-container {
  overflow: hidden;
}

.logs-pre {
  height: 100%;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 12px;
  padding: 8px;
  margin: 0;
}
</style>
