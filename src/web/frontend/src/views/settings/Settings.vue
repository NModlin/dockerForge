<template>
  <div class="settings">
    <h1 class="text-h4 mb-4">Settings</h1>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Settings Content -->
    <template v-else>
      <v-tabs v-model="activeTab" background-color="primary" dark>
        <v-tab>General</v-tab>
        <v-tab>User Preferences</v-tab>
        <v-tab>API Keys</v-tab>
        <v-tab>Docker</v-tab>
        <v-tab>Security</v-tab>
        <v-tab>Monitoring</v-tab>
        <v-tab>Backup</v-tab>
        <v-tab>Notifications</v-tab>
        <v-tab>Advanced</v-tab>
      </v-tabs>

      <v-tabs-items v-model="activeTab">
        <!-- General Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">General Settings</h2>

              <v-form ref="generalForm" v-model="generalFormValid">
                <v-switch
                  v-model="settings.general.darkMode"
                  label="Dark Mode"
                  hint="Enable dark mode for the UI"
                  persistent-hint
                ></v-switch>

                <v-select
                  v-model="settings.general.language"
                  :items="languageOptions"
                  label="Language"
                  hint="Select your preferred language"
                  persistent-hint
                  class="mt-4"
                ></v-select>

                <v-select
                  v-model="settings.general.dateFormat"
                  :items="dateFormatOptions"
                  label="Date Format"
                  hint="Select your preferred date format"
                  persistent-hint
                  class="mt-4"
                ></v-select>

                <v-text-field
                  v-model="settings.general.refreshInterval"
                  label="Auto-refresh Interval (seconds)"
                  type="number"
                  hint="Set to 0 to disable auto-refresh"
                  persistent-hint
                  :rules="[v => v >= 0 || 'Interval must be non-negative']"
                  class="mt-4"
                ></v-text-field>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveGeneralSettings"
                  :disabled="!generalFormValid"
                >
                  Save General Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- User Preferences -->
        <v-tab-item>
          <user-settings />
        </v-tab-item>

        <!-- API Keys -->
        <v-tab-item>
          <api-keys />
        </v-tab-item>

        <!-- Docker Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Docker Settings</h2>

              <v-tabs v-model="dockerTab" background-color="secondary" dark>
                <v-tab>Connection</v-tab>
                <v-tab>Daemon Configuration</v-tab>
              </v-tabs>

              <v-tabs-items v-model="dockerTab">
                <!-- Docker Connection Settings -->
                <v-tab-item>
                  <v-form ref="dockerForm" v-model="dockerFormValid" class="mt-4">
                    <v-text-field
                      v-model="settings.docker.socketPath"
                      label="Docker Socket Path"
                      hint="Path to the Docker socket"
                      persistent-hint
                      :rules="[v => !!v || 'Socket path is required']"
                    ></v-text-field>

                    <v-switch
                      v-model="settings.docker.useTLS"
                      label="Use TLS"
                      hint="Enable TLS for Docker API communication"
                      persistent-hint
                      class="mt-4"
                    ></v-switch>

                    <v-text-field
                      v-model="settings.docker.certPath"
                      label="Certificate Path"
                      hint="Path to TLS certificates"
                      persistent-hint
                      :disabled="!settings.docker.useTLS"
                      :rules="[v => !settings.docker.useTLS || !!v || 'Certificate path is required when TLS is enabled']"
                      class="mt-4"
                    ></v-text-field>

                    <v-text-field
                      v-model="settings.docker.registryUrl"
                      label="Default Registry URL"
                      hint="URL of the default Docker registry"
                      persistent-hint
                      class="mt-4"
                    ></v-text-field>

                    <v-switch
                      v-model="settings.docker.pruneUnused"
                      label="Auto-prune Unused Resources"
                      hint="Automatically remove unused containers, networks, and images"
                      persistent-hint
                      class="mt-4"
                    ></v-switch>

                    <v-select
                      v-model="settings.docker.pruneSchedule"
                      :items="pruneScheduleOptions"
                      label="Prune Schedule"
                      hint="When to automatically prune unused resources"
                      persistent-hint
                      :disabled="!settings.docker.pruneUnused"
                      class="mt-4"
                    ></v-select>

                    <v-btn
                      color="primary"
                      class="mt-4"
                      @click="saveDockerSettings"
                      :disabled="!dockerFormValid"
                    >
                      Save Connection Settings
                    </v-btn>
                  </v-form>
                </v-tab-item>

                <!-- Docker Daemon Configuration -->
                <v-tab-item>
                  <div class="mt-4">
                    <v-alert
                      v-if="daemonConfigError"
                      type="error"
                      dismissible
                      class="mb-4"
                    >
                      {{ daemonConfigError }}
                    </v-alert>

                    <v-alert
                      v-if="daemonConfigSuccess"
                      type="success"
                      dismissible
                      class="mb-4"
                    >
                      {{ daemonConfigSuccess }}
                    </v-alert>

                    <v-alert
                      type="info"
                      outlined
                      class="mb-4"
                    >
                      <p>These settings modify the Docker daemon configuration file (<code>/etc/docker/daemon.json</code>). Changes require a Docker daemon restart and may temporarily disrupt running containers.</p>
                      <p class="mb-0"><strong>Note:</strong> Incorrect configuration may prevent the Docker daemon from starting. Make sure you know what you're doing!</p>
                    </v-alert>

                    <v-expansion-panels>
                      <!-- Registry Configuration -->
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-server</v-icon>
                            Registry Configuration
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <v-form ref="registryForm" v-model="registryFormValid">
                            <p class="text-subtitle-1 mb-2">Registry Mirrors</p>
                            <p class="text-caption mb-4">Registry mirrors can speed up image pulls by providing alternative download locations.</p>

                            <div v-for="(mirror, i) in daemonConfig.registry.registry_mirrors" :key="`mirror-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.registry.registry_mirrors[i]"
                                label="Registry Mirror URL"
                                placeholder="https://mirror.example.com"
                                :rules="[v => !!v || 'URL is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeMirror(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addMirror"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add Registry Mirror
                            </v-btn>

                            <p class="text-subtitle-1 mb-2">Insecure Registries</p>
                            <p class="text-caption mb-4">Registries that Docker should connect to without TLS verification.</p>

                            <div v-for="(registry, i) in daemonConfig.registry.insecure_registries" :key="`insecure-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.registry.insecure_registries[i]"
                                label="Insecure Registry"
                                placeholder="registry.example.com:5000"
                                :rules="[v => !!v || 'Registry is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeInsecureRegistry(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addInsecureRegistry"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add Insecure Registry
                            </v-btn>

                            <v-btn
                              color="primary"
                              @click="saveRegistryConfig"
                              :disabled="!registryFormValid || registrySaving"
                              class="mt-4"
                            >
                              <v-progress-circular
                                v-if="registrySaving"
                                indeterminate
                                size="20"
                                width="2"
                                class="mr-2"
                              ></v-progress-circular>
                              <v-icon v-else left>mdi-content-save</v-icon>
                              Save Registry Configuration
                            </v-btn>
                          </v-form>
                        </v-expansion-panel-content>
                      </v-expansion-panel>

                      <!-- Logging Configuration -->
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-file-document</v-icon>
                            Logging Configuration
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <v-form ref="loggingForm" v-model="loggingFormValid">
                            <p class="text-subtitle-1 mb-2">Logging Driver</p>
                            <p class="text-caption mb-4">The logging driver determines how container logs are stored and accessed.</p>

                            <v-select
                              v-model="daemonConfig.logging.log_driver"
                              :items="loggingDrivers"
                              item-text="name"
                              item-value="name"
                              label="Logging Driver"
                              :hint="getDriverDescription(daemonConfig.logging.log_driver, 'logging')"
                              persistent-hint
                              class="mb-4"
                            ></v-select>

                            <p class="text-subtitle-1 mb-2">Logging Options</p>
                            <p class="text-caption mb-4">Configure options for the selected logging driver.</p>

                            <div v-for="(value, key) in daemonConfig.logging.log_opts" :key="`log-opt-${key}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="logOptKeys[key]"
                                label="Option Name"
                                :rules="[v => !!v || 'Option name is required']"
                                class="mr-2"
                                @input="updateLogOptKey(key, $event)"
                              ></v-text-field>
                              <v-text-field
                                v-model="daemonConfig.logging.log_opts[key]"
                                label="Option Value"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeLogOpt(key)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addLogOpt"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add Logging Option
                            </v-btn>

                            <v-btn
                              color="primary"
                              @click="saveLoggingConfig"
                              :disabled="!loggingFormValid || loggingSaving"
                              class="mt-4"
                            >
                              <v-progress-circular
                                v-if="loggingSaving"
                                indeterminate
                                size="20"
                                width="2"
                                class="mr-2"
                              ></v-progress-circular>
                              <v-icon v-else left>mdi-content-save</v-icon>
                              Save Logging Configuration
                            </v-btn>
                          </v-form>
                        </v-expansion-panel-content>
                      </v-expansion-panel>

                      <!-- Storage Configuration -->
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-harddisk</v-icon>
                            Storage Configuration
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <v-form ref="storageForm" v-model="storageFormValid">
                            <p class="text-subtitle-1 mb-2">Storage Driver</p>
                            <p class="text-caption mb-4">The storage driver determines how container images and layers are stored on disk.</p>

                            <v-select
                              v-model="daemonConfig.storage.storage_driver"
                              :items="storageDrivers"
                              item-text="name"
                              item-value="name"
                              label="Storage Driver"
                              :hint="getDriverDescription(daemonConfig.storage.storage_driver, 'storage')"
                              persistent-hint
                              class="mb-4"
                            ></v-select>

                            <p class="text-subtitle-1 mb-2">Data Root</p>
                            <p class="text-caption mb-4">The directory where Docker stores all its data.</p>

                            <v-text-field
                              v-model="daemonConfig.storage.data_root"
                              label="Data Root Directory"
                              placeholder="/var/lib/docker"
                              hint="Changing this will not migrate existing data"
                              persistent-hint
                              class="mb-4"
                            ></v-text-field>

                            <p class="text-subtitle-1 mb-2">Storage Options</p>
                            <p class="text-caption mb-4">Configure options for the selected storage driver.</p>

                            <div v-for="(opt, i) in daemonConfig.storage.storage_opts" :key="`storage-opt-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.storage.storage_opts[i]"
                                label="Storage Option"
                                placeholder="dm.basesize=20G"
                                :rules="[v => !!v || 'Option is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeStorageOpt(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addStorageOpt"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add Storage Option
                            </v-btn>

                            <v-btn
                              color="primary"
                              @click="saveStorageConfig"
                              :disabled="!storageFormValid || storageSaving"
                              class="mt-4"
                            >
                              <v-progress-circular
                                v-if="storageSaving"
                                indeterminate
                                size="20"
                                width="2"
                                class="mr-2"
                              ></v-progress-circular>
                              <v-icon v-else left>mdi-content-save</v-icon>
                              Save Storage Configuration
                            </v-btn>
                          </v-form>
                        </v-expansion-panel-content>
                      </v-expansion-panel>

                      <!-- Network Configuration -->
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-network</v-icon>
                            Network Configuration
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <v-form ref="networkForm" v-model="networkFormValid">
                            <p class="text-subtitle-1 mb-2">DNS Settings</p>
                            <p class="text-caption mb-4">Configure DNS servers and options for containers.</p>

                            <div v-for="(dns, i) in daemonConfig.network.dns" :key="`dns-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.network.dns[i]"
                                label="DNS Server"
                                placeholder="8.8.8.8"
                                :rules="[v => !!v || 'DNS server is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeDns(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addDns"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add DNS Server
                            </v-btn>

                            <p class="text-subtitle-1 mb-2">DNS Options</p>
                            <p class="text-caption mb-4">Configure DNS resolver options for containers.</p>

                            <div v-for="(opt, i) in daemonConfig.network.dns_opts" :key="`dns-opt-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.network.dns_opts[i]"
                                label="DNS Option"
                                placeholder="ndots:2"
                                :rules="[v => !!v || 'DNS option is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeDnsOpt(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addDnsOpt"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add DNS Option
                            </v-btn>

                            <p class="text-subtitle-1 mb-2">DNS Search Domains</p>
                            <p class="text-caption mb-4">Configure DNS search domains for containers.</p>

                            <div v-for="(domain, i) in daemonConfig.network.dns_search" :key="`dns-search-${i}`" class="d-flex align-center mb-2">
                              <v-text-field
                                v-model="daemonConfig.network.dns_search[i]"
                                label="Search Domain"
                                placeholder="example.com"
                                :rules="[v => !!v || 'Search domain is required']"
                                class="mr-2"
                              ></v-text-field>
                              <v-btn icon @click="removeDnsSearch(i)">
                                <v-icon>mdi-delete</v-icon>
                              </v-btn>
                            </div>

                            <v-btn
                              text
                              color="primary"
                              @click="addDnsSearch"
                              class="mb-4"
                            >
                              <v-icon left>mdi-plus</v-icon>
                              Add Search Domain
                            </v-btn>

                            <p class="text-subtitle-1 mb-2">IP Address Management</p>
                            <p class="text-caption mb-4">Configure IP address settings for the Docker bridge network.</p>

                            <v-text-field
                              v-model="daemonConfig.network.bip"
                              label="Bridge IP"
                              placeholder="172.17.0.1/16"
                              hint="CIDR notation for the bridge network"
                              persistent-hint
                              class="mb-4"
                            ></v-text-field>

                            <v-switch
                              v-model="daemonConfig.network.ipv6"
                              label="Enable IPv6"
                              hint="Enable IPv6 networking"
                              persistent-hint
                              class="mb-4"
                            ></v-switch>

                            <v-btn
                              color="primary"
                              @click="saveNetworkConfig"
                              :disabled="!networkFormValid || networkSaving"
                              class="mt-4"
                            >
                              <v-progress-circular
                                v-if="networkSaving"
                                indeterminate
                                size="20"
                                width="2"
                                class="mr-2"
                              ></v-progress-circular>
                              <v-icon v-else left>mdi-content-save</v-icon>
                              Save Network Configuration
                            </v-btn>
                          </v-form>
                        </v-expansion-panel-content>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </div>
                </v-tab-item>
              </v-tabs-items>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Security Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Security Settings</h2>

              <v-form ref="securityForm" v-model="securityFormValid">
                <v-switch
                  v-model="settings.security.enableVulnerabilityScanning"
                  label="Enable Vulnerability Scanning"
                  hint="Automatically scan images for vulnerabilities"
                  persistent-hint
                ></v-switch>

                <v-select
                  v-model="settings.security.scanSchedule"
                  :items="scanScheduleOptions"
                  label="Scan Schedule"
                  hint="When to automatically scan images"
                  persistent-hint
                  :disabled="!settings.security.enableVulnerabilityScanning"
                  class="mt-4"
                ></v-select>

                <v-select
                  v-model="settings.security.vulnerabilitySeverity"
                  :items="severityOptions"
                  label="Minimum Vulnerability Severity"
                  hint="Minimum severity level to report"
                  persistent-hint
                  :disabled="!settings.security.enableVulnerabilityScanning"
                  class="mt-4"
                ></v-select>

                <v-switch
                  v-model="settings.security.enforceImageSigning"
                  label="Enforce Image Signing"
                  hint="Only allow signed images to be pulled"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-switch
                  v-model="settings.security.restrictPrivilegedContainers"
                  label="Restrict Privileged Containers"
                  hint="Prevent running containers in privileged mode"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveSecuritySettings"
                  :disabled="!securityFormValid"
                >
                  Save Security Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Monitoring Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Monitoring Settings</h2>

              <v-form ref="monitoringForm" v-model="monitoringFormValid">
                <v-switch
                  v-model="settings.monitoring.enableResourceMonitoring"
                  label="Enable Resource Monitoring"
                  hint="Monitor CPU, memory, and disk usage"
                  persistent-hint
                ></v-switch>

                <v-text-field
                  v-model="settings.monitoring.collectionInterval"
                  label="Collection Interval (seconds)"
                  type="number"
                  hint="How often to collect metrics"
                  persistent-hint
                  :rules="[v => v > 0 || 'Interval must be positive']"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.monitoring.retentionPeriod"
                  label="Data Retention Period (days)"
                  type="number"
                  hint="How long to keep monitoring data"
                  persistent-hint
                  :rules="[v => v > 0 || 'Retention period must be positive']"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>

                <v-switch
                  v-model="settings.monitoring.enableAnomalyDetection"
                  label="Enable Anomaly Detection"
                  hint="Detect unusual resource usage patterns"
                  persistent-hint
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-switch>

                <v-text-field
                  v-model="settings.monitoring.cpuThreshold"
                  label="CPU Alert Threshold (%)"
                  type="number"
                  hint="Alert when CPU usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.monitoring.memoryThreshold"
                  label="Memory Alert Threshold (%)"
                  type="number"
                  hint="Alert when memory usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.monitoring.diskThreshold"
                  label="Disk Alert Threshold (%)"
                  type="number"
                  hint="Alert when disk usage exceeds this percentage"
                  persistent-hint
                  :rules="[
                    v => v >= 0 && v <= 100 || 'Threshold must be between 0 and 100'
                  ]"
                  :disabled="!settings.monitoring.enableResourceMonitoring"
                  class="mt-4"
                ></v-text-field>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveMonitoringSettings"
                  :disabled="!monitoringFormValid"
                >
                  Save Monitoring Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Backup Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Backup Settings</h2>

              <v-form ref="backupForm" v-model="backupFormValid">
                <v-switch
                  v-model="settings.backup.enableAutoBackup"
                  label="Enable Automatic Backups"
                  hint="Automatically backup Docker resources"
                  persistent-hint
                ></v-switch>

                <v-select
                  v-model="settings.backup.backupSchedule"
                  :items="backupScheduleOptions"
                  label="Backup Schedule"
                  hint="When to automatically create backups"
                  persistent-hint
                  :disabled="!settings.backup.enableAutoBackup"
                  class="mt-4"
                ></v-select>

                <v-text-field
                  v-model="settings.backup.backupLocation"
                  label="Backup Storage Location"
                  hint="Path where backups will be stored"
                  persistent-hint
                  :rules="[v => !!v || 'Backup location is required']"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.backup.retentionCount"
                  label="Backup Retention Count"
                  type="number"
                  hint="Number of backups to keep"
                  persistent-hint
                  :rules="[v => v > 0 || 'Retention count must be positive']"
                  class="mt-4"
                ></v-text-field>

                <v-switch
                  v-model="settings.backup.compressBackups"
                  label="Compress Backups"
                  hint="Compress backup files to save space"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-switch
                  v-model="settings.backup.includeVolumes"
                  label="Include Volumes in Backups"
                  hint="Include volume data in backups"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveBackupSettings"
                  :disabled="!backupFormValid"
                >
                  Save Backup Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Notification Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Notification Settings</h2>

              <v-form ref="notificationForm" v-model="notificationFormValid">
                <v-switch
                  v-model="settings.notifications.enableEmailNotifications"
                  label="Enable Email Notifications"
                  hint="Send notifications via email"
                  persistent-hint
                ></v-switch>

                <v-text-field
                  v-model="settings.notifications.emailRecipients"
                  label="Email Recipients"
                  hint="Comma-separated list of email addresses"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'Email recipients are required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.notifications.smtpServer"
                  label="SMTP Server"
                  hint="SMTP server address"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'SMTP server is required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.notifications.smtpPort"
                  label="SMTP Port"
                  type="number"
                  hint="SMTP server port"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableEmailNotifications || !!v || 'SMTP port is required'
                  ]"
                  :disabled="!settings.notifications.enableEmailNotifications"
                  class="mt-4"
                ></v-text-field>

                <v-switch
                  v-model="settings.notifications.enableSlackNotifications"
                  label="Enable Slack Notifications"
                  hint="Send notifications to Slack"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-text-field
                  v-model="settings.notifications.slackWebhookUrl"
                  label="Slack Webhook URL"
                  hint="Webhook URL for Slack integration"
                  persistent-hint
                  :rules="[
                    v => !settings.notifications.enableSlackNotifications || !!v || 'Webhook URL is required'
                  ]"
                  :disabled="!settings.notifications.enableSlackNotifications"
                  class="mt-4"
                ></v-text-field>

                <v-select
                  v-model="settings.notifications.notificationEvents"
                  :items="notificationEventOptions"
                  label="Events to Notify"
                  hint="Select which events trigger notifications"
                  persistent-hint
                  multiple
                  chips
                  class="mt-4"
                ></v-select>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveNotificationSettings"
                  :disabled="!notificationFormValid"
                >
                  Save Notification Settings
                </v-btn>

                <v-btn
                  color="secondary"
                  class="mt-4 ml-2"
                  @click="testNotifications"
                >
                  Test Notifications
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>

        <!-- Advanced Settings -->
        <v-tab-item>
          <v-card flat>
            <v-card-text>
              <h2 class="text-h5 mb-4">Advanced Settings</h2>

              <v-alert
                type="warning"
                class="mb-4"
              >
                These settings are for advanced users. Incorrect configuration may cause system instability.
              </v-alert>

              <v-form ref="advancedForm" v-model="advancedFormValid">
                <v-switch
                  v-model="settings.advanced.enableDebugMode"
                  label="Enable Debug Mode"
                  hint="Enable detailed logging for troubleshooting"
                  persistent-hint
                ></v-switch>

                <v-select
                  v-model="settings.advanced.logLevel"
                  :items="logLevelOptions"
                  label="Log Level"
                  hint="Set the logging verbosity"
                  persistent-hint
                  class="mt-4"
                ></v-select>

                <v-text-field
                  v-model="settings.advanced.apiRateLimit"
                  label="API Rate Limit (requests per minute)"
                  type="number"
                  hint="Limit API request rate"
                  persistent-hint
                  :rules="[v => v > 0 || 'Rate limit must be positive']"
                  class="mt-4"
                ></v-text-field>

                <v-text-field
                  v-model="settings.advanced.sessionTimeout"
                  label="Session Timeout (minutes)"
                  type="number"
                  hint="User session timeout"
                  persistent-hint
                  :rules="[v => v > 0 || 'Timeout must be positive']"
                  class="mt-4"
                ></v-text-field>

                <v-switch
                  v-model="settings.advanced.enableTelemetry"
                  label="Enable Telemetry"
                  hint="Send anonymous usage data to help improve DockerForge"
                  persistent-hint
                  class="mt-4"
                ></v-switch>

                <v-btn
                  color="primary"
                  class="mt-4"
                  @click="saveAdvancedSettings"
                  :disabled="!advancedFormValid"
                >
                  Save Advanced Settings
                </v-btn>

                <v-btn
                  color="error"
                  class="mt-4 ml-2"
                  @click="showResetDialog"
                >
                  Reset All Settings
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs-items>
    </template>

    <!-- Reset Confirmation Dialog -->
    <v-dialog v-model="resetDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Reset All Settings</v-card-title>
        <v-card-text>
          Are you sure you want to reset all settings to their default values?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="resetDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="resetAllSettings">
            Reset
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="showSuccessSnackbar"
      :timeout="3000"
      color="success"
    >
      {{ successMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="showSuccessSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import UserSettings from './UserSettings.vue';
import ApiKeys from './ApiKeys.vue';

export default {
  name: 'Settings',
  components: {
    UserSettings,
    ApiKeys
  },
  data() {
    return {
      loading: true,
      error: null,
      activeTab: 0,
      dockerTab: 0,
      settings: {
        general: {
          darkMode: false,
          language: 'en',
          dateFormat: 'MM/DD/YYYY',
          refreshInterval: 30,
        },
        docker: {
          socketPath: '/var/run/docker.sock',
          useTLS: false,
          certPath: '',
          registryUrl: 'docker.io',
          pruneUnused: true,
          pruneSchedule: 'weekly',
        },
        security: {
          enableVulnerabilityScanning: true,
          scanSchedule: 'daily',
          vulnerabilitySeverity: 'high',
          enforceImageSigning: false,
          restrictPrivilegedContainers: true,
        },
        monitoring: {
          enableResourceMonitoring: true,
          collectionInterval: 60,
          retentionPeriod: 30,
          enableAnomalyDetection: true,
          cpuThreshold: 80,
          memoryThreshold: 80,
          diskThreshold: 85,
        },
        backup: {
          enableAutoBackup: true,
          backupSchedule: 'weekly',
          backupLocation: '/var/lib/dockerforge/backups',
          retentionCount: 5,
          compressBackups: true,
          includeVolumes: true,
        },
        notifications: {
          enableEmailNotifications: false,
          emailRecipients: '',
          smtpServer: '',
          smtpPort: 587,
          enableSlackNotifications: false,
          slackWebhookUrl: '',
          notificationEvents: ['error', 'security'],
        },
        advanced: {
          enableDebugMode: false,
          logLevel: 'info',
          apiRateLimit: 60,
          sessionTimeout: 30,
          enableTelemetry: true,
        },
      },
      generalFormValid: true,
      dockerFormValid: true,
      securityFormValid: true,
      monitoringFormValid: true,
      backupFormValid: true,
      notificationFormValid: true,
      advancedFormValid: true,
      resetDialog: false,
      showSuccessSnackbar: false,
      successMessage: '',

      // Options for select inputs
      // Docker daemon configuration
      daemonConfig: {
        registry: {
          registry_mirrors: [],
          insecure_registries: [],
          allow_nondistributable_artifacts: []
        },
        logging: {
          log_driver: 'json-file',
          log_opts: {}
        },
        storage: {
          storage_driver: '',
          storage_opts: [],
          data_root: '/var/lib/docker'
        },
        network: {
          dns: [],
          dns_opts: [],
          dns_search: [],
          bip: '',
          ipv6: false
        }
      },
      logOptKeys: {},

      // Docker daemon configuration status
      daemonConfigError: null,
      daemonConfigSuccess: null,
      registrySaving: false,
      loggingSaving: false,
      storageSaving: false,
      networkSaving: false,

      // Available drivers
      loggingDrivers: [],
      storageDrivers: [],

      // Form validation
      generalFormValid: true,
      dockerFormValid: true,
      securityFormValid: true,
      monitoringFormValid: true,
      backupFormValid: true,
      notificationFormValid: true,
      advancedFormValid: true,
      registryFormValid: true,
      loggingFormValid: true,
      storageFormValid: true,
      networkFormValid: true,

      languageOptions: [
        { text: 'English', value: 'en' },
        { text: 'Spanish', value: 'es' },
        { text: 'French', value: 'fr' },
        { text: 'German', value: 'de' },
        { text: 'Chinese', value: 'zh' },
        { text: 'Japanese', value: 'ja' },
      ],
      dateFormatOptions: [
        { text: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
        { text: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
        { text: 'YYYY-MM-DD', value: 'YYYY-MM-DD' },
      ],
      pruneScheduleOptions: [
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
        { text: 'Monthly', value: 'monthly' },
      ],
      scanScheduleOptions: [
        { text: 'Hourly', value: 'hourly' },
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
      ],
      severityOptions: [
        { text: 'Critical', value: 'critical' },
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      backupScheduleOptions: [
        { text: 'Daily', value: 'daily' },
        { text: 'Weekly', value: 'weekly' },
        { text: 'Monthly', value: 'monthly' },
      ],
      notificationEventOptions: [
        { text: 'Errors', value: 'error' },
        { text: 'Warnings', value: 'warning' },
        { text: 'Security Issues', value: 'security' },
        { text: 'Resource Alerts', value: 'resource' },
        { text: 'Container Events', value: 'container' },
        { text: 'Backup Events', value: 'backup' },
      ],
      logLevelOptions: [
        { text: 'Error', value: 'error' },
        { text: 'Warning', value: 'warning' },
        { text: 'Info', value: 'info' },
        { text: 'Debug', value: 'debug' },
        { text: 'Trace', value: 'trace' },
      ],
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchSettings();
    this.fetchDaemonConfig();
    this.fetchAvailableDrivers();

    // Initialize the dark mode setting from the store
    this.settings.general.darkMode = this.$store.getters.darkMode;
  },
  methods: {
    async fetchSettings() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/settings', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.settings = response.data;

        // Mock implementation - just use the default settings
        setTimeout(() => {
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load settings. Please try again.';
        this.loading = false;
      }
    },
    async saveGeneralSettings() {
      if (!this.$refs.generalForm.validate()) return;

      try {
        // Update the dark mode setting in the store
        this.$store.commit('SET_DARK_MODE', this.settings.general.darkMode);

        // In a real implementation, this would call the API
        // await axios.put('/api/settings/general', this.settings.general, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('General settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save general settings';
      }
    },
    async saveDockerSettings() {
      if (!this.$refs.dockerForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/docker', this.settings.docker, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Docker settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save Docker settings';
      }
    },
    async saveSecuritySettings() {
      if (!this.$refs.securityForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/security', this.settings.security, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Security settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save security settings';
      }
    },
    async saveMonitoringSettings() {
      if (!this.$refs.monitoringForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/monitoring', this.settings.monitoring, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Monitoring settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save monitoring settings';
      }
    },
    async saveBackupSettings() {
      if (!this.$refs.backupForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/backup', this.settings.backup, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Backup settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save backup settings';
      }
    },
    async saveNotificationSettings() {
      if (!this.$refs.notificationForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/notifications', this.settings.notifications, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Notification settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save notification settings';
      }
    },
    async saveAdvancedSettings() {
      if (!this.$refs.advancedForm.validate()) return;

      try {
        // In a real implementation, this would call the API
        // await axios.put('/api/settings/advanced', this.settings.advanced, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Advanced settings saved successfully');
      } catch (error) {
        this.error = 'Failed to save advanced settings';
      }
    },
    showResetDialog() {
      this.resetDialog = true;
    },
    async resetAllSettings() {
      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/settings/reset', {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation - reset to default values
        this.fetchSettings();
        this.resetDialog = false;
        this.showSuccessMessage('All settings have been reset to defaults');
      } catch (error) {
        this.error = 'Failed to reset settings';
        this.resetDialog = false;
      }
    },
    async testNotifications() {
      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/settings/notifications/test', {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });

        // Mock implementation
        this.showSuccessMessage('Test notification sent successfully');
      } catch (error) {
        this.error = 'Failed to send test notification';
      }
    },
    showSuccessMessage(message) {
      this.successMessage = message;
      this.showSuccessSnackbar = true;
    },

    // Docker Daemon Configuration Methods
    async fetchDaemonConfig() {
      try {
        // Call the API to get daemon configuration
        const response = await axios.get('/api/settings/daemon', {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        // Convert API response format to UI format
        this.daemonConfig = {
          registry: {
            registry_mirrors: response.data.registry['registry-mirrors'] || [],
            insecure_registries: response.data.registry['insecure-registries'] || [],
            allow_nondistributable_artifacts: response.data.registry['allow-nondistributable-artifacts'] || []
          },
          logging: {
            log_driver: response.data.logging['log-driver'] || 'json-file',
            log_opts: response.data.logging['log-opts'] || {}
          },
          storage: {
            storage_driver: response.data.storage['storage-driver'] || '',
            storage_opts: response.data.storage['storage-opts'] || [],
            data_root: response.data.storage['data-root'] || '/var/lib/docker'
          },
          network: {
            dns: response.data.network.dns || [],
            dns_opts: response.data.network['dns-opts'] || [],
            dns_search: response.data.network['dns-search'] || [],
            bip: response.data.network.bip || '',
            ipv6: response.data.network.ipv6 || false
          }
        };

        // Initialize log option keys
        this.logOptKeys = {};
        Object.keys(this.daemonConfig.logging.log_opts).forEach(key => {
          this.logOptKeys[key] = key;
        });
      } catch (error) {
        console.error('Error fetching daemon configuration:', error);
        this.daemonConfigError = 'Failed to load Docker daemon configuration: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      }
    },

    async fetchAvailableDrivers() {
      try {
        // Call the API to get available drivers
        const response = await axios.get('/api/settings/daemon/drivers', {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.loggingDrivers = response.data.logging_drivers;
        this.storageDrivers = response.data.storage_drivers;

        // Fallback to default drivers if API returns empty arrays
        if (!this.loggingDrivers || this.loggingDrivers.length === 0) {
          this.loggingDrivers = [
            { name: 'json-file', description: 'JSON File logging driver' },
            { name: 'syslog', description: 'Syslog logging driver' },
            { name: 'journald', description: 'Journald logging driver' },
            { name: 'gelf', description: 'GELF (Graylog) logging driver' },
            { name: 'fluentd', description: 'Fluentd logging driver' },
            { name: 'awslogs', description: 'Amazon CloudWatch Logs logging driver' },
            { name: 'splunk', description: 'Splunk logging driver' },
            { name: 'local', description: 'Local file logging driver' },
          ];
        }

        if (!this.storageDrivers || this.storageDrivers.length === 0) {
          this.storageDrivers = [
            { name: 'overlay2', description: 'OverlayFS v2 storage driver' },
            { name: 'aufs', description: 'AUFS storage driver' },
            { name: 'btrfs', description: 'Btrfs storage driver' },
            { name: 'devicemapper', description: 'Device Mapper storage driver' },
            { name: 'vfs', description: 'VFS storage driver' },
            { name: 'zfs', description: 'ZFS storage driver' },
          ];
        }
      } catch (error) {
        console.error('Error fetching available drivers:', error);
        this.daemonConfigError = 'Failed to load available drivers: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      }
    },

    getDriverDescription(driverName, type) {
      if (type === 'logging') {
        const driver = this.loggingDrivers.find(d => d.name === driverName);
        return driver ? driver.description : '';
      } else if (type === 'storage') {
        const driver = this.storageDrivers.find(d => d.name === driverName);
        return driver ? driver.description : '';
      }
      return '';
    },

    // Registry Configuration Methods
    addMirror() {
      this.daemonConfig.registry.registry_mirrors.push('');
    },

    removeMirror(index) {
      this.daemonConfig.registry.registry_mirrors.splice(index, 1);
    },

    addInsecureRegistry() {
      this.daemonConfig.registry.insecure_registries.push('');
    },

    removeInsecureRegistry(index) {
      this.daemonConfig.registry.insecure_registries.splice(index, 1);
    },

    async saveRegistryConfig() {
      if (!this.$refs.registryForm.validate()) return;

      // Show confirmation dialog for potentially disruptive changes
      if (!confirm('Updating registry configuration will restart the Docker daemon. This may temporarily disrupt running containers. Continue?')) {
        return;
      }

      this.registrySaving = true;
      this.daemonConfigError = null;
      this.daemonConfigSuccess = null;

      try {
        // Convert UI format to API format
        const registryConfig = {
          'registry-mirrors': this.daemonConfig.registry.registry_mirrors,
          'insecure-registries': this.daemonConfig.registry.insecure_registries,
          'allow-nondistributable-artifacts': this.daemonConfig.registry.allow_nondistributable_artifacts
        };

        // Call the API to update registry configuration
        const response = await axios.put('/api/settings/daemon/registry', registryConfig, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.daemonConfigSuccess = response.data.message || 'Registry configuration saved successfully. Docker daemon has been restarted.';
      } catch (error) {
        console.error('Error saving registry configuration:', error);
        this.daemonConfigError = 'Failed to save registry configuration: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      } finally {
        this.registrySaving = false;
      }
    },

    // Logging Configuration Methods
    addLogOpt() {
      const newKey = `new-option-${Object.keys(this.daemonConfig.logging.log_opts).length}`;
      this.$set(this.daemonConfig.logging.log_opts, newKey, '');
      this.$set(this.logOptKeys, newKey, newKey);
    },

    removeLogOpt(key) {
      this.$delete(this.daemonConfig.logging.log_opts, key);
      this.$delete(this.logOptKeys, key);
    },

    updateLogOptKey(oldKey, newKey) {
      if (oldKey === newKey) return;

      const value = this.daemonConfig.logging.log_opts[oldKey];
      this.$delete(this.daemonConfig.logging.log_opts, oldKey);
      this.$set(this.daemonConfig.logging.log_opts, newKey, value);
      this.$set(this.logOptKeys, newKey, newKey);
      this.$delete(this.logOptKeys, oldKey);
    },

    async saveLoggingConfig() {
      if (!this.$refs.loggingForm.validate()) return;

      // Show confirmation dialog for potentially disruptive changes
      if (!confirm('Updating logging configuration will restart the Docker daemon. This may temporarily disrupt running containers. Continue?')) {
        return;
      }

      this.loggingSaving = true;
      this.daemonConfigError = null;
      this.daemonConfigSuccess = null;

      try {
        // Convert UI format to API format
        const loggingConfig = {
          'log-driver': this.daemonConfig.logging.log_driver,
          'log-opts': this.daemonConfig.logging.log_opts
        };

        // Call the API to update logging configuration
        const response = await axios.put('/api/settings/daemon/logging', loggingConfig, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.daemonConfigSuccess = response.data.message || 'Logging configuration saved successfully. Docker daemon has been restarted.';
      } catch (error) {
        console.error('Error saving logging configuration:', error);
        this.daemonConfigError = 'Failed to save logging configuration: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      } finally {
        this.loggingSaving = false;
      }
    },

    // Storage Configuration Methods
    addStorageOpt() {
      this.daemonConfig.storage.storage_opts.push('');
    },

    removeStorageOpt(index) {
      this.daemonConfig.storage.storage_opts.splice(index, 1);
    },

    async saveStorageConfig() {
      if (!this.$refs.storageForm.validate()) return;

      // Show confirmation dialog for potentially disruptive changes
      if (!confirm('Updating storage configuration will restart the Docker daemon. This may temporarily disrupt running containers. Continue?')) {
        return;
      }

      this.storageSaving = true;
      this.daemonConfigError = null;
      this.daemonConfigSuccess = null;

      try {
        // Convert UI format to API format
        const storageConfig = {
          'storage-driver': this.daemonConfig.storage.storage_driver,
          'storage-opts': this.daemonConfig.storage.storage_opts,
          'data-root': this.daemonConfig.storage.data_root
        };

        // Call the API to update storage configuration
        const response = await axios.put('/api/settings/daemon/storage', storageConfig, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.daemonConfigSuccess = response.data.message || 'Storage configuration saved successfully. Docker daemon has been restarted.';
      } catch (error) {
        console.error('Error saving storage configuration:', error);
        this.daemonConfigError = 'Failed to save storage configuration: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      } finally {
        this.storageSaving = false;
      }
    },

    // Network Configuration Methods
    addDns() {
      this.daemonConfig.network.dns.push('');
    },

    removeDns(index) {
      this.daemonConfig.network.dns.splice(index, 1);
    },

    addDnsOpt() {
      this.daemonConfig.network.dns_opts.push('');
    },

    removeDnsOpt(index) {
      this.daemonConfig.network.dns_opts.splice(index, 1);
    },

    addDnsSearch() {
      this.daemonConfig.network.dns_search.push('');
    },

    removeDnsSearch(index) {
      this.daemonConfig.network.dns_search.splice(index, 1);
    },

    async saveNetworkConfig() {
      if (!this.$refs.networkForm.validate()) return;

      // Show confirmation dialog for potentially disruptive changes
      if (!confirm('Updating network configuration will restart the Docker daemon. This may temporarily disrupt running containers. Continue?')) {
        return;
      }

      this.networkSaving = true;
      this.daemonConfigError = null;
      this.daemonConfigSuccess = null;

      try {
        // Convert UI format to API format
        const networkConfig = {
          dns: this.daemonConfig.network.dns,
          'dns-opts': this.daemonConfig.network.dns_opts,
          'dns-search': this.daemonConfig.network.dns_search,
          bip: this.daemonConfig.network.bip,
          ipv6: this.daemonConfig.network.ipv6
        };

        // Call the API to update network configuration
        const response = await axios.put('/api/settings/daemon/network', networkConfig, {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        this.daemonConfigSuccess = response.data.message || 'Network configuration saved successfully. Docker daemon has been restarted.';
      } catch (error) {
        console.error('Error saving network configuration:', error);
        this.daemonConfigError = 'Failed to save network configuration: ' +
          (error.response?.data?.detail || error.message || 'Unknown error');
      } finally {
        this.networkSaving = false;
      }
    }
  }
};
</script>

<style scoped>
.settings {
  padding: 16px;
}
</style>
