<template>
  <div class="container-create">
    <h1 class="text-h4 mb-4">Create Container</h1>

    <!-- Stepper -->
    <v-stepper v-model="currentStep" class="mb-6">
      <v-stepper-header>
        <v-stepper-step :complete="currentStep > 1" step="1">
          Image Selection
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="currentStep > 2" step="2">
          Basic Settings
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="currentStep > 3" step="3">
          Network Settings
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="currentStep > 4" step="4">
          Storage Settings
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="currentStep > 5" step="5">
          Environment Variables
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="currentStep > 6" step="6">
          Resource Limits
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step step="7">
          Review & Create
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items>
        <!-- Step 1: Image Selection -->
        <v-stepper-content step="1">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-package-variant-closed</v-icon>
              Select an Image
            </v-card-title>
            <v-card-text>
              <v-tabs v-model="imageTab" background-color="transparent" grow>
                <v-tab>
                  <v-icon left>mdi-harddisk</v-icon>
                  Local Images
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-cloud-search</v-icon>
                  Docker Hub
                </v-tab>
              </v-tabs>

              <v-tabs-items v-model="imageTab">
                <!-- Local Images Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-text-field
                        v-model="localImageSearch"
                        label="Search local images"
                        prepend-icon="mdi-magnify"
                        clearable
                        @input="filterLocalImages"
                      ></v-text-field>

                      <v-data-table
                        :headers="localImageHeaders"
                        :items="filteredLocalImages"
                        :loading="loadingLocalImages"
                        :items-per-page="5"
                        :footer-props="{
                          'items-per-page-options': [5, 10, 15, 20],
                        }"
                        item-key="id"
                        @click:row="selectLocalImage"
                        class="elevation-1"
                      >
                        <template v-slot:item.tags="{ item }">
                          <v-chip
                            v-for="tag in item.tags"
                            :key="tag"
                            class="ma-1"
                            small
                            color="primary"
                            text-color="white"
                          >
                            {{ tag }}
                          </v-chip>
                        </template>
                        <template v-slot:item.size="{ item }">
                          {{ formatSize(item.size) }}
                        </template>
                        <template v-slot:item.created_at="{ item }">
                          {{ formatDate(item.created_at) }}
                        </template>
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            small
                            color="primary"
                            @click.stop="selectLocalImage(item)"
                          >
                            Select
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-tab-item>

                <!-- Docker Hub Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-form @submit.prevent="searchDockerHub">
                        <v-row>
                          <v-col cols="12" md="9">
                            <v-text-field
                              v-model="dockerHubSearch"
                              label="Search Docker Hub"
                              prepend-icon="mdi-magnify"
                              clearable
                              @keydown.enter="searchDockerHub"
                            ></v-text-field>
                          </v-col>
                          <v-col cols="12" md="3">
                            <v-btn
                              color="primary"
                              block
                              @click="searchDockerHub"
                              :loading="loadingDockerHub"
                            >
                              Search
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-form>

                      <div v-if="loadingDockerHub" class="d-flex justify-center my-5">
                        <v-progress-circular indeterminate color="primary"></v-progress-circular>
                      </div>

                      <div v-else-if="dockerHubResults.length > 0">
                        <v-list two-line>
                          <v-list-item
                            v-for="image in dockerHubResults"
                            :key="image.name"
                            @click="selectDockerHubImage(image)"
                          >
                            <v-list-item-avatar>
                              <v-img
                                v-if="image.logo_url"
                                :src="image.logo_url"
                                alt="Logo"
                              ></v-img>
                              <v-icon v-else>mdi-package-variant-closed</v-icon>
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title>{{ image.name }}</v-list-item-title>
                              <v-list-item-subtitle>
                                <v-chip
                                  v-if="image.is_official"
                                  x-small
                                  color="success"
                                  text-color="white"
                                  class="mr-2"
                                >
                                  Official
                                </v-chip>
                                <span>{{ image.description }}</span>
                              </v-list-item-subtitle>
                            </v-list-item-content>
                            <v-list-item-action>
                              <v-btn
                                small
                                color="primary"
                                @click.stop="selectDockerHubImage(image)"
                              >
                                Select
                              </v-btn>
                            </v-list-item-action>
                          </v-list-item>
                        </v-list>
                        <div class="text-center mt-4">
                          <v-pagination
                            v-model="dockerHubPage"
                            :length="dockerHubTotalPages"
                            @input="searchDockerHub"
                          ></v-pagination>
                        </div>
                      </div>

                      <div v-else-if="dockerHubSearched" class="text-center my-5">
                        <v-icon size="64" color="grey lighten-1">mdi-package-variant-closed</v-icon>
                        <p class="text-h6 mt-2">No images found</p>
                        <p class="text-body-1">Try a different search term</p>
                      </div>

                      <div v-else class="text-center my-5">
                        <v-icon size="64" color="grey lighten-1">mdi-cloud-search</v-icon>
                        <p class="text-h6 mt-2">Search Docker Hub</p>
                        <p class="text-body-1">Enter a search term to find images on Docker Hub</p>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </v-card-text>
          </v-card>

          <!-- Selected Image -->
          <v-card v-if="selectedImage" class="mb-4">
            <v-card-title>
              <v-icon left>mdi-check-circle</v-icon>
              Selected Image
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Image Name</v-list-item-subtitle>
                      <v-list-item-title class="text-h6">
                        {{ selectedImage.name }}
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Tag</v-list-item-subtitle>
                      <v-list-item-title class="text-h6">
                        <v-select
                          v-model="selectedTag"
                          :items="availableTags"
                          label="Select Tag"
                          outlined
                          dense
                        ></v-select>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-end">
            <v-btn
              color="primary"
              :disabled="!selectedImage"
              @click="currentStep = 2"
            >
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <!-- Placeholders for other steps -->
        <v-stepper-content step="2">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-cog</v-icon>
              Basic Settings
            </v-card-title>
            <v-card-text>
              <v-form ref="basicSettingsForm" v-model="basicSettingsValid" lazy-validation>
                <v-row>
                  <!-- Container Name -->
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="containerData.name"
                      label="Container Name"
                      :rules="[v => !!v || 'Container name is required']"
                      required
                      hint="A unique name for your container"
                      persistent-hint
                      outlined
                      :counter="64"
                    ></v-text-field>
                  </v-col>

                  <!-- Restart Policy -->
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="containerData.restart_policy"
                      :items="restartPolicyOptions"
                      label="Restart Policy"
                      item-text="text"
                      item-value="value"
                      hint="Defines when the container should be automatically restarted"
                      persistent-hint
                      outlined
                    ></v-select>
                  </v-col>

                  <!-- Command -->
                  <v-col cols="12">
                    <v-text-field
                      v-model="containerData.command"
                      label="Command"
                      hint="Optional: Override the default command (CMD) in the container"
                      persistent-hint
                      outlined
                    ></v-text-field>
                  </v-col>

                  <!-- Entrypoint -->
                  <v-col cols="12">
                    <v-text-field
                      v-model="containerData.entrypoint"
                      label="Entrypoint"
                      hint="Optional: Override the default entrypoint (ENTRYPOINT) in the container"
                      persistent-hint
                      outlined
                    ></v-text-field>
                  </v-col>

                  <!-- Labels -->
                  <v-col cols="12">
                    <v-expansion-panels flat>
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-label</v-icon>
                            Container Labels
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <v-btn color="primary" text @click="addLabel" class="mb-2">
                            <v-icon left>mdi-plus</v-icon>
                            Add Label
                          </v-btn>

                          <div v-for="(label, index) in containerLabels" :key="index" class="mb-2">
                            <v-row>
                              <v-col cols="12" sm="5">
                                <v-text-field
                                  v-model="label.key"
                                  label="Key"
                                  dense
                                  outlined
                                ></v-text-field>
                              </v-col>
                              <v-col cols="12" sm="5">
                                <v-text-field
                                  v-model="label.value"
                                  label="Value"
                                  dense
                                  outlined
                                ></v-text-field>
                              </v-col>
                              <v-col cols="12" sm="2" class="d-flex align-center">
                                <v-btn icon color="error" @click="removeLabel(index)">
                                  <v-icon>mdi-delete</v-icon>
                                </v-btn>
                              </v-col>
                            </v-row>
                          </div>

                          <div v-if="containerLabels.length === 0" class="text-center grey--text my-3">
                            No labels added yet
                          </div>
                        </v-expansion-panel-content>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Image Summary -->
          <v-card class="mb-4" v-if="selectedImage">
            <v-card-title>
              <v-icon left>mdi-information</v-icon>
              Selected Image
            </v-card-title>
            <v-card-text>
              <v-chip color="primary" text-color="white" class="mr-2">
                {{ selectedImage.name }}:{{ selectedTag }}
              </v-chip>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 1">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn
              color="primary"
              @click="validateAndContinue(3)"
              :disabled="!basicSettingsValid"
            >
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="3">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-lan</v-icon>
              Network Settings
            </v-card-title>
            <v-card-text>
              <v-form ref="networkSettingsForm" v-model="networkSettingsValid" lazy-validation>
                <v-row>
                  <!-- Network Selection -->
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="containerData.network"
                      :items="availableNetworks"
                      label="Network"
                      item-text="name"
                      item-value="name"
                      hint="Select a Docker network for this container"
                      persistent-hint
                      outlined
                    >
                      <template v-slot:selection="{ item }">
                        <v-chip small color="primary" text-color="white" class="mr-2">
                          {{ item.name }}
                        </v-chip>
                        <span>{{ item.driver }} driver</span>
                      </template>
                      <template v-slot:item="{ item }">
                        <v-list-item-content>
                          <v-list-item-title>
                            <v-chip small color="primary" text-color="white" class="mr-2">
                              {{ item.name }}
                            </v-chip>
                            {{ item.driver }} driver
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            {{ item.scope }} scope
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </template>
                    </v-select>
                  </v-col>

                  <!-- Hostname -->
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="containerData.hostname"
                      label="Hostname"
                      hint="Container hostname (optional)"
                      persistent-hint
                      outlined
                    ></v-text-field>
                  </v-col>

                  <!-- DNS Settings -->
                  <v-col cols="12">
                    <v-expansion-panels flat>
                      <v-expansion-panel>
                        <v-expansion-panel-header>
                          <div class="d-flex align-center">
                            <v-icon left>mdi-dns</v-icon>
                            DNS Settings
                          </div>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                          <!-- DNS Servers -->
                          <div class="mb-3">
                            <div class="d-flex align-center mb-2">
                              <h3 class="text-subtitle-1 font-weight-bold">DNS Servers</h3>
                              <v-spacer></v-spacer>
                              <v-btn color="primary" text @click="addDnsServer">
                                <v-icon left>mdi-plus</v-icon>
                                Add DNS Server
                              </v-btn>
                            </div>

                            <div v-for="(server, index) in dnsServers" :key="'dns-server-'+index" class="mb-2">
                              <v-row>
                                <v-col cols="12" sm="10">
                                  <v-text-field
                                    v-model="server.address"
                                    label="DNS Server Address"
                                    :rules="[v => !!v || 'DNS server address is required']"
                                    required
                                    outlined
                                    dense
                                  ></v-text-field>
                                </v-col>
                                <v-col cols="12" sm="2" class="d-flex align-center">
                                  <v-btn icon color="error" @click="removeDnsServer(index)">
                                    <v-icon>mdi-delete</v-icon>
                                  </v-btn>
                                </v-col>
                              </v-row>
                            </div>

                            <div v-if="dnsServers.length === 0" class="text-center grey--text my-3">
                              No DNS servers added yet
                            </div>
                          </div>

                          <!-- DNS Search Domains -->
                          <div class="mb-3">
                            <div class="d-flex align-center mb-2">
                              <h3 class="text-subtitle-1 font-weight-bold">DNS Search Domains</h3>
                              <v-spacer></v-spacer>
                              <v-btn color="primary" text @click="addDnsSearchDomain">
                                <v-icon left>mdi-plus</v-icon>
                                Add Search Domain
                              </v-btn>
                            </div>

                            <div v-for="(domain, index) in dnsSearchDomains" :key="'dns-domain-'+index" class="mb-2">
                              <v-row>
                                <v-col cols="12" sm="10">
                                  <v-text-field
                                    v-model="domain.domain"
                                    label="Search Domain"
                                    :rules="[v => !!v || 'Search domain is required']"
                                    required
                                    outlined
                                    dense
                                  ></v-text-field>
                                </v-col>
                                <v-col cols="12" sm="2" class="d-flex align-center">
                                  <v-btn icon color="error" @click="removeDnsSearchDomain(index)">
                                    <v-icon>mdi-delete</v-icon>
                                  </v-btn>
                                </v-col>
                              </v-row>
                            </div>

                            <div v-if="dnsSearchDomains.length === 0" class="text-center grey--text my-3">
                              No search domains added yet
                            </div>
                          </div>
                        </v-expansion-panel-content>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </v-col>

                  <!-- Port Mappings -->
                  <v-col cols="12">
                    <div class="d-flex align-center mb-2">
                      <h3 class="text-subtitle-1 font-weight-bold">Port Mappings</h3>
                      <v-spacer></v-spacer>
                      <v-btn color="primary" text @click="addPortMapping">
                        <v-icon left>mdi-plus</v-icon>
                        Add Port Mapping
                      </v-btn>
                    </div>

                    <div v-for="(port, index) in portMappings" :key="index" class="mb-3 pa-3 grey lighten-4 rounded">
                      <div class="d-flex align-center mb-2">
                        <span class="text-subtitle-2">Port Mapping #{{ index + 1 }}</span>
                        <v-spacer></v-spacer>
                        <v-btn icon color="error" @click="removePortMapping(index)">
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </div>
                      <v-row>
                        <v-col cols="12" sm="3">
                          <v-text-field
                            v-model.number="port.host_port"
                            label="Host Port"
                            type="number"
                            min="1"
                            max="65535"
                            :rules="[v => !!v || 'Host port is required', v => (v > 0 && v < 65536) || 'Port must be between 1 and 65535']"
                            required
                            outlined
                            dense
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" sm="3">
                          <v-text-field
                            v-model.number="port.container_port"
                            label="Container Port"
                            type="number"
                            min="1"
                            max="65535"
                            :rules="[v => !!v || 'Container port is required', v => (v > 0 && v < 65536) || 'Port must be between 1 and 65535']"
                            required
                            outlined
                            dense
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" sm="3">
                          <v-select
                            v-model="port.protocol"
                            :items="['tcp', 'udp']"
                            label="Protocol"
                            outlined
                            dense
                          ></v-select>
                        </v-col>
                        <v-col cols="12" sm="3">
                          <v-text-field
                            v-model="port.host_ip"
                            label="Host IP (Optional)"
                            hint="Leave empty for all interfaces"
                            persistent-hint
                            outlined
                            dense
                          ></v-text-field>
                        </v-col>
                      </v-row>
                    </div>

                    <div v-if="portMappings.length === 0" class="text-center grey--text my-5">
                      <v-icon large color="grey lighten-1">mdi-lan-disconnect</v-icon>
                      <p class="mt-2">No port mappings defined</p>
                      <p class="text-caption">Add port mappings to expose container ports to the host</p>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Image and Basic Settings Summary -->
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-information</v-icon>
              Configuration Summary
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Image</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white">
                          {{ selectedImage.name }}:{{ selectedTag }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Container Name</v-list-item-subtitle>
                      <v-list-item-title>{{ containerData.name }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 2">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn
              color="primary"
              @click="validateAndContinueNetwork(4)"
              :disabled="!networkSettingsValid"
            >
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="4">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-database</v-icon>
              Storage Settings
            </v-card-title>
            <v-card-text>
              <v-form ref="storageSettingsForm" v-model="storageSettingsValid" lazy-validation>
                <!-- Volume Mappings -->
                <div class="d-flex align-center mb-2">
                  <h3 class="text-subtitle-1 font-weight-bold">Volume Mappings</h3>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" text @click="addVolumeMapping">
                    <v-icon left>mdi-plus</v-icon>
                    Add Volume Mapping
                  </v-btn>
                </div>

                <div v-for="(volume, index) in volumeMappings" :key="index" class="mb-3 pa-3 grey lighten-4 rounded">
                  <div class="d-flex align-center mb-2">
                    <span class="text-subtitle-2">Volume Mapping #{{ index + 1 }}</span>
                    <v-spacer></v-spacer>
                    <v-btn icon color="error" @click="removeVolumeMapping(index)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </div>
                  <v-row>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="volume.type"
                        :items="volumeTypeOptions"
                        label="Type"
                        item-text="text"
                        item-value="value"
                        outlined
                        dense
                      ></v-select>
                    </v-col>
                    <v-col cols="12" sm="8" v-if="volume.type === 'volume'">
                      <v-autocomplete
                        v-model="volume.host_path"
                        :items="availableVolumes"
                        label="Docker Volume"
                        item-text="name"
                        item-value="name"
                        :rules="[v => !!v || 'Volume name is required']"
                        required
                        outlined
                        dense
                      >
                        <template v-slot:selection="{ item }">
                          <v-chip small color="primary" text-color="white" class="mr-2">
                            {{ item.name }}
                          </v-chip>
                          <span>{{ item.driver }} driver</span>
                        </template>
                        <template v-slot:item="{ item }">
                          <v-list-item-content>
                            <v-list-item-title>
                              <v-chip small color="primary" text-color="white" class="mr-2">
                                {{ item.name }}
                              </v-chip>
                              {{ item.driver }} driver
                            </v-list-item-title>
                            <v-list-item-subtitle>
                              {{ item.mountpoint }}
                            </v-list-item-subtitle>
                          </v-list-item-content>
                        </template>
                      </v-autocomplete>
                    </v-col>
                    <v-col cols="12" sm="8" v-else-if="volume.type === 'bind'">
                      <v-text-field
                        v-model="volume.host_path"
                        label="Host Path"
                        :rules="[v => !!v || 'Host path is required']"
                        required
                        hint="Absolute path on the host machine"
                        persistent-hint
                        outlined
                        dense
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="8">
                      <v-text-field
                        v-model="volume.container_path"
                        label="Container Path"
                        :rules="[v => !!v || 'Container path is required']"
                        required
                        hint="Absolute path inside the container"
                        persistent-hint
                        outlined
                        dense
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="volume.mode"
                        :items="volumeModeOptions"
                        label="Access Mode"
                        item-text="text"
                        item-value="value"
                        outlined
                        dense
                      ></v-select>
                    </v-col>
                  </v-row>
                </div>

                <div v-if="volumeMappings.length === 0" class="text-center grey--text my-5">
                  <v-icon large color="grey lighten-1">mdi-database-off</v-icon>
                  <p class="mt-2">No volume mappings defined</p>
                  <p class="text-caption">Add volume mappings to persist data or share files with the container</p>
                </div>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Configuration Summary -->
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-information</v-icon>
              Configuration Summary
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Image</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white">
                          {{ selectedImage.name }}:{{ selectedTag }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Network</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white" v-if="containerData.network">
                          {{ containerData.network }}
                        </v-chip>
                        <span v-else>Default network</span>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
              <v-row v-if="portMappings.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Port Mappings</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(port, index) in portMappings"
                          :key="index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ port.host_port }}:{{ port.container_port }}/{{ port.protocol }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 3">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn
              color="primary"
              @click="validateAndContinueStorage(5)"
              :disabled="!storageSettingsValid"
            >
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="5">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-code-braces</v-icon>
              Environment Variables
            </v-card-title>
            <v-card-text>
              <v-form ref="envVarsForm" v-model="envVarsValid" lazy-validation>
                <div class="d-flex align-center mb-2">
                  <h3 class="text-subtitle-1 font-weight-bold">Environment Variables</h3>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" text @click="addEnvVar">
                    <v-icon left>mdi-plus</v-icon>
                    Add Variable
                  </v-btn>
                </div>

                <div v-for="(envVar, index) in environmentVariables" :key="index" class="mb-3 pa-3 grey lighten-4 rounded">
                  <div class="d-flex align-center mb-2">
                    <span class="text-subtitle-2">Variable #{{ index + 1 }}</span>
                    <v-spacer></v-spacer>
                    <v-btn icon color="error" @click="removeEnvVar(index)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </div>
                  <v-row>
                    <v-col cols="12" sm="5">
                      <v-text-field
                        v-model="envVar.key"
                        label="Key"
                        :rules="[v => !!v || 'Key is required']"
                        required
                        outlined
                        dense
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="7">
                      <v-text-field
                        v-model="envVar.value"
                        label="Value"
                        outlined
                        dense
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </div>

                <div v-if="environmentVariables.length === 0" class="text-center grey--text my-5">
                  <v-icon large color="grey lighten-1">mdi-code-braces</v-icon>
                  <p class="mt-2">No environment variables defined</p>
                  <p class="text-caption">Add environment variables to configure your container</p>
                </div>

                <v-divider class="my-5"></v-divider>

                <div class="d-flex align-center mb-2">
                  <h3 class="text-subtitle-1 font-weight-bold">Environment Files</h3>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" text @click="addEnvFile">
                    <v-icon left>mdi-plus</v-icon>
                    Add File
                  </v-btn>
                </div>

                <div v-for="(envFile, index) in environmentFiles" :key="index" class="mb-3 pa-3 grey lighten-4 rounded">
                  <div class="d-flex align-center mb-2">
                    <span class="text-subtitle-2">Environment File #{{ index + 1 }}</span>
                    <v-spacer></v-spacer>
                    <v-btn icon color="error" @click="removeEnvFile(index)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </div>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field
                        v-model="envFile.path"
                        label="File Path"
                        :rules="[v => !!v || 'File path is required']"
                        required
                        hint="Absolute path to an environment file on the host"
                        persistent-hint
                        outlined
                        dense
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </div>

                <div v-if="environmentFiles.length === 0" class="text-center grey--text my-5">
                  <v-icon large color="grey lighten-1">mdi-file-document</v-icon>
                  <p class="mt-2">No environment files defined</p>
                  <p class="text-caption">Add environment files to load variables from .env files</p>
                </div>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Configuration Summary -->
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-information</v-icon>
              Configuration Summary
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Image</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white">
                          {{ selectedImage.name }}:{{ selectedTag }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Container Name</v-list-item-subtitle>
                      <v-list-item-title>{{ containerData.name }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- Show volume mappings if any -->
              <v-row v-if="volumeMappings.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Volume Mappings</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(volume, index) in volumeMappings"
                          :key="index"
                          small
                          class="ma-1"
                          color="success"
                          text-color="white"
                        >
                          {{ volume.host_path }}:{{ volume.container_path }}:{{ volume.mode }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 4">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn
              color="primary"
              @click="validateAndContinueEnvVars(6)"
              :disabled="!envVarsValid"
            >
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="6">
          <v-card class="mb-4">
            <v-card-title>Resource Limits</v-card-title>
            <v-card-text>
              <p>Resource limits content will go here</p>
            </v-card-text>
          </v-card>
          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 5">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn color="primary" @click="currentStep = 7">
              Continue
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="7">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-check-circle</v-icon>
              Review & Create
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Image</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white">
                          {{ selectedImage.name }}:{{ selectedTag }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Container Name</v-list-item-subtitle>
                      <v-list-item-title>{{ containerData.name }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <v-divider class="my-3"></v-divider>

              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Network</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip color="primary" text-color="white" v-if="containerData.network">
                          {{ containerData.network }}
                        </v-chip>
                        <span v-else>Default network</span>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Hostname</v-list-item-subtitle>
                      <v-list-item-title>
                        <span v-if="containerData.hostname">{{ containerData.hostname }}</span>
                        <span v-else class="grey--text">Default hostname</span>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- DNS Settings -->
              <v-row v-if="containerData.dns && containerData.dns.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>DNS Servers</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(server, index) in containerData.dns"
                          :key="'dns-'+index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ server }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <v-row v-if="containerData.dns_search && containerData.dns_search.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>DNS Search Domains</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(domain, index) in containerData.dns_search"
                          :key="'dns-search-'+index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ domain }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- Port Mappings -->
              <v-row v-if="portMappings.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Port Mappings</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(port, index) in portMappings"
                          :key="'port-'+index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ port.host_port }}:{{ port.container_port }}/{{ port.protocol }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- Volume Mappings -->
              <v-row v-if="volumeMappings.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Volume Mappings</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(volume, index) in volumeMappings"
                          :key="'volume-'+index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ volume.host_path }}:{{ volume.container_path }}:{{ volume.mode }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- Environment Variables -->
              <v-row v-if="environmentVariables.length > 0">
                <v-col cols="12">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Environment Variables</v-list-item-subtitle>
                      <v-list-item-title>
                        <v-chip
                          v-for="(envVar, index) in environmentVariables"
                          :key="'env-'+index"
                          small
                          class="ma-1"
                          color="info"
                          text-color="white"
                        >
                          {{ envVar.key }}={{ envVar.value }}
                        </v-chip>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>

              <!-- Resource Limits -->
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>CPU Limit</v-list-item-subtitle>
                      <v-list-item-title>
                        <span v-if="containerData.cpu_limit">{{ containerData.cpu_limit }} cores</span>
                        <span v-else class="grey--text">No limit</span>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Memory Limit</v-list-item-subtitle>
                      <v-list-item-title>
                        <span v-if="containerData.memory_limit">{{ formatSize(containerData.memory_limit) }}</span>
                        <span v-else class="grey--text">No limit</span>
                      </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Creation Progress -->
          <v-card v-if="isCreating" class="mb-4">
            <v-card-text>
              <div class="d-flex align-center">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  class="mr-3"
                ></v-progress-circular>
                <span>{{ creationProgress || 'Creating container...' }}</span>
              </div>
            </v-card-text>
          </v-card>

          <div class="d-flex justify-space-between">
            <v-btn @click="currentStep = 6" :disabled="isCreating">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn
              color="success"
              @click="createContainer"
              :loading="isCreating"
              :disabled="isCreating"
            >
              <v-icon left>mdi-check</v-icon>
              Create Container
            </v-btn>
          </div>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'ContainerCreate',

  data() {
    return {
      currentStep: 1,
      imageTab: 0,

      // Local images
      localImageSearch: '',
      localImageHeaders: [
        { text: 'Tags', value: 'tags' },
        { text: 'Size', value: 'size' },
        { text: 'Created', value: 'created_at' },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      filteredLocalImages: [],
      loadingLocalImages: false,

      // Docker Hub
      dockerHubSearch: '',
      dockerHubResults: [],
      dockerHubPage: 1,
      dockerHubTotalPages: 1,
      loadingDockerHub: false,
      dockerHubSearched: false,

      // Selected image
      selectedImage: null,
      selectedTag: 'latest',
      availableTags: ['latest'],

      // Container data
      containerData: {
        name: '',
        image: '',
        command: '',
        entrypoint: '',
        environment: {},
        ports: [],
        volumes: [],
        network: '',
        restart_policy: 'no',
        labels: {},
        hostname: '',
        dns: [],
        dns_search: [],
      },

      // Basic Settings
      basicSettingsValid: true,
      restartPolicyOptions: [
        { text: 'No', value: 'no' },
        { text: 'Always', value: 'always' },
        { text: 'On Failure', value: 'on-failure' },
        { text: 'Unless Stopped', value: 'unless-stopped' },
      ],
      containerLabels: [],

      // Network Settings
      networkSettingsValid: true,
      availableNetworks: [
        { name: 'bridge', driver: 'bridge', scope: 'local' },
        { name: 'host', driver: 'host', scope: 'local' },
        { name: 'none', driver: 'null', scope: 'local' },
        { name: 'custom-network', driver: 'bridge', scope: 'local' },
      ],
      portMappings: [],
      dnsServers: [],
      dnsSearchDomains: [],

      // Storage Settings
      storageSettingsValid: true,
      volumeMappings: [],
      volumeTypeOptions: [
        { text: 'Docker Volume', value: 'volume' },
        { text: 'Bind Mount', value: 'bind' },
      ],
      volumeModeOptions: [
        { text: 'Read/Write', value: 'rw' },
        { text: 'Read Only', value: 'ro' },
      ],
      availableVolumes: [
        { name: 'data-volume', driver: 'local', mountpoint: '/var/lib/docker/volumes/data-volume/_data' },
        { name: 'postgres-data', driver: 'local', mountpoint: '/var/lib/docker/volumes/postgres-data/_data' },
        { name: 'redis-data', driver: 'local', mountpoint: '/var/lib/docker/volumes/redis-data/_data' },
        { name: 'nginx-config', driver: 'local', mountpoint: '/var/lib/docker/volumes/nginx-config/_data' },
      ],

      // Environment Variables Settings
      envVarsValid: true,
      environmentVariables: [],
      environmentFiles: [],

      // Container Creation Progress
      isCreating: false,
      creationProgress: '',

      // Notifications
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },

  computed: {
    ...mapState('images', ['images']),
  },

  created() {
    this.fetchLocalImages();
    this.fetchNetworks();
    this.fetchVolumes();
  },

  methods: {
    ...mapActions({
      fetchImages: 'images/getImages',
      searchImages: 'images/searchDockerHub',
      getImageTags: 'images/getImageTags',
      pullImage: 'images/pullImage',
      createContainer: 'containers/createContainer',
    }),

    async fetchLocalImages() {
      this.loadingLocalImages = true;
      try {
        await this.fetchImages();
        this.filterLocalImages();
      } catch (error) {
        this.showError(`Failed to fetch local images: ${error.message}`);
      } finally {
        this.loadingLocalImages = false;
      }
    },

    filterLocalImages() {
      if (!this.localImageSearch) {
        this.filteredLocalImages = [...this.images];
        return;
      }

      const search = this.localImageSearch.toLowerCase();
      this.filteredLocalImages = this.images.filter(image => {
        // Check if any tag contains the search term
        return image.tags.some(tag => tag.toLowerCase().includes(search));
      });
    },

    selectLocalImage(image) {
      this.selectedImage = {
        id: image.id,
        name: image.tags[0]?.split(':')[0] || 'unnamed',
        tag: image.tags[0]?.split(':')[1] || 'latest',
        size: image.size,
        created_at: image.created_at,
        source: 'local',
      };

      // Extract available tags for this image
      this.availableTags = image.tags.map(tag => {
        const parts = tag.split(':');
        return parts.length > 1 ? parts[1] : 'latest';
      });

      if (this.availableTags.length > 0) {
        this.selectedTag = this.availableTags[0];
      } else {
        this.availableTags = ['latest'];
        this.selectedTag = 'latest';
      }

      // Update container data
      this.containerData.image = `${this.selectedImage.name}:${this.selectedTag}`;
    },

    async searchDockerHub() {
      if (!this.dockerHubSearch) {
        return;
      }

      this.loadingDockerHub = true;
      this.dockerHubSearched = true;

      try {
        const response = await this.searchImages({
          query: this.dockerHubSearch,
          page: this.dockerHubPage,
          pageSize: 10,
        });

        this.dockerHubResults = response.results;
        this.dockerHubTotalPages = response.total_pages;
      } catch (error) {
        this.showError(`Failed to search Docker Hub: ${error.message}`);
        this.dockerHubResults = [];
      } finally {
        this.loadingDockerHub = false;
      }
    },

    selectDockerHubImage(image) {
      this.selectedImage = {
        id: null,
        name: image.name,
        tag: 'latest',
        size: null,
        created_at: null,
        source: 'dockerhub',
        description: image.description,
        is_official: image.is_official,
      };

      // For Docker Hub images, we need to fetch available tags
      this.fetchImageTags(image.name);

      // Update container data
      this.containerData.image = `${this.selectedImage.name}:${this.selectedTag}`;
    },

    async fetchImageTags(imageName) {
      try {
        const tags = await this.getImageTags(imageName);
        this.availableTags = tags;
        this.selectedTag = 'latest';
      } catch (error) {
        this.showError(`Failed to fetch image tags: ${error.message}`);
        this.availableTags = ['latest'];
        this.selectedTag = 'latest';
      }
    },

    // Basic Settings methods
    addLabel() {
      this.containerLabels.push({ key: '', value: '' });
    },

    removeLabel(index) {
      this.containerLabels.splice(index, 1);
    },

    updateLabels() {
      // Convert containerLabels array to object for containerData.labels
      const labels = {};
      this.containerLabels.forEach(label => {
        if (label.key && label.key.trim() !== '') {
          labels[label.key] = label.value || '';
        }
      });
      this.containerData.labels = labels;
    },

    validateAndContinue(nextStep) {
      if (this.$refs.basicSettingsForm.validate()) {
        // Update labels before continuing
        this.updateLabels();

        // Generate a default name if none is provided
        if (!this.containerData.name) {
          const baseName = this.selectedImage.name.replace(/[^a-zA-Z0-9]/g, '-');
          this.containerData.name = `${baseName}-${Math.floor(Math.random() * 10000)}`;
        }

        this.currentStep = nextStep;
      }
    },

    // Network Settings methods
    addPortMapping() {
      this.portMappings.push({
        host_port: null,
        container_port: null,
        protocol: 'tcp',
        host_ip: '',
      });
    },

    removePortMapping(index) {
      this.portMappings.splice(index, 1);
    },

    // DNS Settings methods
    addDnsServer() {
      this.dnsServers.push({ address: '' });
    },

    removeDnsServer(index) {
      this.dnsServers.splice(index, 1);
    },

    addDnsSearchDomain() {
      this.dnsSearchDomains.push({ domain: '' });
    },

    removeDnsSearchDomain(index) {
      this.dnsSearchDomains.splice(index, 1);
    },

    updateDnsSettings() {
      // Convert dnsServers array to string array for containerData.dns
      this.containerData.dns = this.dnsServers
        .filter(server => server.address && server.address.trim() !== '')
        .map(server => server.address.trim());

      // Convert dnsSearchDomains array to string array for containerData.dns_search
      this.containerData.dns_search = this.dnsSearchDomains
        .filter(domain => domain.domain && domain.domain.trim() !== '')
        .map(domain => domain.domain.trim());
    },

    validateAndContinueNetwork(nextStep) {
      if (this.$refs.networkSettingsForm.validate()) {
        // Update port mappings in containerData
        this.containerData.ports = [...this.portMappings];

        // Update DNS settings
        this.updateDnsSettings();

        this.currentStep = nextStep;
      }
    },

    fetchNetworks() {
      // In a real implementation, this would call the API to get available networks
      // For now, we'll use the mock data in availableNetworks
      // If the API endpoint is implemented later, uncomment the following code:
      /*
      try {
        const response = await axios.get('/api/networks');
        this.availableNetworks = response.data;
      } catch (error) {
        this.showError(`Failed to fetch networks: ${error.message}`);
      }
      */
    },

    // Storage Settings methods
    addVolumeMapping() {
      this.volumeMappings.push({
        type: 'volume',
        host_path: '',
        container_path: '',
        mode: 'rw',
      });
    },

    removeVolumeMapping(index) {
      this.volumeMappings.splice(index, 1);
    },

    validateAndContinueStorage(nextStep) {
      if (this.$refs.storageSettingsForm.validate()) {
        // Update volume mappings in containerData
        this.containerData.volumes = [...this.volumeMappings];

        this.currentStep = nextStep;
      }
    },

    fetchVolumes() {
      // In a real implementation, this would call the API to get available volumes
      // For now, we'll use the mock data in availableVolumes
      // If the API endpoint is implemented later, uncomment the following code:
      /*
      try {
        const response = await axios.get('/api/volumes');
        this.availableVolumes = response.data;
      } catch (error) {
        this.showError(`Failed to fetch volumes: ${error.message}`);
      }
      */
    },

    // Environment Variables methods
    addEnvVar() {
      this.environmentVariables.push({
        key: '',
        value: '',
      });
    },

    removeEnvVar(index) {
      this.environmentVariables.splice(index, 1);
    },

    addEnvFile() {
      this.environmentFiles.push({
        path: '',
      });
    },

    removeEnvFile(index) {
      this.environmentFiles.splice(index, 1);
    },

    updateEnvironmentVariables() {
      // Convert environmentVariables array to object for containerData.environment
      const environment = {};
      this.environmentVariables.forEach(envVar => {
        if (envVar.key && envVar.key.trim() !== '') {
          environment[envVar.key] = envVar.value || '';
        }
      });
      this.containerData.environment = environment;
    },

    validateAndContinueEnvVars(nextStep) {
      if (this.$refs.envVarsForm.validate()) {
        // Update environment variables before continuing
        this.updateEnvironmentVariables();

        // Update environment files (in a real implementation, these would be processed)
        // For now, we'll just store them in a custom property
        this.containerData.env_files = this.environmentFiles.map(file => file.path);

        this.currentStep = nextStep;
      }
    },

    async createContainer() {
      try {
        // Set loading state
        this.isCreating = true;

        // Update container data with selected image
        this.containerData.image = `${this.selectedImage.name}:${this.selectedTag}`;

        // Update labels
        this.updateLabels();

        // Update port mappings
        this.containerData.ports = [...this.portMappings];

        // Update volume mappings
        this.containerData.volumes = [...this.volumeMappings];

        // Update DNS settings
        this.updateDnsSettings();

        // Update environment variables
        this.updateEnvironmentVariables();

        // If the image is from Docker Hub and not pulled yet, pull it first
        if (this.selectedImage.source === 'dockerhub' && !this.selectedImage.id) {
          this.creationProgress = 'Pulling image...';
          await this.pullImage({
            name: this.selectedImage.name,
            tag: this.selectedTag,
          });
        }

        // Create container
        this.creationProgress = 'Creating container...';
        const container = await this.createContainer(this.containerData);

        // Show success message
        this.showSuccess(`Container ${container.name} created successfully`);

        // Navigate to container detail page
        this.$router.push(`/containers/${container.id}`);
      } catch (error) {
        this.showError(`Failed to create container: ${error.message}`);
      } finally {
        this.isCreating = false;
        this.creationProgress = '';
      }
    },

    formatSize(bytes) {
      if (bytes === 0) return '0 B';

      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));

      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
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

  watch: {
    selectedTag(newTag) {
      if (this.selectedImage) {
        this.containerData.image = `${this.selectedImage.name}:${newTag}`;
      }
    },
    'containerData.labels': {
      immediate: true,
      handler(newLabels) {
        // Initialize containerLabels array from containerData.labels object
        if (newLabels && Object.keys(newLabels).length > 0 && this.containerLabels.length === 0) {
          this.containerLabels = Object.entries(newLabels).map(([key, value]) => ({ key, value }));
        }
      },
    },
    'containerData.ports': {
      immediate: true,
      handler(newPorts) {
        // Initialize portMappings array from containerData.ports array
        if (newPorts && newPorts.length > 0 && this.portMappings.length === 0) {
          this.portMappings = [...newPorts];
        }
      },
    },
    'containerData.volumes': {
      immediate: true,
      handler(newVolumes) {
        // Initialize volumeMappings array from containerData.volumes array
        if (newVolumes && newVolumes.length > 0 && this.volumeMappings.length === 0) {
          this.volumeMappings = [...newVolumes];
        }
      },
    },
    'containerData.environment': {
      immediate: true,
      handler(newEnvironment) {
        // Initialize environmentVariables array from containerData.environment object
        if (newEnvironment && Object.keys(newEnvironment).length > 0 && this.environmentVariables.length === 0) {
          this.environmentVariables = Object.entries(newEnvironment).map(([key, value]) => ({ key, value }));
        }
      },
    },
  },
};
</script>

<style scoped>
.container-create {
  padding: 16px;
}
</style>
