<template>
  <div class="container-inspect">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon left>mdi-magnify</v-icon>
        Container Inspection
        <v-spacer></v-spacer>
        <v-btn icon @click="copyToClipboard" title="Copy to clipboard">
          <v-icon>mdi-content-copy</v-icon>
        </v-btn>
        <v-btn icon @click="expandAll" title="Expand all sections">
          <v-icon>mdi-arrow-expand-all</v-icon>
        </v-btn>
        <v-btn icon @click="collapseAll" title="Collapse all sections">
          <v-icon>mdi-arrow-collapse-all</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <div v-if="loading" class="d-flex justify-center align-center my-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else-if="error" class="error-container">
          <v-alert type="error">{{ error }}</v-alert>
        </div>

        <div v-else>
          <!-- Search and filter -->
          <v-text-field
            v-model="searchQuery"
            label="Search in inspect data"
            prepend-icon="mdi-magnify"
            clearable
            outlined
            dense
            class="mb-4"
          ></v-text-field>

          <!-- Inspect data sections -->
          <v-expansion-panels v-model="openPanels" multiple>
            <!-- Config section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="primary">mdi-cog</v-icon>
                  <span class="font-weight-medium">Configuration</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-simple-table dense>
                  <template v-slot:default>
                    <tbody>
                      <tr>
                        <th>Hostname</th>
                        <td>{{ inspectData.Config?.Hostname || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Domain Name</th>
                        <td>{{ inspectData.Config?.Domainname || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>User</th>
                        <td>{{ inspectData.Config?.User || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Working Directory</th>
                        <td>{{ inspectData.Config?.WorkingDir || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Image</th>
                        <td>{{ inspectData.Config?.Image || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Command</th>
                        <td>
                          <code v-if="inspectData.Config?.Cmd">{{ formatArray(inspectData.Config.Cmd) }}</code>
                          <span v-else>N/A</span>
                        </td>
                      </tr>
                      <tr>
                        <th>Entrypoint</th>
                        <td>
                          <code v-if="inspectData.Config?.Entrypoint">{{ formatArray(inspectData.Config.Entrypoint) }}</code>
                          <span v-else>N/A</span>
                        </td>
                      </tr>
                      <tr>
                        <th>Tty</th>
                        <td>{{ inspectData.Config?.Tty ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Open Stdin</th>
                        <td>{{ inspectData.Config?.OpenStdin ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Stdin Once</th>
                        <td>{{ inspectData.Config?.StdinOnce ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Attach Stdin</th>
                        <td>{{ inspectData.Config?.AttachStdin ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Attach Stdout</th>
                        <td>{{ inspectData.Config?.AttachStdout ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Attach Stderr</th>
                        <td>{{ inspectData.Config?.AttachStderr ? 'Yes' : 'No' }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- State section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left :color="getStateColor(inspectData.State?.Status)">mdi-state-machine</v-icon>
                  <span class="font-weight-medium">State</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-simple-table dense>
                  <template v-slot:default>
                    <tbody>
                      <tr>
                        <th>Status</th>
                        <td>
                          <v-chip
                            small
                            :color="getStateColor(inspectData.State?.Status)"
                            text-color="white"
                          >
                            {{ inspectData.State?.Status || 'N/A' }}
                          </v-chip>
                        </td>
                      </tr>
                      <tr>
                        <th>Running</th>
                        <td>{{ inspectData.State?.Running ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Paused</th>
                        <td>{{ inspectData.State?.Paused ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Restarting</th>
                        <td>{{ inspectData.State?.Restarting ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>OOM Killed</th>
                        <td>{{ inspectData.State?.OOMKilled ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Dead</th>
                        <td>{{ inspectData.State?.Dead ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Pid</th>
                        <td>{{ inspectData.State?.Pid || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Exit Code</th>
                        <td>
                          <v-chip
                            v-if="inspectData.State?.ExitCode !== undefined"
                            small
                            :color="inspectData.State.ExitCode === 0 ? 'success' : 'error'"
                            text-color="white"
                          >
                            {{ inspectData.State.ExitCode }}
                          </v-chip>
                          <span v-else>N/A</span>
                        </td>
                      </tr>
                      <tr>
                        <th>Error</th>
                        <td>{{ inspectData.State?.Error || 'None' }}</td>
                      </tr>
                      <tr>
                        <th>Started At</th>
                        <td>{{ formatDate(inspectData.State?.StartedAt) }}</td>
                      </tr>
                      <tr>
                        <th>Finished At</th>
                        <td>{{ formatDate(inspectData.State?.FinishedAt) }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>

                <!-- Health Check Status -->
                <div v-if="inspectData.State?.Health" class="mt-4">
                  <h3 class="subtitle-1 font-weight-medium mb-2">Health Check</h3>
                  <v-chip
                    class="mb-3"
                    :color="getHealthColor(inspectData.State.Health.Status)"
                    text-color="white"
                  >
                    {{ inspectData.State.Health.Status }}
                  </v-chip>
                  
                  <v-simple-table dense>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Time</th>
                          <th>Exit Code</th>
                          <th>Output</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(check, index) in inspectData.State.Health.Log" :key="index">
                          <td>{{ formatDate(check.Start) }}</td>
                          <td>
                            <v-chip
                              x-small
                              :color="check.ExitCode === 0 ? 'success' : 'error'"
                              text-color="white"
                            >
                              {{ check.ExitCode }}
                            </v-chip>
                          </td>
                          <td class="health-check-output">{{ check.Output }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Network Settings section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="blue">mdi-network</v-icon>
                  <span class="font-weight-medium">Network Settings</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-simple-table dense>
                  <template v-slot:default>
                    <tbody>
                      <tr>
                        <th>Bridge</th>
                        <td>{{ inspectData.NetworkSettings?.Bridge || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>SandboxID</th>
                        <td>{{ inspectData.NetworkSettings?.SandboxID || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>HairpinMode</th>
                        <td>{{ inspectData.NetworkSettings?.HairpinMode ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Gateway</th>
                        <td>{{ inspectData.NetworkSettings?.Gateway || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>IP Address</th>
                        <td>{{ inspectData.NetworkSettings?.IPAddress || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>IP Prefix Length</th>
                        <td>{{ inspectData.NetworkSettings?.IPPrefixLen || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>MAC Address</th>
                        <td>{{ inspectData.NetworkSettings?.MacAddress || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>

                <!-- Networks -->
                <div v-if="inspectData.NetworkSettings?.Networks" class="mt-4">
                  <h3 class="subtitle-1 font-weight-medium mb-2">Networks</h3>
                  <v-expansion-panels>
                    <v-expansion-panel
                      v-for="(network, name) in inspectData.NetworkSettings.Networks"
                      :key="name"
                    >
                      <v-expansion-panel-header>
                        {{ name }}
                      </v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <v-simple-table dense>
                          <template v-slot:default>
                            <tbody>
                              <tr>
                                <th>Network ID</th>
                                <td>{{ network.NetworkID || 'N/A' }}</td>
                              </tr>
                              <tr>
                                <th>Endpoint ID</th>
                                <td>{{ network.EndpointID || 'N/A' }}</td>
                              </tr>
                              <tr>
                                <th>Gateway</th>
                                <td>{{ network.Gateway || 'N/A' }}</td>
                              </tr>
                              <tr>
                                <th>IP Address</th>
                                <td>{{ network.IPAddress || 'N/A' }}</td>
                              </tr>
                              <tr>
                                <th>IP Prefix Length</th>
                                <td>{{ network.IPPrefixLen || 'N/A' }}</td>
                              </tr>
                              <tr>
                                <th>MAC Address</th>
                                <td>{{ network.MacAddress || 'N/A' }}</td>
                              </tr>
                            </tbody>
                          </template>
                        </v-simple-table>
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </div>

                <!-- Ports -->
                <div v-if="inspectData.NetworkSettings?.Ports" class="mt-4">
                  <h3 class="subtitle-1 font-weight-medium mb-2">Port Mappings</h3>
                  <v-simple-table dense>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Container Port</th>
                          <th>Host Bindings</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(bindings, port) in inspectData.NetworkSettings.Ports" :key="port">
                          <td>{{ port }}</td>
                          <td>
                            <div v-if="bindings && bindings.length">
                              <div v-for="(binding, index) in bindings" :key="index">
                                {{ binding.HostIp || '0.0.0.0' }}:{{ binding.HostPort }}
                              </div>
                            </div>
                            <div v-else>Not published</div>
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Mounts section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="amber darken-2">mdi-harddisk</v-icon>
                  <span class="font-weight-medium">Mounts</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div v-if="inspectData.Mounts && inspectData.Mounts.length">
                  <v-simple-table dense>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Type</th>
                          <th>Source</th>
                          <th>Destination</th>
                          <th>Mode</th>
                          <th>RW</th>
                          <th>Propagation</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(mount, index) in inspectData.Mounts" :key="index">
                          <td>{{ mount.Type }}</td>
                          <td>{{ mount.Source }}</td>
                          <td>{{ mount.Destination }}</td>
                          <td>{{ mount.Mode }}</td>
                          <td>{{ mount.RW ? 'Yes' : 'No' }}</td>
                          <td>{{ mount.Propagation }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
                <div v-else class="text-center pa-4">
                  No mounts configured
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Host Config section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="deep-purple">mdi-server</v-icon>
                  <span class="font-weight-medium">Host Configuration</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-simple-table dense>
                  <template v-slot:default>
                    <tbody>
                      <tr>
                        <th>CPU Shares</th>
                        <td>{{ inspectData.HostConfig?.CpuShares || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Memory Limit</th>
                        <td>{{ formatBytes(inspectData.HostConfig?.Memory) }}</td>
                      </tr>
                      <tr>
                        <th>Memory Swap</th>
                        <td>{{ formatBytes(inspectData.HostConfig?.MemorySwap) }}</td>
                      </tr>
                      <tr>
                        <th>CPU Period</th>
                        <td>{{ inspectData.HostConfig?.CpuPeriod || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>CPU Quota</th>
                        <td>{{ inspectData.HostConfig?.CpuQuota || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>CpusetCpus</th>
                        <td>{{ inspectData.HostConfig?.CpusetCpus || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>CpusetMems</th>
                        <td>{{ inspectData.HostConfig?.CpusetMems || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>BlkioWeight</th>
                        <td>{{ inspectData.HostConfig?.BlkioWeight || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <th>Privileged</th>
                        <td>{{ inspectData.HostConfig?.Privileged ? 'Yes' : 'No' }}</td>
                      </tr>
                      <tr>
                        <th>Restart Policy</th>
                        <td>
                          {{ inspectData.HostConfig?.RestartPolicy?.Name || 'none' }}
                          <span v-if="inspectData.HostConfig?.RestartPolicy?.MaximumRetryCount > 0">
                            ({{ inspectData.HostConfig.RestartPolicy.MaximumRetryCount }} retries)
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Environment Variables section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="green">mdi-variable</v-icon>
                  <span class="font-weight-medium">Environment Variables</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div v-if="inspectData.Config?.Env && inspectData.Config.Env.length">
                  <v-text-field
                    v-model="envSearch"
                    label="Search environment variables"
                    prepend-icon="mdi-magnify"
                    clearable
                    outlined
                    dense
                    class="mb-2"
                  ></v-text-field>
                  
                  <v-simple-table dense>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Name</th>
                          <th>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(env, index) in filteredEnvVars" :key="index">
                          <td class="font-weight-medium">{{ env.name }}</td>
                          <td>{{ env.value }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
                <div v-else class="text-center pa-4">
                  No environment variables configured
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Labels section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="orange">mdi-tag-multiple</v-icon>
                  <span class="font-weight-medium">Labels</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div v-if="inspectData.Config?.Labels && Object.keys(inspectData.Config.Labels).length">
                  <v-text-field
                    v-model="labelSearch"
                    label="Search labels"
                    prepend-icon="mdi-magnify"
                    clearable
                    outlined
                    dense
                    class="mb-2"
                  ></v-text-field>
                  
                  <v-simple-table dense>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th>Name</th>
                          <th>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(value, key) in filteredLabels" :key="key">
                          <td class="font-weight-medium">{{ key }}</td>
                          <td>{{ value }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
                <div v-else class="text-center pa-4">
                  No labels configured
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <!-- Raw JSON section -->
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="grey darken-1">mdi-code-json</v-icon>
                  <span class="font-weight-medium">Raw JSON</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <pre class="json-content">{{ JSON.stringify(inspectData, null, 2) }}</pre>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'ContainerInspect',
  props: {
    containerId: {
      type: String,
      required: true
    },
    inspectData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      searchQuery: '',
      envSearch: '',
      labelSearch: '',
      openPanels: [0, 1], // Open first two panels by default
    };
  },
  computed: {
    filteredEnvVars() {
      if (!this.inspectData.Config?.Env) return [];
      
      const envVars = this.inspectData.Config.Env.map(env => {
        const parts = env.split('=');
        const name = parts.shift();
        const value = parts.join('='); // Rejoin in case value contains = characters
        return { name, value };
      });
      
      if (!this.envSearch) return envVars;
      
      const search = this.envSearch.toLowerCase();
      return envVars.filter(env => 
        env.name.toLowerCase().includes(search) || 
        env.value.toLowerCase().includes(search)
      );
    },
    filteredLabels() {
      if (!this.inspectData.Config?.Labels) return {};
      
      if (!this.labelSearch) return this.inspectData.Config.Labels;
      
      const search = this.labelSearch.toLowerCase();
      const result = {};
      
      Object.entries(this.inspectData.Config.Labels).forEach(([key, value]) => {
        if (key.toLowerCase().includes(search) || 
            (value && value.toLowerCase().includes(search))) {
          result[key] = value;
        }
      });
      
      return result;
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString || dateString === '0001-01-01T00:00:00Z') return 'N/A';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch (e) {
        return dateString;
      }
    },
    formatBytes(bytes) {
      if (bytes === 0 || bytes === undefined || bytes === null) return 'N/A';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let value = bytes;
      let unitIndex = 0;
      
      while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex++;
      }
      
      return `${value.toFixed(2)} ${units[unitIndex]}`;
    },
    formatArray(arr) {
      if (!arr || !Array.isArray(arr)) return 'N/A';
      return JSON.stringify(arr);
    },
    getStateColor(status) {
      if (!status) return 'grey';
      
      switch (status.toLowerCase()) {
        case 'running':
          return 'success';
        case 'created':
          return 'info';
        case 'exited':
          return 'error';
        case 'paused':
          return 'warning';
        case 'restarting':
          return 'orange';
        default:
          return 'grey';
      }
    },
    getHealthColor(health) {
      if (!health) return 'grey';
      
      switch (health.toLowerCase()) {
        case 'healthy':
          return 'success';
        case 'unhealthy':
          return 'error';
        case 'starting':
          return 'warning';
        default:
          return 'grey';
      }
    },
    copyToClipboard() {
      try {
        navigator.clipboard.writeText(JSON.stringify(this.inspectData, null, 2));
        this.$emit('show-snackbar', {
          text: 'Container inspect data copied to clipboard',
          color: 'success'
        });
      } catch (error) {
        this.$emit('show-snackbar', {
          text: 'Failed to copy to clipboard',
          color: 'error'
        });
      }
    },
    expandAll() {
      this.openPanels = [...Array(10).keys()]; // Open all panels (assuming we have less than 10)
    },
    collapseAll() {
      this.openPanels = []; // Close all panels
    }
  }
};
</script>

<style scoped>
.container-inspect {
  width: 100%;
}

.json-content {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.health-check-output {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
