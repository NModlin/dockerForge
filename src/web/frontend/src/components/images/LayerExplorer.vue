<template>
  <div class="layer-explorer">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-folder-search</v-icon>
        Layer Explorer
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="refreshLayerContent"
          :loading="loading"
        >
          <v-icon left small>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <div v-if="!layers || layers.length === 0" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-folder-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No layer information available</p>
        </div>
        
        <div v-else>
          <div class="layer-selection pa-4">
            <v-select
              v-model="selectedLayerIndex"
              :items="layerItems"
              label="Select Layer"
              outlined
              dense
              @change="onLayerChange"
            ></v-select>
          </div>
          
          <v-divider></v-divider>
          
          <div class="layer-content">
            <div v-if="loading" class="text-center pa-6">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <p class="text-body-2 mt-2">Loading layer content...</p>
            </div>
            
            <div v-else-if="!layerContent || layerContent.length === 0" class="text-center pa-6">
              <v-icon large color="grey lighten-1">mdi-file-outline</v-icon>
              <p class="text-body-2 mt-2 grey--text">No content available for this layer</p>
              <p class="text-caption grey--text">
                This might be an empty layer or content inspection is not available
              </p>
            </div>
            
            <div v-else>
              <!-- Layer Content Explorer -->
              <v-card flat>
                <v-card-text class="pa-0">
                  <v-tabs v-model="activeTab" background-color="primary" dark>
                    <v-tab>Files</v-tab>
                    <v-tab>Changes</v-tab>
                    <v-tab>Metadata</v-tab>
                  </v-tabs>
                  
                  <v-tabs-items v-model="activeTab">
                    <!-- Files Tab -->
                    <v-tab-item>
                      <v-card flat>
                        <v-card-text>
                          <v-text-field
                            v-model="fileSearch"
                            label="Search Files"
                            prepend-icon="mdi-magnify"
                            clearable
                            outlined
                            dense
                          ></v-text-field>
                          
                          <v-treeview
                            :items="fileTree"
                            :search="fileSearch"
                            :open.sync="openNodes"
                            item-key="path"
                            activatable
                            open-on-click
                            return-object
                            dense
                            class="file-tree"
                          >
                            <template v-slot:prepend="{ item }">
                              <v-icon v-if="item.isDirectory">
                                {{ item.open ? 'mdi-folder-open' : 'mdi-folder' }}
                              </v-icon>
                              <v-icon v-else>
                                {{ getFileIcon(item.name) }}
                              </v-icon>
                            </template>
                            
                            <template v-slot:append="{ item }">
                              <div class="d-flex align-center">
                                <span v-if="!item.isDirectory" class="text-caption grey--text mr-2">
                                  {{ formatSize(item.size) }}
                                </span>
                                <v-btn
                                  v-if="!item.isDirectory"
                                  icon
                                  x-small
                                  @click.stop="previewFile(item)"
                                  v-tooltip="'Preview'"
                                >
                                  <v-icon x-small>mdi-eye</v-icon>
                                </v-btn>
                              </div>
                            </template>
                          </v-treeview>
                        </v-card-text>
                      </v-card>
                    </v-tab-item>
                    
                    <!-- Changes Tab -->
                    <v-tab-item>
                      <v-card flat>
                        <v-card-text>
                          <v-simple-table>
                            <template v-slot:default>
                              <thead>
                                <tr>
                                  <th>Type</th>
                                  <th>Path</th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr v-for="(change, index) in layerChanges" :key="index">
                                  <td>
                                    <v-chip
                                      small
                                      :color="getChangeTypeColor(change.type)"
                                      text-color="white"
                                    >
                                      {{ change.type }}
                                    </v-chip>
                                  </td>
                                  <td>{{ change.path }}</td>
                                </tr>
                              </tbody>
                            </template>
                          </v-simple-table>
                        </v-card-text>
                      </v-card>
                    </v-tab-item>
                    
                    <!-- Metadata Tab -->
                    <v-tab-item>
                      <v-card flat>
                        <v-card-text>
                          <v-row>
                            <v-col cols="12" md="6">
                              <v-list dense>
                                <v-list-item>
                                  <v-list-item-content>
                                    <v-list-item-title>Layer ID</v-list-item-title>
                                    <v-list-item-subtitle>{{ selectedLayer?.Id || 'Unknown' }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                                
                                <v-list-item>
                                  <v-list-item-content>
                                    <v-list-item-title>Size</v-list-item-title>
                                    <v-list-item-subtitle>{{ formatSize(selectedLayer?.Size) }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                                
                                <v-list-item v-if="selectedLayer?.Created">
                                  <v-list-item-content>
                                    <v-list-item-title>Created</v-list-item-title>
                                    <v-list-item-subtitle>{{ formatDate(selectedLayer.Created) }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-col>
                            
                            <v-col cols="12" md="6">
                              <v-list dense>
                                <v-list-item v-if="selectedLayer?.CreatedBy">
                                  <v-list-item-content>
                                    <v-list-item-title>Created By</v-list-item-title>
                                    <v-list-item-subtitle>{{ selectedLayer.CreatedBy }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                                
                                <v-list-item v-if="selectedLayer?.Comment">
                                  <v-list-item-content>
                                    <v-list-item-title>Comment</v-list-item-title>
                                    <v-list-item-subtitle>{{ selectedLayer.Comment }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                                
                                <v-list-item>
                                  <v-list-item-content>
                                    <v-list-item-title>Empty Layer</v-list-item-title>
                                    <v-list-item-subtitle>{{ selectedLayer?.Size === 0 ? 'Yes' : 'No' }}</v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-col>
                          </v-row>
                        </v-card-text>
                      </v-card>
                    </v-tab-item>
                  </v-tabs-items>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </div>
      </v-card-text>
    </v-card>
    
    <!-- File Preview Dialog -->
    <v-dialog v-model="previewDialog" max-width="800px">
      <v-card>
        <v-card-title class="headline">
          {{ previewFile ? previewFile.name : '' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="previewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <div v-if="previewContent" class="preview-content">
            <pre v-if="isTextFile"><code>{{ previewContent }}</code></pre>
            <div v-else-if="isImageFile" class="text-center">
              <img :src="previewContent" alt="Preview" class="preview-image" />
            </div>
            <div v-else class="text-center pa-4">
              <v-icon large color="grey lighten-1">mdi-file-document-outline</v-icon>
              <p class="text-body-2 mt-2 grey--text">Preview not available for this file type</p>
            </div>
          </div>
          <div v-else class="text-center pa-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="text-body-2 mt-2">Loading preview...</p>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { format, parseISO } from 'date-fns';

export default {
  name: 'LayerExplorer',
  
  props: {
    layers: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      selectedLayerIndex: 0,
      activeTab: 0,
      loading: false,
      layerContent: [],
      layerChanges: [],
      fileSearch: '',
      openNodes: [],
      previewDialog: false,
      previewFile: null,
      previewContent: null,
      isTextFile: false,
      isImageFile: false
    };
  },
  
  computed: {
    layerItems() {
      return this.layers.map((layer, index) => {
        const command = this.getLayerCommand(layer);
        return {
          text: `Layer ${index + 1}: ${command.substring(0, 50)}${command.length > 50 ? '...' : ''}`,
          value: index
        };
      });
    },
    
    selectedLayer() {
      return this.layers[this.selectedLayerIndex] || null;
    },
    
    fileTree() {
      if (!this.layerContent || this.layerContent.length === 0) {
        return [];
      }
      
      // Create a tree structure from flat file list
      const root = {
        name: '/',
        path: '/',
        isDirectory: true,
        children: []
      };
      
      const directoryMap = new Map();
      directoryMap.set('/', root);
      
      // Sort files to process directories first
      const sortedFiles = [...this.layerContent].sort((a, b) => {
        const aIsDir = a.isDirectory;
        const bIsDir = b.isDirectory;
        if (aIsDir && !bIsDir) return -1;
        if (!aIsDir && bIsDir) return 1;
        return a.path.localeCompare(b.path);
      });
      
      // Process each file
      sortedFiles.forEach(file => {
        const pathParts = file.path.split('/').filter(part => part);
        let currentPath = '';
        let parentPath = '/';
        
        // Create parent directories if they don't exist
        for (let i = 0; i < pathParts.length - 1; i++) {
          const part = pathParts[i];
          currentPath = currentPath ? `${currentPath}/${part}` : `/${part}`;
          
          if (!directoryMap.has(currentPath)) {
            const dirNode = {
              name: part,
              path: currentPath,
              isDirectory: true,
              children: []
            };
            
            directoryMap.set(currentPath, dirNode);
            
            // Add to parent
            const parent = directoryMap.get(parentPath);
            parent.children.push(dirNode);
          }
          
          parentPath = currentPath;
        }
        
        // Add the file to its parent directory
        if (file.isDirectory) {
          // This is a directory that might already be in the map
          const dirPath = file.path;
          if (!directoryMap.has(dirPath)) {
            const dirNode = {
              name: pathParts[pathParts.length - 1],
              path: dirPath,
              isDirectory: true,
              children: []
            };
            
            directoryMap.set(dirPath, dirNode);
            
            // Add to parent
            const parent = directoryMap.get(parentPath);
            parent.children.push(dirNode);
          }
        } else {
          // This is a regular file
          const fileNode = {
            name: pathParts[pathParts.length - 1],
            path: file.path,
            isDirectory: false,
            size: file.size,
            content: file.content
          };
          
          // Add to parent
          const parent = directoryMap.get(parentPath);
          parent.children.push(fileNode);
        }
      });
      
      return [root];
    }
  },
  
  watch: {
    layers: {
      handler() {
        if (this.layers && this.layers.length > 0) {
          this.selectedLayerIndex = 0;
          this.onLayerChange();
        }
      },
      immediate: true
    }
  },
  
  methods: {
    onLayerChange() {
      this.refreshLayerContent();
    },
    
    async refreshLayerContent() {
      if (!this.selectedLayer) return;
      
      this.loading = true;
      
      try {
        // In a real implementation, this would call an API to get layer content
        // For now, we'll simulate the response with mock data
        await this.simulateLayerContent();
      } catch (error) {
        console.error('Error loading layer content:', error);
        this.layerContent = [];
        this.layerChanges = [];
      } finally {
        this.loading = false;
      }
    },
    
    async simulateLayerContent() {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate mock layer content based on the layer command
      const command = this.getLayerCommand(this.selectedLayer);
      
      // Generate mock files
      this.layerContent = [];
      this.layerChanges = [];
      
      if (command.includes('COPY') || command.includes('ADD')) {
        // Simulate copied files
        const files = [
          { path: '/app', isDirectory: true, size: 0 },
          { path: '/app/package.json', isDirectory: false, size: 1024, content: '{\n  "name": "app",\n  "version": "1.0.0"\n}' },
          { path: '/app/src', isDirectory: true, size: 0 },
          { path: '/app/src/index.js', isDirectory: false, size: 2048, content: 'console.log("Hello World");' }
        ];
        
        this.layerContent = files;
        
        // Simulate changes
        this.layerChanges = [
          { type: 'ADD', path: '/app' },
          { type: 'ADD', path: '/app/package.json' },
          { type: 'ADD', path: '/app/src' },
          { type: 'ADD', path: '/app/src/index.js' }
        ];
      } else if (command.includes('RUN')) {
        // Simulate installed packages or created files
        const files = [
          { path: '/usr/local/lib', isDirectory: true, size: 0 },
          { path: '/usr/local/lib/node_modules', isDirectory: true, size: 0 },
          { path: '/usr/local/lib/node_modules/express', isDirectory: true, size: 0 },
          { path: '/usr/local/lib/node_modules/express/package.json', isDirectory: false, size: 1536, content: '{\n  "name": "express",\n  "version": "4.17.1"\n}' },
          { path: '/var/cache/apt', isDirectory: true, size: 0 },
          { path: '/var/cache/apt/archives', isDirectory: true, size: 0 }
        ];
        
        this.layerContent = files;
        
        // Simulate changes
        this.layerChanges = [
          { type: 'MODIFY', path: '/usr/local/lib' },
          { type: 'ADD', path: '/usr/local/lib/node_modules' },
          { type: 'ADD', path: '/usr/local/lib/node_modules/express' },
          { type: 'ADD', path: '/usr/local/lib/node_modules/express/package.json' },
          { type: 'MODIFY', path: '/var/cache/apt' },
          { type: 'ADD', path: '/var/cache/apt/archives' }
        ];
      } else if (command.includes('WORKDIR')) {
        // Simulate workdir creation
        const workdir = command.split(' ')[1];
        
        this.layerContent = [
          { path: workdir, isDirectory: true, size: 0 }
        ];
        
        // Simulate changes
        this.layerChanges = [
          { type: 'ADD', path: workdir }
        ];
      } else if (command.includes('ENV')) {
        // Environment variables don't create files
        this.layerContent = [];
        
        // Simulate changes
        this.layerChanges = [
          { type: 'ENV', path: command.replace('ENV ', '') }
        ];
      } else {
        // Default empty layer
        this.layerContent = [];
        this.layerChanges = [];
      }
    },
    
    getLayerCommand(layer) {
      if (!layer) return 'Unknown';
      
      // Extract command from CreatedBy field
      if (layer.CreatedBy) {
        // Remove "/bin/sh -c " prefix if present
        let command = layer.CreatedBy;
        if (command.startsWith('/bin/sh -c ')) {
          command = command.substring('/bin/sh -c '.length);
        }
        
        // Remove "#(nop) " prefix if present
        if (command.startsWith('#(nop) ')) {
          command = command.substring('#(nop) '.length);
        }
        
        return command;
      }
      
      // Fallback to comment if available
      if (layer.Comment) {
        return layer.Comment;
      }
      
      return 'Unknown';
    },
    
    getChangeTypeColor(type) {
      switch (type) {
        case 'ADD':
          return 'success';
        case 'MODIFY':
          return 'warning';
        case 'DELETE':
          return 'error';
        case 'ENV':
          return 'info';
        default:
          return 'grey';
      }
    },
    
    getFileIcon(fileName) {
      const extension = fileName.split('.').pop().toLowerCase();
      
      switch (extension) {
        case 'js':
          return 'mdi-language-javascript';
        case 'py':
          return 'mdi-language-python';
        case 'html':
          return 'mdi-language-html5';
        case 'css':
          return 'mdi-language-css3';
        case 'json':
          return 'mdi-code-json';
        case 'md':
          return 'mdi-markdown';
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
          return 'mdi-file-image';
        case 'pdf':
          return 'mdi-file-pdf';
        case 'doc':
        case 'docx':
          return 'mdi-file-word';
        case 'xls':
        case 'xlsx':
          return 'mdi-file-excel';
        case 'ppt':
        case 'pptx':
          return 'mdi-file-powerpoint';
        case 'zip':
        case 'tar':
        case 'gz':
          return 'mdi-zip-box';
        default:
          return 'mdi-file';
      }
    },
    
    async previewFile(file) {
      this.previewFile = file;
      this.previewContent = null;
      this.previewDialog = true;
      this.isTextFile = false;
      this.isImageFile = false;
      
      try {
        // In a real implementation, this would call an API to get file content
        // For now, we'll use the mock content
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        const extension = file.name.split('.').pop().toLowerCase();
        
        // Check file type
        if (['js', 'py', 'html', 'css', 'json', 'md', 'txt', 'sh', 'Dockerfile'].includes(extension)) {
          // Text file
          this.isTextFile = true;
          this.previewContent = file.content || 'File content not available';
        } else if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
          // Image file
          this.isImageFile = true;
          // In a real implementation, this would be a data URL or a URL to the image
          this.previewContent = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
        } else {
          // Unsupported file type
          this.previewContent = 'Preview not available for this file type';
        }
      } catch (error) {
        console.error('Error previewing file:', error);
        this.previewContent = 'Error loading file preview';
      }
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
.layer-explorer {
  width: 100%;
}

.layer-selection {
  background-color: #f5f5f5;
}

.file-tree {
  max-height: 400px;
  overflow-y: auto;
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
  font-family: monospace;
}

.preview-image {
  max-width: 100%;
  max-height: 500px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}
</style>
