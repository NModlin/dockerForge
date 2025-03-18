<template>
  <div class="backup-list">
    <h1 class="text-h4 mb-4">Backups</h1>

    <!-- Filters and Actions -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="filters.name"
              label="Filter by name"
              prepend-icon="mdi-magnify"
              clearable
              @input="applyFilters"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="filters.type"
              :items="backupTypeOptions"
              label="Filter by type"
              prepend-icon="mdi-filter"
              clearable
              @change="applyFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4" class="d-flex align-center justify-end">
            <v-btn color="primary" @click="showCreateBackupDialog">
              <v-icon left>mdi-plus</v-icon>
              Create Backup
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Empty State -->
    <v-card v-else-if="backups.length === 0" class="mb-4 text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-backup-restore</v-icon>
      <h3 class="text-h5 mt-4">No backups found</h3>
      <p class="text-body-1 mt-2">
        {{ filters.name || filters.type ? 'Try adjusting your filters' : 'Create your first backup to protect your data' }}
      </p>
      <v-btn color="primary" class="mt-4" @click="showCreateBackupDialog">
        <v-icon left>mdi-plus</v-icon>
        Create Backup
      </v-btn>
    </v-card>

    <!-- Backup List -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="backups"
        :items-per-page="10"
        :footer-props="{
          'items-per-page-options': [5, 10, 15, 20],
        }"
        class="elevation-1"
      >
        <!-- Name Column -->
        <template v-slot:item.name="{ item }">
          <div class="font-weight-medium">{{ item.name }}</div>
          <div class="text-caption">{{ item.description }}</div>
        </template>

        <!-- Type Column -->
        <template v-slot:item.type="{ item }">
          <v-chip
            :color="getBackupTypeColor(item.type)"
            text-color="white"
            small
          >
            {{ item.type }}
          </v-chip>
        </template>

        <!-- Status Column -->
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            text-color="white"
            small
          >
            {{ item.status }}
          </v-chip>
        </template>

        <!-- Size Column -->
        <template v-slot:item.size="{ item }">
          {{ formatSize(item.size) }}
        </template>

        <!-- Created Column -->
        <template v-slot:item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <!-- Actions Column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            small
            @click="showRestoreDialog(item)"
            title="Restore"
            :disabled="item.status !== 'completed'"
          >
            <v-icon small>mdi-backup-restore</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            @click="downloadBackup(item)"
            title="Download"
            :disabled="item.status !== 'completed'"
          >
            <v-icon small>mdi-download</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            @click="showDeleteDialog(item)"
            title="Delete"
          >
            <v-icon small>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create Backup Dialog -->
    <v-dialog v-model="createBackupDialog" max-width="600">
      <v-card>
        <v-card-title class="headline">Create Backup</v-card-title>
        <v-card-text>
          <v-form ref="createBackupForm" v-model="createBackupFormValid">
            <v-text-field
              v-model="newBackup.name"
              label="Backup Name"
              :rules="[v => !!v || 'Name is required']"
              required
            ></v-text-field>
            
            <v-textarea
              v-model="newBackup.description"
              label="Description"
              rows="2"
            ></v-textarea>
            
            <v-select
              v-model="newBackup.type"
              :items="backupTypeOptions"
              label="Backup Type"
              :rules="[v => !!v || 'Type is required']"
              required
            ></v-select>
            
            <v-select
              v-model="newBackup.resources"
              :items="resourceOptions"
              label="Resources to Backup"
              multiple
              chips
              :rules="[v => v.length > 0 || 'Select at least one resource']"
              required
            ></v-select>
            
            <v-checkbox
              v-model="newBackup.includeVolumes"
              label="Include volumes"
            ></v-checkbox>
            
            <v-checkbox
              v-model="newBackup.compress"
              label="Compress backup"
            ></v-checkbox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="createBackupDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            text
            @click="createBackup"
            :disabled="!createBackupFormValid || creatingBackup"
            :loading="creatingBackup"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Restore Backup Dialog -->
    <v-dialog v-model="restoreDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Restore Backup</v-card-title>
        <v-card-text>
          Are you sure you want to restore the backup <strong>{{ selectedBackup?.name }}</strong>?
          <v-alert
            type="warning"
            class="mt-3"
            dense
          >
            This will replace your current data with the backup data. This action cannot be undone.
          </v-alert>
          
          <v-checkbox
            v-model="restoreOptions.includeVolumes"
            label="Restore volumes"
            class="mt-4"
          ></v-checkbox>
          
          <v-checkbox
            v-model="restoreOptions.stopContainers"
            label="Stop running containers before restore"
            class="mt-2"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="restoreDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="warning"
            text
            @click="restoreBackup"
            :loading="restoringBackup"
          >
            Restore
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Backup</v-card-title>
        <v-card-text>
          Are you sure you want to delete the backup <strong>{{ selectedBackup?.name }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteBackup">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'BackupList',
  data() {
    return {
      loading: true,
      error: null,
      backups: [],
      filters: {
        name: '',
        type: '',
      },
      backupTypeOptions: [
        { text: 'All', value: '' },
        { text: 'Full', value: 'full' },
        { text: 'Containers', value: 'containers' },
        { text: 'Images', value: 'images' },
        { text: 'Volumes', value: 'volumes' },
        { text: 'Configuration', value: 'config' },
      ],
      resourceOptions: [
        'All Containers',
        'All Images',
        'All Volumes',
        'All Networks',
        'Docker Configuration',
      ],
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Type', value: 'type', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Size', value: 'size', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      createBackupDialog: false,
      createBackupFormValid: false,
      creatingBackup: false,
      newBackup: {
        name: '',
        description: '',
        type: 'full',
        resources: ['All Containers'],
        includeVolumes: true,
        compress: true,
      },
      restoreDialog: false,
      restoringBackup: false,
      restoreOptions: {
        includeVolumes: true,
        stopContainers: true,
      },
      deleteDialog: false,
      selectedBackup: null,
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchBackups();
  },
  methods: {
    async fetchBackups() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get('/api/backups', {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: this.filters,
        // });
        // this.backups = response.data;

        // Mock data for development
        setTimeout(() => {
          this.backups = [
            {
              id: 'b1',
              name: 'Weekly Full Backup',
              description: 'Automated weekly backup of all resources',
              type: 'full',
              status: 'completed',
              size: 1024 * 1024 * 1024 * 2.5, // 2.5 GB
              created_at: '2025-03-16T00:00:00Z',
            },
            {
              id: 'b2',
              name: 'Pre-deployment Backup',
              description: 'Manual backup before major deployment',
              type: 'containers',
              status: 'completed',
              size: 1024 * 1024 * 512, // 512 MB
              created_at: '2025-03-15T12:00:00Z',
            },
            {
              id: 'b3',
              name: 'Database Volumes',
              description: 'Backup of database volumes only',
              type: 'volumes',
              status: 'completed',
              size: 1024 * 1024 * 1024 * 1.2, // 1.2 GB
              created_at: '2025-03-14T08:00:00Z',
            },
            {
              id: 'b4',
              name: 'Configuration Backup',
              description: 'Docker daemon and container configurations',
              type: 'config',
              status: 'completed',
              size: 1024 * 1024 * 5, // 5 MB
              created_at: '2025-03-13T16:00:00Z',
            },
            {
              id: 'b5',
              name: 'Image Repository',
              description: 'Backup of all local images',
              type: 'images',
              status: 'in-progress',
              size: 0,
              created_at: '2025-03-17T05:30:00Z',
            },
          ];
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load backups. Please try again.';
        this.loading = false;
      }
    },
    applyFilters() {
      this.fetchBackups();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    formatSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    getBackupTypeColor(type) {
      switch (type) {
        case 'full':
          return 'primary';
        case 'containers':
          return 'success';
        case 'images':
          return 'info';
        case 'volumes':
          return 'warning';
        case 'config':
          return 'purple';
        default:
          return 'grey';
      }
    },
    getStatusColor(status) {
      switch (status) {
        case 'completed':
          return 'success';
        case 'in-progress':
          return 'info';
        case 'failed':
          return 'error';
        default:
          return 'grey';
      }
    },
    showCreateBackupDialog() {
      this.newBackup = {
        name: '',
        description: '',
        type: 'full',
        resources: ['All Containers'],
        includeVolumes: true,
        compress: true,
      };
      this.createBackupDialog = true;
    },
    async createBackup() {
      if (!this.$refs.createBackupForm.validate()) return;
      
      this.creatingBackup = true;
      
      try {
        // In a real implementation, this would call the API
        // await axios.post('/api/backups', this.newBackup, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        setTimeout(() => {
          const newBackupId = `b${this.backups.length + 1}`;
          const now = new Date().toISOString();
          
          this.backups.unshift({
            id: newBackupId,
            name: this.newBackup.name,
            description: this.newBackup.description,
            type: this.newBackup.type,
            status: 'in-progress',
            size: 0,
            created_at: now,
          });
          
          // Simulate backup completion after 3 seconds
          setTimeout(() => {
            const index = this.backups.findIndex(b => b.id === newBackupId);
            if (index !== -1) {
              this.backups[index].status = 'completed';
              this.backups[index].size = Math.random() * 1024 * 1024 * 1024 * 3; // Random size up to 3 GB
              this.$forceUpdate();
            }
          }, 3000);
          
          this.createBackupDialog = false;
          this.creatingBackup = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to create backup. Please try again.';
        this.creatingBackup = false;
      }
    },
    showRestoreDialog(backup) {
      this.selectedBackup = backup;
      this.restoreOptions = {
        includeVolumes: true,
        stopContainers: true,
      };
      this.restoreDialog = true;
    },
    async restoreBackup() {
      this.restoringBackup = true;
      
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/backups/${this.selectedBackup.id}/restore`, this.restoreOptions, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        setTimeout(() => {
          this.restoreDialog = false;
          this.restoringBackup = false;
          
          // Show success message
          this.$emit('show-notification', {
            type: 'success',
            message: `Backup ${this.selectedBackup.name} restored successfully`,
          });
        }, 2000);
      } catch (error) {
        this.error = `Failed to restore backup ${this.selectedBackup.name}`;
        this.restoringBackup = false;
      }
    },
    downloadBackup(backup) {
      // In a real implementation, this would trigger a file download
      // window.location.href = `/api/backups/${backup.id}/download?token=${this.token}`;
      
      // Mock implementation - just show a notification
      this.$emit('show-notification', {
        type: 'info',
        message: `Downloading backup: ${backup.name} (${this.formatSize(backup.size)})`,
      });
    },
    showDeleteDialog(backup) {
      this.selectedBackup = backup;
      this.deleteDialog = true;
    },
    async deleteBackup() {
      if (!this.selectedBackup) return;
      
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/backups/${this.selectedBackup.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.backups = this.backups.filter(b => b.id !== this.selectedBackup.id);
        this.deleteDialog = false;
        this.selectedBackup = null;
      } catch (error) {
        this.error = `Failed to delete backup ${this.selectedBackup.name}`;
        this.deleteDialog = false;
      }
    },
  },
};
</script>

<style scoped>
.backup-list {
  padding: 16px;
}
</style>
