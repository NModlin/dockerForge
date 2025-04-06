<template>
  <div class="compose-project-list">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-docker</v-icon>
              Docker Compose Projects
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search projects"
                single-line
                hide-details
                class="mx-4"
                dense
                outlined
              ></v-text-field>
              <v-btn color="primary" to="/compose/create">
                <v-icon left>mdi-plus</v-icon>
                New Project
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-data-table
                :headers="headers"
                :items="filteredProjects"
                :search="search"
                :loading="loading"
                :items-per-page="10"
                :footer-props="{
                  'items-per-page-options': [5, 10, 15, 20, -1],
                  'items-per-page-text': 'Projects per page',
                }"
                class="elevation-1"
              >
                <!-- Status column -->
                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="getStatusColor(item.status)"
                    dark
                    small
                  >
                    {{ item.status }}
                  </v-chip>
                </template>
                
                <!-- Service count column -->
                <template v-slot:item.service_count="{ item }">
                  <v-badge
                    :content="item.service_count"
                    :color="getStatusColor(item.status)"
                    offset-x="10"
                    offset-y="10"
                  >
                    <v-icon>mdi-cube-outline</v-icon>
                  </v-badge>
                </template>
                
                <!-- Created at column -->
                <template v-slot:item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
                
                <!-- Actions column -->
                <template v-slot:item.actions="{ item }">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        color="primary"
                        v-bind="attrs"
                        v-on="on"
                        @click="viewProject(item)"
                      >
                        <v-icon small>mdi-eye</v-icon>
                      </v-btn>
                    </template>
                    <span>View Project</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        color="success"
                        v-bind="attrs"
                        v-on="on"
                        @click="startProject(item)"
                        :disabled="item.status === 'running'"
                      >
                        <v-icon small>mdi-play</v-icon>
                      </v-btn>
                    </template>
                    <span>Start Project</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        color="error"
                        v-bind="attrs"
                        v-on="on"
                        @click="stopProject(item)"
                        :disabled="item.status === 'stopped'"
                      >
                        <v-icon small>mdi-stop</v-icon>
                      </v-btn>
                    </template>
                    <span>Stop Project</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        color="warning"
                        v-bind="attrs"
                        v-on="on"
                        @click="restartProject(item)"
                        :disabled="item.status === 'stopped'"
                      >
                        <v-icon small>mdi-restart</v-icon>
                      </v-btn>
                    </template>
                    <span>Restart Project</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        color="info"
                        v-bind="attrs"
                        v-on="on"
                        @click="openControlPanel(item)"
                      >
                        <v-icon small>mdi-tune</v-icon>
                      </v-btn>
                    </template>
                    <span>Control Panel</span>
                  </v-tooltip>
                </template>
                
                <!-- No data template -->
                <template v-slot:no-data>
                  <v-alert
                    :value="true"
                    color="info"
                    icon="mdi-information"
                    outlined
                  >
                    No Docker Compose projects found. Click the "New Project" button to create one.
                  </v-alert>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Control Panel Dialog -->
    <compose-control-panel
      v-if="selectedProject"
      v-model="showControlPanel"
      :project="selectedProject"
      @refresh="fetchProjects"
      @error="showError"
      @success="showSuccess"
    ></compose-control-panel>
    
    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      bottom
      right
    >
      {{ snackbar.text }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import ComposeControlPanel from '../../components/compose/ComposeControlPanel.vue';

export default {
  name: 'ComposeProjectList',
  
  components: {
    ComposeControlPanel
  },
  
  data() {
    return {
      search: '',
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Services', value: 'service_count', sortable: true },
        { text: 'Location', value: 'location', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      selectedProject: null,
      showControlPanel: false,
      snackbar: {
        show: false,
        text: '',
        color: 'success',
        timeout: 5000
      }
    };
  },
  
  computed: {
    ...mapState('compose', ['composeFiles', 'loading', 'error']),
    
    filteredProjects() {
      return this.composeFiles;
    }
  },
  
  created() {
    this.fetchProjects();
  },
  
  methods: {
    ...mapActions('compose', [
      'getComposeFiles',
      'startComposeProject',
      'stopComposeProject',
      'restartComposeProject'
    ]),
    
    async fetchProjects() {
      try {
        await this.getComposeFiles();
      } catch (error) {
        this.showError('Failed to load compose projects');
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
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
    
    viewProject(project) {
      this.$router.push({ name: 'ComposeDetail', params: { id: project.id } });
    },
    
    async startProject(project) {
      try {
        await this.startComposeProject(project.id);
        this.showSuccess(`Project ${project.name} started successfully`);
        this.fetchProjects();
      } catch (error) {
        this.showError(`Failed to start project ${project.name}`);
      }
    },
    
    async stopProject(project) {
      try {
        await this.stopComposeProject(project.id);
        this.showSuccess(`Project ${project.name} stopped successfully`);
        this.fetchProjects();
      } catch (error) {
        this.showError(`Failed to stop project ${project.name}`);
      }
    },
    
    async restartProject(project) {
      try {
        await this.restartComposeProject(project.id);
        this.showSuccess(`Project ${project.name} restarted successfully`);
        this.fetchProjects();
      } catch (error) {
        this.showError(`Failed to restart project ${project.name}`);
      }
    },
    
    openControlPanel(project) {
      this.selectedProject = project;
      this.showControlPanel = true;
    },
    
    showSuccess(text) {
      this.snackbar.text = text;
      this.snackbar.color = 'success';
      this.snackbar.show = true;
    },
    
    showError(text) {
      this.snackbar.text = text;
      this.snackbar.color = 'error';
      this.snackbar.show = true;
    }
  }
};
</script>

<style scoped>
.compose-project-list {
  height: 100%;
}
</style>
