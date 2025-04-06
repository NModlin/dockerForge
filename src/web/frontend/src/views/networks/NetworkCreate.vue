<template>
  <div class="network-create">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-plus-network</v-icon>
              Create Network
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Networks
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-form ref="form" v-model="valid" @submit.prevent="createNetwork">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-information</v-icon>
                        Basic Information
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <!-- Network Name -->
                        <v-text-field
                          v-model="network.name"
                          label="Network Name"
                          :rules="[v => !!v || 'Network name is required']"
                          required
                          outlined
                          dense
                          hint="A unique name for your network"
                          persistent-hint
                        ></v-text-field>
                        
                        <!-- Network Driver -->
                        <v-select
                          v-model="network.driver"
                          :items="networkDrivers"
                          label="Network Driver"
                          outlined
                          dense
                          class="mt-4"
                          hint="The network driver to use"
                          persistent-hint
                        ></v-select>
                        
                        <!-- Internal Network -->
                        <v-checkbox
                          v-model="network.internal"
                          label="Internal Network"
                          hint="Internal networks are not connected to the external network"
                          persistent-hint
                          class="mt-4"
                        ></v-checkbox>
                        
                        <!-- Driver Options -->
                        <v-expansion-panels flat class="mt-4">
                          <v-expansion-panel>
                            <v-expansion-panel-header>
                              Driver Options
                            </v-expansion-panel-header>
                            <v-expansion-panel-content>
                              <v-btn
                                small
                                color="primary"
                                text
                                @click="addDriverOption"
                                class="mb-2"
                              >
                                <v-icon left small>mdi-plus</v-icon>
                                Add Option
                              </v-btn>
                              
                              <div
                                v-for="(option, index) in driverOptions"
                                :key="index"
                                class="d-flex align-center mb-2"
                              >
                                <v-text-field
                                  v-model="option.key"
                                  label="Option Key"
                                  outlined
                                  dense
                                  class="mr-2"
                                ></v-text-field>
                                <v-text-field
                                  v-model="option.value"
                                  label="Option Value"
                                  outlined
                                  dense
                                ></v-text-field>
                                <v-btn
                                  icon
                                  small
                                  color="error"
                                  @click="removeDriverOption(index)"
                                  class="ml-2"
                                >
                                  <v-icon small>mdi-delete</v-icon>
                                </v-btn>
                              </div>
                            </v-expansion-panel-content>
                          </v-expansion-panel>
                        </v-expansion-panels>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-ip-network</v-icon>
                        IP Configuration
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <!-- Subnet -->
                        <v-text-field
                          v-model="network.subnet"
                          label="Subnet"
                          outlined
                          dense
                          hint="e.g., 172.18.0.0/16"
                          persistent-hint
                          :rules="[
                            v => !v || isValidSubnet(v) || 'Invalid subnet format (e.g., 172.18.0.0/16)'
                          ]"
                        ></v-text-field>
                        
                        <!-- Gateway -->
                        <v-text-field
                          v-model="network.gateway"
                          label="Gateway"
                          outlined
                          dense
                          class="mt-4"
                          hint="e.g., 172.18.0.1"
                          persistent-hint
                          :rules="[
                            v => !v || isValidIP(v) || 'Invalid IP address format'
                          ]"
                        ></v-text-field>
                        
                        <!-- IP Range -->
                        <v-text-field
                          v-model="network.ipRange"
                          label="IP Range"
                          outlined
                          dense
                          class="mt-4"
                          hint="e.g., 172.18.0.0/24"
                          persistent-hint
                          :rules="[
                            v => !v || isValidSubnet(v) || 'Invalid subnet format (e.g., 172.18.0.0/24)'
                          ]"
                        ></v-text-field>
                        
                        <!-- Auxiliary Addresses -->
                        <v-expansion-panels flat class="mt-4">
                          <v-expansion-panel>
                            <v-expansion-panel-header>
                              Auxiliary Addresses
                            </v-expansion-panel-header>
                            <v-expansion-panel-content>
                              <v-btn
                                small
                                color="primary"
                                text
                                @click="addAuxAddress"
                                class="mb-2"
                              >
                                <v-icon left small>mdi-plus</v-icon>
                                Add Address
                              </v-btn>
                              
                              <div
                                v-for="(address, index) in auxAddresses"
                                :key="index"
                                class="d-flex align-center mb-2"
                              >
                                <v-text-field
                                  v-model="address.name"
                                  label="Host Name"
                                  outlined
                                  dense
                                  class="mr-2"
                                ></v-text-field>
                                <v-text-field
                                  v-model="address.ip"
                                  label="IP Address"
                                  outlined
                                  dense
                                  :rules="[
                                    v => !v || isValidIP(v) || 'Invalid IP address format'
                                  ]"
                                ></v-text-field>
                                <v-btn
                                  icon
                                  small
                                  color="error"
                                  @click="removeAuxAddress(index)"
                                  class="ml-2"
                                >
                                  <v-icon small>mdi-delete</v-icon>
                                </v-btn>
                              </div>
                            </v-expansion-panel-content>
                          </v-expansion-panel>
                        </v-expansion-panels>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                
                <v-row class="mt-4">
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-tag-multiple</v-icon>
                        Labels
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <v-btn
                          small
                          color="primary"
                          text
                          @click="addLabel"
                          class="mb-2"
                        >
                          <v-icon left small>mdi-plus</v-icon>
                          Add Label
                        </v-btn>
                        
                        <div
                          v-for="(label, index) in labels"
                          :key="index"
                          class="d-flex align-center mb-2"
                        >
                          <v-text-field
                            v-model="label.key"
                            label="Label Key"
                            outlined
                            dense
                            class="mr-2"
                          ></v-text-field>
                          <v-text-field
                            v-model="label.value"
                            label="Label Value"
                            outlined
                            dense
                          ></v-text-field>
                          <v-btn
                            icon
                            small
                            color="error"
                            @click="removeLabel(index)"
                            class="ml-2"
                          >
                            <v-icon small>mdi-delete</v-icon>
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                
                <v-row class="mt-4">
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-information-outline</v-icon>
                        Network Preview
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <v-alert
                          v-if="network.driver === 'host'"
                          type="info"
                          outlined
                          dense
                        >
                          Host networks use the host's network stack directly and do not have their own IP configuration.
                        </v-alert>
                        
                        <v-alert
                          v-if="network.driver === 'null'"
                          type="info"
                          outlined
                          dense
                        >
                          Null networks do not provide any networking capabilities to containers.
                        </v-alert>
                        
                        <div v-if="network.driver !== 'host' && network.driver !== 'null'" class="network-visualization pa-4">
                          <div class="network-diagram">
                            <div class="network-node gateway" v-if="network.gateway">
                              <v-icon large>mdi-router-wireless</v-icon>
                              <div class="node-label">Gateway</div>
                              <div class="node-sublabel">{{ network.gateway }}</div>
                            </div>
                            
                            <div class="network-subnet">
                              <v-icon large>mdi-ip-network</v-icon>
                              <div class="node-label">Subnet</div>
                              <div class="node-sublabel">{{ network.subnet || 'Not specified' }}</div>
                            </div>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                
                <v-row class="mt-4">
                  <v-col cols="12" class="text-center">
                    <v-btn
                      color="primary"
                      large
                      :disabled="!valid || creating"
                      :loading="creating"
                      type="submit"
                    >
                      <v-icon left>mdi-plus-network</v-icon>
                      Create Network
                    </v-btn>
                    
                    <v-btn
                      text
                      large
                      color="grey darken-1"
                      class="ml-4"
                      @click="resetForm"
                      :disabled="creating"
                    >
                      Reset
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
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
import { mapActions } from 'vuex';

export default {
  name: 'NetworkCreate',
  
  data() {
    return {
      valid: false,
      creating: false,
      network: {
        name: '',
        driver: 'bridge',
        internal: false,
        subnet: '',
        gateway: '',
        ipRange: ''
      },
      networkDrivers: [
        { text: 'Bridge', value: 'bridge' },
        { text: 'Host', value: 'host' },
        { text: 'Overlay', value: 'overlay' },
        { text: 'Macvlan', value: 'macvlan' },
        { text: 'IPvlan', value: 'ipvlan' },
        { text: 'None', value: 'null' }
      ],
      driverOptions: [],
      auxAddresses: [],
      labels: [],
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  methods: {
    ...mapActions('networks', ['createNetwork']),
    
    goBack() {
      this.$router.push({ name: 'Networks' });
    },
    
    resetForm() {
      this.network = {
        name: '',
        driver: 'bridge',
        internal: false,
        subnet: '',
        gateway: '',
        ipRange: ''
      };
      this.driverOptions = [];
      this.auxAddresses = [];
      this.labels = [];
      this.$refs.form.resetValidation();
    },
    
    addDriverOption() {
      this.driverOptions.push({ key: '', value: '' });
    },
    
    removeDriverOption(index) {
      this.driverOptions.splice(index, 1);
    },
    
    addAuxAddress() {
      this.auxAddresses.push({ name: '', ip: '' });
    },
    
    removeAuxAddress(index) {
      this.auxAddresses.splice(index, 1);
    },
    
    addLabel() {
      this.labels.push({ key: '', value: '' });
    },
    
    removeLabel(index) {
      this.labels.splice(index, 1);
    },
    
    isValidIP(ip) {
      // Simple IP validation regex
      const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      return ipRegex.test(ip);
    },
    
    isValidSubnet(subnet) {
      // Simple subnet validation regex (IP/CIDR)
      const subnetRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[1-2]?[0-9])$/;
      return subnetRegex.test(subnet);
    },
    
    async handleCreateNetwork() {
      if (!this.valid) return;
      
      this.creating = true;
      
      try {
        // Prepare driver options
        const options = {};
        this.driverOptions.forEach(option => {
          if (option.key && option.value) {
            options[option.key] = option.value;
          }
        });
        
        // Prepare auxiliary addresses
        const auxAddresses = {};
        this.auxAddresses.forEach(address => {
          if (address.name && address.ip) {
            auxAddresses[address.name] = address.ip;
          }
        });
        
        // Prepare labels
        const labels = {};
        this.labels.forEach(label => {
          if (label.key && label.value) {
            labels[label.key] = label.value;
          }
        });
        
        // Prepare IPAM config
        const ipamConfig = [];
        if (this.network.subnet) {
          const config = {
            subnet: this.network.subnet
          };
          
          if (this.network.gateway) {
            config.gateway = this.network.gateway;
          }
          
          if (this.network.ipRange) {
            config.ip_range = this.network.ipRange;
          }
          
          if (Object.keys(auxAddresses).length > 0) {
            config.aux_addresses = auxAddresses;
          }
          
          ipamConfig.push(config);
        }
        
        // Prepare network data
        const networkData = {
          name: this.network.name,
          driver: this.network.driver,
          internal: this.network.internal,
          options: Object.keys(options).length > 0 ? options : undefined,
          labels: Object.keys(labels).length > 0 ? labels : undefined,
          ipam: {
            driver: 'default',
            config: ipamConfig
          }
        };
        
        // Create network
        await this.createNetwork(networkData);
        
        this.showSuccess(`Network ${this.network.name} created successfully`);
        
        // Navigate to networks list
        this.$router.push({ name: 'Networks' });
      } catch (error) {
        this.showError(`Failed to create network: ${error.message || 'Unknown error'}`);
      } finally {
        this.creating = false;
      }
    },
    
    async createNetwork() {
      await this.handleCreateNetwork();
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
    }
  }
};
</script>

<style scoped>
.network-create {
  height: 100%;
}

.network-visualization {
  min-height: 200px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.network-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.network-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  margin: 10px;
  min-width: 120px;
}

.gateway {
  background-color: rgba(33, 150, 243, 0.1);
  border: 2px solid #2196F3;
}

.network-subnet {
  background-color: rgba(76, 175, 80, 0.1);
  border: 2px solid #4CAF50;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  margin: 10px;
  min-width: 120px;
}

.node-label {
  font-weight: bold;
  margin-top: 5px;
}

.node-sublabel {
  font-size: 0.8rem;
  color: #666;
}
</style>
