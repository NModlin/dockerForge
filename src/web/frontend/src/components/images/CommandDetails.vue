<template>
  <div class="command-details">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-code-braces</v-icon>
        Command Details
        <v-spacer></v-spacer>
        <v-btn
          v-if="command"
          text
          small
          color="primary"
          @click="copyCommand"
        >
          <v-icon left small>mdi-content-copy</v-icon>
          Copy
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <div v-if="!command" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-code-braces-box</v-icon>
          <p class="text-body-2 mt-2 grey--text">Select a command from the timeline to view details</p>
        </div>
        
        <div v-else>
          <v-row>
            <v-col cols="12">
              <div class="text-h6 d-flex align-center">
                <v-avatar
                  size="32"
                  :color="commandColor"
                  class="mr-2"
                >
                  <v-icon dark small>{{ commandIcon }}</v-icon>
                </v-avatar>
                {{ commandType }}
              </div>
              
              <v-card outlined class="mt-4 command-card">
                <v-card-text class="pa-0">
                  <pre class="command-code">{{ formattedCommand }}</pre>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title class="text-subtitle-2">
                  <v-icon left small>mdi-information</v-icon>
                  Command Information
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text>
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-title>Type</v-list-item-title>
                        <v-list-item-subtitle>{{ commandType }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-title>Size Impact</v-list-item-title>
                        <v-list-item-subtitle>{{ formatSize(commandItem.Size) }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-title>Created</v-list-item-title>
                        <v-list-item-subtitle>{{ formatDate(commandItem.Created) }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-list-item v-if="commandItem.Comment">
                      <v-list-item-content>
                        <v-list-item-title>Comment</v-list-item-title>
                        <v-list-item-subtitle>{{ commandItem.Comment }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title class="text-subtitle-2">
                  <v-icon left small>mdi-help-circle</v-icon>
                  Command Explanation
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text>
                  <p>{{ commandExplanation }}</p>
                  
                  <div v-if="commandImpact" class="mt-4">
                    <div class="text-subtitle-2">Impact</div>
                    <p>{{ commandImpact }}</p>
                  </div>
                  
                  <div v-if="commandBestPractices" class="mt-4">
                    <div class="text-subtitle-2">Best Practices</div>
                    <p>{{ commandBestPractices }}</p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
    
    <!-- Snackbar for copy notification -->
    <v-snackbar v-model="snackbar" :timeout="2000" color="success">
      Command copied to clipboard
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { format, parseISO } from 'date-fns';

export default {
  name: 'CommandDetails',
  
  props: {
    commandItem: {
      type: Object,
      default: null
    }
  },
  
  data() {
    return {
      snackbar: false
    };
  },
  
  computed: {
    command() {
      if (!this.commandItem || !this.commandItem.CreatedBy) return null;
      
      // Extract command from CreatedBy field
      let command = this.commandItem.CreatedBy;
      
      // Remove "/bin/sh -c " prefix if present
      if (command.startsWith('/bin/sh -c ')) {
        command = command.substring('/bin/sh -c '.length);
      }
      
      // Remove "#(nop) " prefix if present
      if (command.startsWith('#(nop) ')) {
        command = command.substring('#(nop) '.length);
      }
      
      return command;
    },
    
    formattedCommand() {
      if (!this.command) return '';
      
      // Format the command for better readability
      let formatted = this.command;
      
      // Add syntax highlighting (simplified version)
      const commandType = this.commandType;
      
      if (commandType === 'RUN') {
        // Highlight RUN commands
        formatted = formatted.replace(/^RUN\s+/, 'RUN ');
      } else if (commandType === 'COPY' || commandType === 'ADD') {
        // Highlight COPY/ADD commands
        formatted = formatted.replace(/^(COPY|ADD)\s+/, '$1 ');
      } else if (commandType === 'ENV') {
        // Highlight ENV commands
        formatted = formatted.replace(/^ENV\s+([^\s=]+)=/, 'ENV $1=');
      }
      
      return formatted;
    },
    
    commandType() {
      if (!this.commandItem || !this.commandItem.CreatedBy) return 'Unknown';
      
      const command = this.commandItem.CreatedBy;
      
      if (command.includes('#(nop)')) {
        // Non-operation commands (metadata)
        if (command.includes('FROM')) return 'FROM';
        if (command.includes('LABEL')) return 'LABEL';
        if (command.includes('MAINTAINER')) return 'MAINTAINER';
        if (command.includes('EXPOSE')) return 'EXPOSE';
        if (command.includes('ENV')) return 'ENV';
        if (command.includes('ENTRYPOINT')) return 'ENTRYPOINT';
        if (command.includes('CMD')) return 'CMD';
        if (command.includes('VOLUME')) return 'VOLUME';
        if (command.includes('USER')) return 'USER';
        if (command.includes('WORKDIR')) return 'WORKDIR';
        if (command.includes('ARG')) return 'ARG';
        if (command.includes('ONBUILD')) return 'ONBUILD';
        if (command.includes('STOPSIGNAL')) return 'STOPSIGNAL';
        if (command.includes('HEALTHCHECK')) return 'HEALTHCHECK';
        if (command.includes('SHELL')) return 'SHELL';
        return 'Metadata';
      } else {
        // Operation commands
        if (command.includes('RUN')) return 'RUN';
        if (command.includes('COPY')) return 'COPY';
        if (command.includes('ADD')) return 'ADD';
        return 'Operation';
      }
    },
    
    commandIcon() {
      switch (this.commandType) {
        case 'FROM':
          return 'mdi-package-variant';
        case 'RUN':
          return 'mdi-console';
        case 'COPY':
        case 'ADD':
          return 'mdi-file-multiple';
        case 'ENV':
          return 'mdi-variable';
        case 'WORKDIR':
          return 'mdi-folder';
        case 'EXPOSE':
          return 'mdi-network';
        case 'VOLUME':
          return 'mdi-database';
        case 'ENTRYPOINT':
        case 'CMD':
          return 'mdi-play';
        case 'USER':
          return 'mdi-account';
        case 'LABEL':
          return 'mdi-tag';
        case 'ARG':
          return 'mdi-key-variant';
        case 'HEALTHCHECK':
          return 'mdi-heart-pulse';
        default:
          return 'mdi-docker';
      }
    },
    
    commandColor() {
      switch (this.commandType) {
        case 'FROM':
          return '#4CAF50'; // Green
        case 'RUN':
          return '#FF5722'; // Deep Orange
        case 'COPY':
        case 'ADD':
          return '#2196F3'; // Blue
        case 'ENV':
          return '#9C27B0'; // Purple
        case 'WORKDIR':
          return '#795548'; // Brown
        case 'EXPOSE':
          return '#00BCD4'; // Cyan
        case 'VOLUME':
          return '#3F51B5'; // Indigo
        case 'ENTRYPOINT':
        case 'CMD':
          return '#FFC107'; // Amber
        case 'USER':
          return '#E91E63'; // Pink
        case 'LABEL':
          return '#607D8B'; // Blue Grey
        case 'ARG':
          return '#8BC34A'; // Light Green
        case 'HEALTHCHECK':
          return '#F44336'; // Red
        default:
          return '#9E9E9E'; // Grey
      }
    },
    
    commandExplanation() {
      switch (this.commandType) {
        case 'FROM':
          return 'The FROM instruction initializes a new build stage and sets the base image for subsequent instructions. This is typically the first instruction in a Dockerfile.';
        case 'RUN':
          return 'The RUN instruction executes commands in a new layer on top of the current image and commits the results. The resulting committed image will be used for the next step in the Dockerfile.';
        case 'COPY':
          return 'The COPY instruction copies new files or directories from the build context and adds them to the filesystem of the container at the specified path.';
        case 'ADD':
          return 'The ADD instruction copies new files, directories, or remote file URLs from the build context and adds them to the filesystem of the container at the specified path.';
        case 'ENV':
          return 'The ENV instruction sets environment variables that will be available to containers launched from the resulting image.';
        case 'WORKDIR':
          return 'The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY, and ADD instructions that follow it in the Dockerfile.';
        case 'EXPOSE':
          return 'The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. It does not actually publish the ports.';
        case 'VOLUME':
          return 'The VOLUME instruction creates a mount point with the specified name and marks it as holding externally mounted volumes from native host or other containers.';
        case 'ENTRYPOINT':
          return 'The ENTRYPOINT instruction configures a container that will run as an executable. It specifies the command that will always be executed when the container starts.';
        case 'CMD':
          return 'The CMD instruction provides defaults for an executing container. These defaults can include an executable, or they can omit the executable, in which case you must specify an ENTRYPOINT instruction.';
        case 'USER':
          return 'The USER instruction sets the user name or UID to use when running the image and for any RUN, CMD and ENTRYPOINT instructions that follow it in the Dockerfile.';
        case 'LABEL':
          return 'The LABEL instruction adds metadata to an image as key-value pairs. Labels are useful for organizing images by project, license, or any other metadata you want to include.';
        case 'ARG':
          return 'The ARG instruction defines a variable that users can pass at build-time to the builder with the docker build command using the --build-arg flag.';
        case 'HEALTHCHECK':
          return 'The HEALTHCHECK instruction tells Docker how to test a container to check that it is still working. This can detect cases such as a web server that is stuck in an infinite loop and unable to handle new connections.';
        default:
          return 'This command modifies the Docker image by adding or changing files, configurations, or metadata.';
      }
    },
    
    commandImpact() {
      switch (this.commandType) {
        case 'RUN':
          return `This command added ${this.formatSize(this.commandItem.Size)} to the image size. RUN commands typically create new layers that can significantly impact the final image size.`;
        case 'COPY':
        case 'ADD':
          return `This command added ${this.formatSize(this.commandItem.Size)} to the image size by copying files into the container filesystem.`;
        case 'FROM':
          return 'This command sets the base image, which determines the starting point for your container. The choice of base image significantly impacts the final image size and security profile.';
        case 'ENV':
          return 'Environment variables are stored in the image metadata and do not significantly impact image size. They will be available to all containers created from this image.';
        case 'WORKDIR':
          return 'Setting the working directory creates the directory if it doesn\'t exist, but typically has minimal impact on image size.';
        default:
          return this.commandItem.Size > 0 
            ? `This command added ${this.formatSize(this.commandItem.Size)} to the image size.` 
            : 'This command had no significant impact on the image size.';
      }
    },
    
    commandBestPractices() {
      switch (this.commandType) {
        case 'RUN':
          return 'Combine multiple RUN commands into a single instruction to reduce the number of layers. Use multi-stage builds to keep build dependencies out of the final image.';
        case 'COPY':
          return 'Prefer COPY over ADD for simple file copying. Use .dockerignore to exclude files that are not needed in the build context.';
        case 'ADD':
          return 'Use ADD only when you need its tar auto-extraction capability or for downloading remote resources. For simple file copying, COPY is preferred.';
        case 'FROM':
          return 'Use specific version tags instead of "latest" to ensure reproducible builds. Consider using smaller base images like alpine variants to reduce image size.';
        case 'ENV':
          return 'Group related environment variables in a single ENV instruction to reduce layers. Use ARG for build-time variables that should not persist in the final image.';
        case 'WORKDIR':
          return 'Always use absolute paths for WORKDIR. Avoid using RUN cd /some/path as it doesn\'t change the working directory for subsequent instructions.';
        case 'CMD':
        case 'ENTRYPOINT':
          return 'Use the JSON array format (["executable", "param1", "param2"]) to avoid unexpected shell behavior. Prefer ENTRYPOINT for defining the main executable and CMD for default arguments.';
        case 'USER':
          return 'Create the user and group before using them in the USER instruction. Avoid running containers as root when possible for better security.';
        default:
          return 'Follow the principle of least privilege and minimize the number of layers to create efficient and secure Docker images.';
      }
    }
  },
  
  methods: {
    copyCommand() {
      if (!this.command) return;
      
      // Copy command to clipboard
      navigator.clipboard.writeText(this.command)
        .then(() => {
          this.snackbar = true;
        })
        .catch(err => {
          console.error('Failed to copy command: ', err);
        });
    },
    
    formatSize(size) {
      if (size === undefined || size === null) return 'Unknown';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let formattedSize = size;
      let unitIndex = 0;
      
      while (formattedSize >= 1024 && unitIndex < units.length - 1) {
        formattedSize /= 1024;
        unitIndex++;
      }
      
      return `${formattedSize.toFixed(2)} ${units[unitIndex]}`;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
      try {
        // Check if dateString is a timestamp
        if (typeof dateString === 'number') {
          return format(new Date(dateString * 1000), 'MMM d, yyyy HH:mm');
        }
        
        // Otherwise, parse as ISO string
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
      } catch (error) {
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.command-details {
  width: 100%;
}

.command-card {
  background-color: #1e1e1e;
  overflow: hidden;
}

.command-code {
  padding: 16px;
  margin: 0;
  color: #f0f0f0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
