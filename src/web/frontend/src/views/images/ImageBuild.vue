<template>
  <div class="image-build">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-docker</v-icon>
              Build Docker Image
            </v-card-title>

            <v-card-text>
              <v-tabs v-model="activeTab">
                <v-tab>
                  <v-icon left>mdi-file-code</v-icon>
                  Dockerfile
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-folder</v-icon>
                  Build Context
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-cog</v-icon>
                  Build Options
                </v-tab>
              </v-tabs>

              <v-tabs-items v-model="activeTab">
                <!-- Dockerfile Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <dockerfile-editor
                        v-model="dockerfile"
                        @update:modelValue="dockerfile = $event"
                      />
                    </v-card-text>
                  </v-card>
                </v-tab-item>

                <!-- Build Context Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-alert
                        type="info"
                        text
                        class="mb-4"
                      >
                        The build context is the set of files that will be available during the build process.
                      </v-alert>

                      <v-row>
                        <v-col cols="12" md="6">
                          <build-context-uploader
                            v-model="contextFiles"
                            @error="showError"
                            @change="updateIgnoredFiles"
                            :disabled="building"
                          />
                        </v-col>

                        <v-col cols="12" md="6">
                          <directory-viewer
                            :files="contextFiles"
                            :ignored-files="ignoredPatterns"
                            @remove-file="removeFile"
                            @remove-directory="removeDirectory"
                          />
                        </v-col>
                      </v-row>

                      <v-row class="mt-4">
                        <v-col cols="12">
                          <dockerignore-editor
                            v-model="dockerignore"
                            :files="contextFiles"
                            @change="updateIgnoredFiles"
                          />
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-tab-item>

                <!-- Build Options Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <tag-editor
                            v-model="tagConfig"
                            :disabled="building"
                            @change="updateTagConfig"
                          />
                        </v-col>

                        <v-col cols="12" md="6">
                          <build-args-editor
                            v-model="buildArgs"
                            :disabled="building"
                            @change="updateBuildArgs"
                          />
                        </v-col>
                      </v-row>

                      <v-row class="mt-4">
                        <v-col cols="12">
                          <build-options-editor
                            v-model="buildOptions"
                            :disabled="building"
                            @change="updateBuildOptions"
                          />
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>

              <v-divider class="my-4"></v-divider>

              <v-row>
                <v-col cols="12">
                  <v-btn
                    color="primary"
                    :loading="building"
                    :disabled="!isFormValid"
                    @click="buildImage"
                  >
                    <v-icon left>mdi-hammer-wrench</v-icon>
                    Build Image
                  </v-btn>

                  <v-btn
                    text
                    color="grey darken-1"
                    class="ml-2"
                    :disabled="building"
                    @click="resetForm"
                  >
                    Reset
                  </v-btn>
                </v-col>
              </v-row>

              <!-- Build Progress -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <build-progress-tracker
                    :building="building"
                    :build-status="buildStatus"
                    :logs="buildLogs"
                    :start-time="buildStartTime"
                    :end-time="buildEndTime"
                    :total-steps="totalBuildSteps"
                    :current-step="currentBuildStep"
                    @cancel="cancelBuild"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import DockerfileEditor from '@/components/dockerfile/DockerfileEditor.vue';
import BuildContextUploader from '@/components/dockerfile/BuildContextUploader.vue';
import DirectoryViewer from '@/components/dockerfile/DirectoryViewer.vue';
import DockerignoreEditor from '@/components/dockerfile/DockerignoreEditor.vue';
import TagEditor from '@/components/dockerfile/TagEditor.vue';
import BuildArgsEditor from '@/components/dockerfile/BuildArgsEditor.vue';
import BuildOptionsEditor from '@/components/dockerfile/BuildOptionsEditor.vue';
import BuildProgressTracker from '@/components/dockerfile/BuildProgressTracker.vue';

export default {
  name: 'ImageBuild',

  components: {
    DockerfileEditor,
    BuildContextUploader,
    DirectoryViewer,
    DockerignoreEditor,
    TagEditor,
    BuildArgsEditor,
    BuildOptionsEditor,
    BuildProgressTracker
  },

  data() {
    return {
      activeTab: 0,
      dockerfile: '',
      contextFiles: [],
      dockerignore: '',
      ignoredPatterns: [],
      tagConfig: {
        name: '',
        tags: ['latest']
      },
      buildArgs: {},
      buildOptions: {
        noCache: false,
        pull: false,
        rm: true
      },
      building: false,
      buildLogs: [],
      buildError: null,
      buildStatus: null, // null, 'success', 'error'
      buildStartTime: null,
      buildEndTime: null,
      totalBuildSteps: 8, // Default number of steps
      currentBuildStep: 0
    };
  },

  computed: {
    isFormValid() {
      return this.dockerfile && this.tagConfig.name && this.tagConfig.tags.length > 0;
    },

    imageName() {
      return this.tagConfig.name;
    },

    imageTag() {
      return this.tagConfig.tags[0] || 'latest';
    }
  },

  methods: {
    ...mapActions({
      // These actions will need to be implemented in the store
      buildImageAction: 'images/buildImage',
      showSnackbar: 'showSnackbar'
    }),

    async buildImage() {
      if (!this.isFormValid) {
        return;
      }

      this.building = true;
      this.buildLogs = [];
      this.buildError = null;
      this.buildStatus = null;
      this.buildStartTime = new Date();
      this.buildEndTime = null;
      this.currentBuildStep = 0;

      try {
        // Add initial log entry
        this.buildLogs.push(`Starting build for ${this.imageName}:${this.imageTag}...`);

        // Prepare build options
        const buildData = {
          dockerfile: this.dockerfile,
          name: this.imageName,
          tag: this.imageTag,
          options: {
            ...this.buildOptions,
            buildArgs: this.buildArgs
          }
        };

        // In a real implementation, we would call the API to build the image
        // For now, we'll simulate the build process
        await this.simulateBuild();

        // Set build status to success
        this.buildStatus = 'success';
        this.buildEndTime = new Date();

        this.showSnackbar({
          text: `Successfully built image ${this.imageName}:${this.imageTag}`,
          color: 'success'
        });

        // Don't navigate away automatically so user can see the build results
        // this.$router.push('/images');
      } catch (error) {
        console.error('Error building image:', error);
        this.buildError = error.message || 'Failed to build image';
        this.buildLogs.push(`Error: ${this.buildError}`);

        // Set build status to error
        this.buildStatus = 'error';
        this.buildEndTime = new Date();

        this.showSnackbar({
          text: `Failed to build image: ${this.buildError}`,
          color: 'error'
        });
      } finally {
        this.building = false;
      }
    },

    cancelBuild() {
      if (!this.building) return;

      // In a real implementation, we would call the API to cancel the build
      this.buildLogs.push('Build cancelled by user');
      this.buildStatus = 'error';
      this.buildEndTime = new Date();
      this.building = false;

      this.showSnackbar({
        text: 'Build cancelled',
        color: 'warning'
      });
    },

    resetForm() {
      this.dockerfile = '';
      this.contextFiles = [];
      this.dockerignore = '';
      this.ignoredPatterns = [];
      this.tagConfig = {
        name: '',
        tags: ['latest']
      };
      this.buildArgs = {};
      this.buildOptions = {
        noCache: false,
        pull: false,
        rm: true
      };
      this.buildLogs = [];
      this.buildError = null;
    },

    updateTagConfig(config) {
      this.tagConfig = config;
    },

    updateBuildArgs(args) {
      this.buildArgs = args;
    },

    updateBuildOptions(options) {
      this.buildOptions = options;
    },

    updateIgnoredFiles() {
      // Parse dockerignore content to get patterns
      if (!this.dockerignore.trim()) {
        this.ignoredPatterns = [];
        return;
      }

      this.ignoredPatterns = this.dockerignore
        .split('\n')
        .filter(line => line.trim() && !line.trim().startsWith('#'))
        .map(line => line.trim());
    },

    removeFile(file) {
      const index = this.contextFiles.findIndex(f => f === file);
      if (index !== -1) {
        this.contextFiles.splice(index, 1);
      }
    },

    removeDirectory(dirPath) {
      // Remove all files in the directory
      this.contextFiles = this.contextFiles.filter(file => {
        const filePath = file.webkitRelativePath || file.name;
        return !filePath.startsWith(dirPath + '/') && filePath !== dirPath;
      });
    },

    showError(message) {
      this.showSnackbar({
        text: message,
        color: 'error'
      });
    },

    // This is a placeholder for the actual build process
    async simulateBuild() {
      const steps = [
        'Sending build context to Docker daemon',
        'Step 1/8 : FROM node:14-alpine',
        ' ---> Using cache',
        'Step 2/8 : WORKDIR /app',
        ' ---> Using cache',
        'Step 3/8 : COPY package*.json ./',
        ' ---> 3a1f5c7b9e2d',
        'Step 4/8 : RUN npm install',
        ' ---> Running in 4b2e8c1d9f3a',
        'npm WARN deprecated core-js@2.6.12: core-js@<3.23.3 is no longer maintained and not recommended for usage due to the number of issues.',
        'added 1221 packages, and audited 1222 packages in 25s',
        '121 packages are looking for funding',
        'found 0 vulnerabilities',
        ' ---> 7c9e5d2b1f8a',
        'Step 5/8 : COPY . .',
        ' ---> 6b3d9c8a7f2e',
        'Step 6/8 : EXPOSE 3000',
        ' ---> Running in 2d1e9f8c7b3a',
        ' ---> 5a4b3c2d1e9f',
        'Step 7/8 : CMD ["npm", "start"]',
        ' ---> Running in 8c7b6a5d4e3f',
        ' ---> 1f2e3d4c5b6a',
        'Successfully built 1f2e3d4c5b6a',
        `Successfully tagged ${this.imageName}:${this.imageTag}`
      ];

      this.totalBuildSteps = 8;
      this.currentBuildStep = 0;

      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 500));
        this.buildLogs.push(steps[i]);

        // Update current step based on the log line
        if (steps[i].startsWith('Step ')) {
          const stepMatch = steps[i].match(/Step (\d+)\/(\d+)/);
          if (stepMatch) {
            this.currentBuildStep = parseInt(stepMatch[1]);
          }
        }
      }
    }
  }
};
</script>

<style scoped>
.image-build {
  padding: 16px;
}

.build-logs {
  max-height: 300px;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #f0f0f0;
}

.log-content {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 0.9rem;
  line-height: 1.4;
}
</style>
