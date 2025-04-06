<template>
  <div class="volume-create">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-database-plus</v-icon>
              Create Volume
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Volumes
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-form ref="form" v-model="valid" @submit.prevent="createVolume">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-information</v-icon>
                        Basic Information
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <!-- Volume Name -->
                        <v-text-field
                          v-model="volume.name"
                          label="Volume Name"
                          :rules="[v => !!v || 'Volume name is required']"
                          required
                          outlined
                          dense
                          hint="A unique name for your volume"
                          persistent-hint
                        ></v-text-field>
                        
                        <!-- Volume Driver -->
                        <v-select
                          v-model="volume.driver"
                          :items="volumeDrivers"
                          label="Volume Driver"
                          outlined
                          dense
                          class="mt-4"
                          hint="The volume driver to use"
                          persistent-hint
                        ></v-select>
                        
                        <!-- Volume Type -->
                        <v-select
                          v-model="volume.type"
                          :items="volumeTypes"
                          label="Volume Type"
                          outlined
                          dense
                          class="mt-4"
                          hint="The type of volume to create"
                          persistent-hint
                        ></v-select>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-cog</v-icon>
                        Driver Options
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
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
                        
                        <div v-if="driverOptions.length === 0" class="text-center pa-4 grey--text">
                          <v-icon large color="grey lighten-1">mdi-cog-outline</v-icon>
                          <p class="text-body-2 mt-2">No driver options added</p>
                        </div>
                        
                        <v-alert
                          v-if="volume.driver === 'local'"
                          type="info"
                          outlined
                          dense
                          class="mt-4"
                        >
                          <strong>Common local driver options:</strong>
                          <ul class="mb-0">
                            <li><code>o=bind</code> - Bind mount a directory</li>
                            <li><code>device=/path/on/host</code> - Path on the host</li>
                            <li><code>type=none</code> - Use with bind mounts</li>
                          </ul>
                        </v-alert>
                        
                        <v-alert
                          v-if="volume.driver === 'nfs'"
                          type="info"
                          outlined
                          dense
                          class="mt-4"
                        >
                          <strong>Common NFS driver options:</strong>
                          <ul class="mb-0">
                            <li><code>server=nfs-server.example.com</code> - NFS server address</li>
                            <li><code>share=/path/on/server</code> - Exported share on the server</li>
                          </ul>
                        </v-alert>
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
                        
                        <div v-if="labels.length === 0" class="text-center pa-4 grey--text">
                          <v-icon large color="grey lighten-1">mdi-tag-outline</v-icon>
                          <p class="text-body-2 mt-2">No labels added</p>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                
                <!-- Bind Mount Options (shown only when type is 'bind') -->
                <v-row v-if="volume.type === 'bind'" class="mt-4">
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-folder-open</v-icon>
                        Bind Mount Options
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <v-text-field
                          v-model="volume.source"
                          label="Host Path"
                          outlined
                          dense
                          hint="Path on the host to bind mount"
                          persistent-hint
                          :rules="[v => volume.type !== 'bind' || !!v || 'Host path is required for bind mounts']"
                        ></v-text-field>
                        
                        <v-checkbox
                          v-model="volume.readonly"
                          label="Read Only"
                          hint="Mount as read-only"
                          persistent-hint
                          class="mt-4"
                        ></v-checkbox>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                
                <!-- tmpfs Options (shown only when type is 'tmpfs') -->
                <v-row v-if="volume.type === 'tmpfs'" class="mt-4">
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-memory</v-icon>
                        tmpfs Options
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <v-text-field
                          v-model="volume.size"
                          label="Size"
                          outlined
                          dense
                          hint="Size of the tmpfs mount in bytes, or with k, m, or g suffix"
                          persistent-hint
                        ></v-text-field>
                        
                        <v-text-field
                          v-model="volume.mode"
                          label="Mode"
                          outlined
                          dense
                          hint="File mode of the tmpfs in octal (e.g., 1777)"
                          persistent-hint
                          class="mt-4"
                        ></v-text-field>
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
                      <v-icon left>mdi-database-plus</v-icon>
                      Create Volume
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
  name: 'VolumeCreate',
  
  data() {
    return {
      valid: false,
      creating: false,
      volume: {
        name: '',
        driver: 'local',
        type: 'volume',
        source: '',
        readonly: false,
        size: '',
        mode: ''
      },
      volumeDrivers: [
        { text: 'Local', value: 'local' },
        { text: 'NFS', value: 'nfs' },
        { text: 'CIFS/SMB', value: 'cifs' },
        { text: 'GlusterFS', value: 'glusterfs' },
        { text: 'Custom', value: 'custom' }
      ],
      volumeTypes: [
        { text: 'Named Volume', value: 'volume' },
        { text: 'Bind Mount', value: 'bind' },
        { text: 'tmpfs Mount', value: 'tmpfs' }
      ],
      driverOptions: [],
      labels: [],
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  methods: {
    ...mapActions('volumes', ['createVolume']),
    
    goBack() {
      this.$router.push({ name: 'Volumes' });
    },
    
    resetForm() {
      this.volume = {
        name: '',
        driver: 'local',
        type: 'volume',
        source: '',
        readonly: false,
        size: '',
        mode: ''
      };
      this.driverOptions = [];
      this.labels = [];
      this.$refs.form.resetValidation();
    },
    
    addDriverOption() {
      this.driverOptions.push({ key: '', value: '' });
    },
    
    removeDriverOption(index) {
      this.driverOptions.splice(index, 1);
    },
    
    addLabel() {
      this.labels.push({ key: '', value: '' });
    },
    
    removeLabel(index) {
      this.labels.splice(index, 1);
    },
    
    async handleCreateVolume() {
      if (!this.valid) return;
      
      this.creating = true;
      
      try {
        // Prepare driver options
        const driverOpts = {};
        this.driverOptions.forEach(option => {
          if (option.key && option.value) {
            driverOpts[option.key] = option.value;
          }
        });
        
        // Prepare labels
        const labels = {};
        this.labels.forEach(label => {
          if (label.key && label.value) {
            labels[label.key] = label.value;
          }
        });
        
        // Add type-specific options
        if (this.volume.type === 'bind') {
          driverOpts.type = 'none';
          driverOpts.o = 'bind';
          driverOpts.device = this.volume.source;
          
          if (this.volume.readonly) {
            driverOpts.readonly = 'true';
          }
        } else if (this.volume.type === 'tmpfs') {
          driverOpts.type = 'tmpfs';
          
          if (this.volume.size) {
            driverOpts.size = this.volume.size;
          }
          
          if (this.volume.mode) {
            driverOpts.mode = this.volume.mode;
          }
        }
        
        // Prepare volume data
        const volumeData = {
          name: this.volume.name,
          driver: this.volume.driver,
          driver_opts: Object.keys(driverOpts).length > 0 ? driverOpts : undefined,
          labels: Object.keys(labels).length > 0 ? labels : undefined
        };
        
        // Create volume
        await this.createVolume(volumeData);
        
        this.showSuccess(`Volume ${this.volume.name} created successfully`);
        
        // Navigate to volumes list
        this.$router.push({ name: 'Volumes' });
      } catch (error) {
        this.showError(`Failed to create volume: ${error.message || 'Unknown error'}`);
      } finally {
        this.creating = false;
      }
    },
    
    async createVolume() {
      await this.handleCreateVolume();
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
.volume-create {
  height: 100%;
}
</style>
