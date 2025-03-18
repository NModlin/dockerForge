<template>
  <div class="compose-detail">
    <v-row>
      <v-col cols="12">
        <v-btn text to="/compose" class="mb-4">
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Compose Projects
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Project Not Found -->
    <v-alert v-else-if="!project" type="warning" class="mb-4">
      Compose project not found
    </v-alert>

    <!-- Project Details -->
    <template v-else>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title class="headline d-flex align-center">
              {{ project.name }}
              <v-chip
                class="ml-2"
                :color="getStatusColor(project.status)"
                text-color="white"
                small
              >
                {{ project.status }}
              </v-chip>
              <v-spacer></v-spacer>
              <v-btn-toggle>
                <v-btn
                  :disabled="project.status === 'running'"
                  @click="startProject"
                  color="success"
                  text
                >
                  <v-icon left>mdi-play</v-icon>
                  Start
                </v-btn>
                <v-btn
                  :disabled="project.status !== 'running'"
                  @click="stopProject"
                  color="error"
                  text
                >
                  <v-icon left>mdi-stop</v-icon>
                  Stop
                </v-btn>
                <v-btn
                  :disabled="project.status !== 'running'"
                  @click="restartProject"
                  color="primary"
                  text
                >
                  <v-icon left>mdi-restart</v-icon>
                  Restart
                </v-btn>
                <v-btn
                  @click="showDeleteDialog"
                  color="error"
                  text
                >
                  <v-icon left>mdi-delete</v-icon>
                  Delete
                </v-btn>
              </v-btn-toggle>
            </v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <tbody>
                    <tr>
                      <td class="font-weight-bold">ID</td>
                      <td>{{ project.id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Location</td>
                      <td>{{ project.location }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Services</td>
                      <td>{{ project.service_count }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">Created</td>
                      <td>{{ formatDate(project.created_at) }}</td>
                    </tr>
                    <tr v-if="project.last_deployed">
                      <td class="font-weight-bold">Last Deployed</td>
                      <td>{{ formatDate(project.last_deployed) }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Services -->
      <v-row>
        <v-col cols="12">
          <h2 class="text-h5 mb-3">Services</h2>
          <v-card>
            <v-data-table
              :headers="serviceHeaders"
              :items="services"
              :items-per-page="10"
              class="elevation-1"
            >
              <!-- Name Column -->
              <template v-slot:item.name="{ item }">
                <router-link 
                  v-if="item.container_id" 
                  :to="`/containers/${item.container_id}`" 
                  class="text-decoration-none"
                >
                  {{ item.name }}
                </router-link>
                <span v-else>{{ item.name }}</span>
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

              <!-- Actions Column -->
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  small
                  :disabled="item.status === 'running'"
                  @click="startService(item)"
                  title="Start"
                >
                  <v-icon small>mdi-play</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  :disabled="item.status !== 'running'"
                  @click="stopService(item)"
                  title="Stop"
                >
                  <v-icon small>mdi-stop</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  :disabled="item.status !== 'running'"
                  @click="restartService(item)"
                  title="Restart"
                >
                  <v-icon small>mdi-restart</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  :disabled="!item.logs_available"
                  @click="viewLogs(item)"
                  title="View Logs"
                >
                  <v-icon small>mdi-text-box-outline</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>

      <!-- Compose File -->
      <v-row class="mt-4">
        <v-col cols="12">
          <h2 class="text-h5 mb-3">Compose File</h2>
          <v-card>
            <v-card-title class="d-flex align-center">
              <span>docker-compose.yml</span>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                text
                @click="editComposeFile"
              >
                <v-icon left>mdi-pencil</v-icon>
                Edit
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-sheet
                class="pa-4 compose-file-content"
                outlined
                rounded
              >
                <pre>{{ composeFileContent }}</pre>
              </v-sheet>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete Compose Project</v-card-title>
        <v-card-text>
          Are you sure you want to delete the compose project <strong>{{ project?.name }}</strong>?
          <v-checkbox
            v-model="deleteWithVolumes"
            label="Also remove associated volumes"
            class="mt-4"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteProject">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Logs Dialog -->
    <v-dialog v-model="logsDialog" max-width="800">
      <v-card>
        <v-card-title class="headline">
          Logs: {{ selectedService?.name }}
          <v-spacer></v-spacer>
          <v-btn icon @click="logsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-checkbox
            v-model="followLogs"
            label="Follow logs"
            class="mb-2"
          ></v-checkbox>
          <v-sheet
            class="pa-4 logs-content"
            outlined
            rounded
            height="400px"
            style="overflow-y: auto; font-family: monospace;"
          >
            <div v-for="(line, index) in serviceLogs" :key="index">
              {{ line }}
            </div>
          </v-sheet>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="logsDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit Compose File Dialog -->
    <v-dialog v-model="editDialog" max-width="800">
      <v-card>
        <v-card-title class="headline">
          Edit Compose File
          <v-spacer></v-spacer>
          <v-btn icon @click="editDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-textarea
            v-model="editedComposeFile"
            outlined
            rows="20"
            class="font-family-monospace"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="editDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" text @click="saveComposeFile">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'ComposeDetail',
  data() {
    return {
      loading: true,
      error: null,
      project: null,
      services: [],
      composeFileContent: '',
      serviceHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Image', value: 'image', sortable: true },
        { text: 'Ports', value: 'ports', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
      deleteDialog: false,
      deleteWithVolumes: false,
      logsDialog: false,
      selectedService: null,
      serviceLogs: [],
      followLogs: false,
      editDialog: false,
      editedComposeFile: '',
    };
  },
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      token: 'auth/token',
    }),
  },
  created() {
    this.fetchProjectDetails();
  },
  methods: {
    async fetchProjectDetails() {
      this.loading = true;
      this.error = null;

      try {
        // In a real implementation, this would call the API
        // const response = await axios.get(`/api/compose/${this.$route.params.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        // this.project = response.data;
        // this.services = response.data.services;
        // this.composeFileContent = response.data.compose_file;
        
        // Mock data for development
        setTimeout(() => {
          this.project = {
            id: this.$route.params.id,
            name: 'web-app',
            status: 'running',
            service_count: 3,
            location: '/home/user/projects/web-app',
            created_at: '2025-03-15T10:00:00Z',
            last_deployed: '2025-03-16T08:30:00Z',
          };
          
          this.services = [
            {
              name: 'web',
              status: 'running',
              image: 'nginx:latest',
              ports: ['80:80', '443:443'],
              container_id: 'c1',
              logs_available: true,
            },
            {
              name: 'api',
              status: 'running',
              image: 'node:14-alpine',
              ports: ['3000:3000'],
              container_id: 'c4',
              logs_available: true,
            },
            {
              name: 'db',
              status: 'running',
              image: 'postgres:13',
              ports: ['5432:5432'],
              container_id: 'c3',
              logs_available: true,
            },
          ];
          
          this.composeFileContent = `version: '3'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
    depends_on:
      - api
    restart: always

  api:
    image: node:14-alpine
    working_dir: /app
    volumes:
      - ./api:/app
    command: npm start
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    depends_on:
      - db
    restart: always

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=example
      - POSTGRES_USER=app
      - POSTGRES_DB=app_db
    ports:
      - "5432:5432"
    restart: always

volumes:
  postgres_data:`;
          
          this.loading = false;
        }, 1000);
      } catch (error) {
        this.error = 'Failed to load compose project details. Please try again.';
        this.loading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
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
    async startProject() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/start`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.project.status = 'running';
        this.services.forEach(service => {
          service.status = 'running';
        });
      } catch (error) {
        this.error = `Failed to start compose project ${this.project.name}`;
      }
    },
    async stopProject() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/stop`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.project.status = 'stopped';
        this.services.forEach(service => {
          service.status = 'stopped';
        });
      } catch (error) {
        this.error = `Failed to stop compose project ${this.project.name}`;
      }
    },
    async restartProject() {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/restart`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.project.status = 'running';
        this.services.forEach(service => {
          service.status = 'running';
        });
      } catch (error) {
        this.error = `Failed to restart compose project ${this.project.name}`;
      }
    },
    showDeleteDialog() {
      this.deleteWithVolumes = false;
      this.deleteDialog = true;
    },
    async deleteProject() {
      try {
        // In a real implementation, this would call the API
        // await axios.delete(`/api/compose/${this.project.id}`, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        //   params: { removeVolumes: this.deleteWithVolumes },
        // });
        
        // Navigate back to compose list
        this.$router.push('/compose');
      } catch (error) {
        this.error = `Failed to delete compose project ${this.project.name}`;
        this.deleteDialog = false;
      }
    },
    async startService(service) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/services/${service.name}/start`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        service.status = 'running';
        this.updateProjectStatus();
      } catch (error) {
        this.error = `Failed to start service ${service.name}`;
      }
    },
    async stopService(service) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/services/${service.name}/stop`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        service.status = 'stopped';
        this.updateProjectStatus();
      } catch (error) {
        this.error = `Failed to stop service ${service.name}`;
      }
    },
    async restartService(service) {
      try {
        // In a real implementation, this would call the API
        // await axios.post(`/api/compose/${this.project.id}/services/${service.name}/restart`, {}, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        service.status = 'running';
        this.updateProjectStatus();
      } catch (error) {
        this.error = `Failed to restart service ${service.name}`;
      }
    },
    updateProjectStatus() {
      const runningServices = this.services.filter(s => s.status === 'running').length;
      
      if (runningServices === 0) {
        this.project.status = 'stopped';
      } else if (runningServices === this.services.length) {
        this.project.status = 'running';
      } else {
        this.project.status = 'partial';
      }
    },
    viewLogs(service) {
      this.selectedService = service;
      this.serviceLogs = [
        `[2025-03-16 08:30:01] ${service.name} | Starting ${service.name} service...`,
        `[2025-03-16 08:30:02] ${service.name} | Service started successfully`,
        `[2025-03-16 08:30:03] ${service.name} | Listening on port ${service.ports[0].split(':')[0]}`,
        `[2025-03-16 08:35:15] ${service.name} | Received request from 192.168.1.5`,
        `[2025-03-16 08:35:16] ${service.name} | Request processed successfully (200 OK)`,
        `[2025-03-16 08:40:22] ${service.name} | Received request from 192.168.1.10`,
        `[2025-03-16 08:40:23] ${service.name} | Request processed successfully (200 OK)`,
        `[2025-03-16 08:45:30] ${service.name} | Performing scheduled health check`,
        `[2025-03-16 08:45:31] ${service.name} | Health check passed: all systems operational`,
      ];
      this.logsDialog = true;
    },
    editComposeFile() {
      this.editedComposeFile = this.composeFileContent;
      this.editDialog = true;
    },
    async saveComposeFile() {
      try {
        // In a real implementation, this would call the API
        // await axios.put(`/api/compose/${this.project.id}/file`, {
        //   content: this.editedComposeFile
        // }, {
        //   headers: { Authorization: `Bearer ${this.token}` },
        // });
        
        // Mock implementation
        this.composeFileContent = this.editedComposeFile;
        this.editDialog = false;
      } catch (error) {
        this.error = 'Failed to save compose file';
      }
    },
  },
};
</script>

<style scoped>
.compose-detail {
  padding: 16px;
}

.compose-file-content {
  max-height: 400px;
  overflow-y: auto;
  font-family: monospace;
  white-space: pre-wrap;
}

.font-family-monospace {
  font-family: monospace;
}
</style>
