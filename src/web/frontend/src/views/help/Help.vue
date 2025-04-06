<template>
  <div class="help">
    <h1 class="text-h4 mb-4">Help & Documentation</h1>

    <!-- Documentation Search -->
    <documentation-search class="mb-4" />

    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-book-open-variant</v-icon>
        Documentation
      </v-card-title>
      <v-card-text>
        <p>Welcome to DockerForge! This help section provides resources to help you get the most out of the application.</p>

        <v-tabs v-model="activeTab" background-color="primary" dark>
          <v-tab>Getting Started</v-tab>
          <v-tab>User Guide</v-tab>
          <v-tab>API Reference</v-tab>
          <v-tab>FAQ</v-tab>
        </v-tabs>

        <v-tabs-items v-model="activeTab">
          <!-- Getting Started -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h5 mb-3">Getting Started with DockerForge</h3>

                <v-card outlined class="mb-4">
                  <v-card-title class="subtitle-1">
                    <v-icon left small>mdi-numeric-1-circle</v-icon>
                    Understanding the Dashboard
                  </v-card-title>
                  <v-card-text>
                    <p>The Dashboard provides an overview of your Docker environment, including:</p>
                    <ul>
                      <li>Container status summary</li>
                      <li>Resource usage</li>
                      <li>Recent events</li>
                      <li>Quick actions</li>
                    </ul>
                    <p>Use the Dashboard to quickly assess the health of your Docker environment and access common tasks.</p>
                  </v-card-text>
                </v-card>

                <v-card outlined class="mb-4">
                  <v-card-title class="subtitle-1">
                    <v-icon left small>mdi-numeric-2-circle</v-icon>
                    Managing Containers
                  </v-card-title>
                  <v-card-text>
                    <p>The Containers section allows you to:</p>
                    <ul>
                      <li>View all containers</li>
                      <li>Start, stop, and restart containers</li>
                      <li>View container logs</li>
                      <li>Access container shells</li>
                      <li>Create new containers</li>
                    </ul>
                    <p>Click on a container name to view detailed information and access management options.</p>
                  </v-card-text>
                </v-card>

                <v-card outlined class="mb-4">
                  <v-card-title class="subtitle-1">
                    <v-icon left small>mdi-numeric-3-circle</v-icon>
                    Working with Images
                  </v-card-title>
                  <v-card-text>
                    <p>The Images section allows you to:</p>
                    <ul>
                      <li>View all Docker images</li>
                      <li>Pull new images</li>
                      <li>Build custom images</li>
                      <li>Scan images for vulnerabilities</li>
                    </ul>
                    <p>Use the search field to quickly find specific images in your repository.</p>
                  </v-card-text>
                </v-card>

                <v-btn color="primary" to="/">
                  <v-icon left>mdi-arrow-right</v-icon>
                  Go to Dashboard
                </v-btn>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- User Guide -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h5 mb-3">User Guide</h3>

                <v-expansion-panels>
                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      <div>
                        <v-icon left>mdi-docker</v-icon>
                        Container Management
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <h4 class="subtitle-1 font-weight-bold mb-2">Creating Containers</h4>
                      <p>To create a new container:</p>
                      <ol>
                        <li>Navigate to the Containers section</li>
                        <li>Click the "New Container" button</li>
                        <li>Select an image</li>
                        <li>Configure container settings</li>
                        <li>Click "Create"</li>
                      </ol>

                      <h4 class="subtitle-1 font-weight-bold mb-2 mt-4">Managing Container Lifecycle</h4>
                      <p>You can manage container lifecycle using the action buttons:</p>
                      <ul>
                        <li><strong>Start</strong>: Starts a stopped container</li>
                        <li><strong>Stop</strong>: Gracefully stops a running container</li>
                        <li><strong>Restart</strong>: Restarts a container</li>
                        <li><strong>Pause</strong>: Temporarily pauses container processes</li>
                        <li><strong>Kill</strong>: Forcefully stops a container</li>
                      </ul>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      <div>
                        <v-icon left>mdi-package-variant-closed</v-icon>
                        Image Management
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <h4 class="subtitle-1 font-weight-bold mb-2">Pulling Images</h4>
                      <p>To pull a Docker image:</p>
                      <ol>
                        <li>Navigate to the Images section</li>
                        <li>Click the "Pull Image" button</li>
                        <li>Enter the image name and tag</li>
                        <li>Click "Pull"</li>
                      </ol>

                      <h4 class="subtitle-1 font-weight-bold mb-2 mt-4">Building Images</h4>
                      <p>To build a custom Docker image:</p>
                      <ol>
                        <li>Navigate to the Images section</li>
                        <li>Click the "Build Image" button</li>
                        <li>Upload a Dockerfile or create one in the editor</li>
                        <li>Configure build options</li>
                        <li>Click "Build"</li>
                      </ol>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      <div>
                        <v-icon left>mdi-file-document-multiple</v-icon>
                        Docker Compose
                      </div>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <h4 class="subtitle-1 font-weight-bold mb-2">Managing Compose Projects</h4>
                      <p>DockerForge provides a complete interface for Docker Compose:</p>
                      <ul>
                        <li>Create and manage multiple compose projects</li>
                        <li>Edit compose files with syntax highlighting</li>
                        <li>Start and stop compose stacks</li>
                        <li>View logs for all services</li>
                        <li>Scale services up or down</li>
                      </ul>

                      <p>Navigate to the Compose section to get started with multi-container applications.</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- API Reference -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h5 mb-3">API Reference</h3>
                <p>DockerForge provides a comprehensive REST API for programmatic access to all functionality.</p>

                <v-alert
                  color="info"
                  outlined
                  class="mb-4"
                >
                  <div class="d-flex align-center">
                    <v-icon class="mr-3">mdi-information</v-icon>
                    <div>
                      <p class="mb-0">The complete API documentation is available at:</p>
                      <code>/api/docs</code> or <code>/api/redoc</code>
                    </div>
                  </div>
                </v-alert>

                <h4 class="subtitle-1 font-weight-bold mb-2">Authentication</h4>
                <p>The API supports two authentication methods:</p>
                <ul>
                  <li><strong>API Key</strong>: Include your API key in the <code>X-API-Key</code> header</li>
                  <li><strong>JWT Token</strong>: Include a JWT token in the <code>Authorization</code> header</li>
                </ul>

                <h4 class="subtitle-1 font-weight-bold mb-2 mt-4">Example Endpoints</h4>
                <v-simple-table>
                  <template v-slot:default>
                    <thead>
                      <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><code>/api/containers</code></td>
                        <td>GET</td>
                        <td>List all containers</td>
                      </tr>
                      <tr>
                        <td><code>/api/containers/{id}</code></td>
                        <td>GET</td>
                        <td>Get container details</td>
                      </tr>
                      <tr>
                        <td><code>/api/containers/{id}/start</code></td>
                        <td>POST</td>
                        <td>Start a container</td>
                      </tr>
                      <tr>
                        <td><code>/api/images</code></td>
                        <td>GET</td>
                        <td>List all images</td>
                      </tr>
                      <tr>
                        <td><code>/api/images/pull</code></td>
                        <td>POST</td>
                        <td>Pull a new image</td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>

                <v-btn color="primary" class="mt-4" href="/api/docs" target="_blank">
                  <v-icon left>mdi-open-in-new</v-icon>
                  Open API Documentation
                </v-btn>
              </v-card-text>
            </v-card>
          </v-tab-item>

          <!-- FAQ -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <h3 class="text-h5 mb-3">Frequently Asked Questions</h3>

                <v-expansion-panels>
                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      What is DockerForge?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p>DockerForge is a comprehensive web-based Docker management platform that allows you to manage containers, images, volumes, networks, and more through an intuitive interface. It provides advanced features like security scanning, monitoring, and backup management.</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      How do I create a new container?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p>To create a new container:</p>
                      <ol>
                        <li>Navigate to the Containers section</li>
                        <li>Click the "New Container" button</li>
                        <li>Select an image</li>
                        <li>Configure container settings</li>
                        <li>Click "Create"</li>
                      </ol>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      How do I access container logs?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p>To access container logs:</p>
                      <ol>
                        <li>Navigate to the Containers section</li>
                        <li>Click on the container name to open the detail view</li>
                        <li>Select the "Logs" tab</li>
                      </ol>
                      <p>You can also stream logs in real-time and filter them by keywords.</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      How do I scan images for vulnerabilities?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p>To scan an image for vulnerabilities:</p>
                      <ol>
                        <li>Navigate to the Images section</li>
                        <li>Click on the image name to open the detail view</li>
                        <li>Select the "Security" tab</li>
                        <li>Click "Scan Now"</li>
                      </ol>
                      <p>The scan results will show any vulnerabilities found in the image, along with severity ratings and remediation advice.</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      How do I create a backup?
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p>To create a backup:</p>
                      <ol>
                        <li>Navigate to the Backup section</li>
                        <li>Click "Create Backup"</li>
                        <li>Select the resources to back up (containers, volumes, etc.)</li>
                        <li>Configure backup options</li>
                        <li>Click "Start Backup"</li>
                      </ol>
                      <p>You can schedule regular backups in the Backup section.</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>

                <v-card outlined class="mt-6">
                  <v-card-title>
                    <v-icon left>mdi-help-circle</v-icon>
                    Need More Help?
                  </v-card-title>
                  <v-card-text>
                    <p>If you can't find the answer to your question, you can:</p>
                    <ul>
                      <li>Use the AI Assistant by clicking the robot icon in the top bar</li>
                      <li>Check the <a href="https://github.com/NModlin/dockerForge" target="_blank">GitHub repository</a> for documentation</li>
                      <li>Submit an issue on GitHub if you've found a bug</li>
                    </ul>
                  </v-card-text>
                </v-card>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-school</v-icon>
        Guided Tour
      </v-card-title>
      <v-card-text>
        <p>New to DockerForge? Take a guided tour to learn about the key features and how to use them.</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="startTour">
          <v-icon left>mdi-play</v-icon>
          Start Tour
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Keyboard Shortcuts -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-keyboard</v-icon>
        Keyboard Shortcuts
      </v-card-title>
      <v-card-text>
        <keyboard-shortcuts-guide />
      </v-card-text>
    </v-card>

    <!-- Video Tutorials -->
    <v-card class="mb-4">
      <v-card-title>
        <v-icon left>mdi-video</v-icon>
        Video Tutorials
      </v-card-title>
      <v-card-text>
        <video-tutorials />
      </v-card-text>
    </v-card>

    <!-- Troubleshooting Guide -->
    <v-card>
      <v-card-title>
        <v-icon left>mdi-wrench</v-icon>
        Troubleshooting Guide
      </v-card-title>
      <v-card-text>
        <troubleshooting-guide />
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import DocumentationSearch from '@/components/help/DocumentationSearch.vue';
import KeyboardShortcutsGuide from '@/components/help/KeyboardShortcutsGuide.vue';
import VideoTutorials from '@/components/help/VideoTutorials.vue';
import TroubleshootingGuide from '@/components/help/TroubleshootingGuide.vue';

export default {
  name: 'Help',
  components: {
    DocumentationSearch,
    KeyboardShortcutsGuide,
    VideoTutorials,
    TroubleshootingGuide
  },
  data() {
    return {
      activeTab: 0,
    };
  },
  methods: {
    startTour() {
      // Dispatch action to start the guided tour
      this.$store.dispatch('help/startTour');

      // Emit event to show the tour component
      this.$root.$emit('start-guided-tour');
    }
  }
};
</script>

<style scoped>
.help {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
