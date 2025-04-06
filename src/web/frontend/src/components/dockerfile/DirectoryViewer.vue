<template>
  <div class="directory-viewer">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-folder-open</v-icon>
        Build Context Files
        <v-spacer></v-spacer>
        <v-btn
          icon
          small
          @click="expandAll"
          v-tooltip="'Expand all'"
        >
          <v-icon small>mdi-arrow-expand-all</v-icon>
        </v-btn>
        <v-btn
          icon
          small
          @click="collapseAll"
          v-tooltip="'Collapse all'"
        >
          <v-icon small>mdi-arrow-collapse-all</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <div v-if="treeData.length === 0" class="pa-4 text-center">
          <v-icon large color="grey lighten-1">mdi-folder-open-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No files uploaded yet</p>
        </div>
        
        <v-treeview
          v-else
          :items="treeData"
          :open.sync="openNodes"
          activatable
          item-key="id"
          open-on-click
          return-object
          dense
          class="directory-tree"
        >
          <template v-slot:prepend="{ item }">
            <v-icon v-if="item.isDirectory">
              {{ item.open ? 'mdi-folder-open' : 'mdi-folder' }}
            </v-icon>
            <v-icon v-else>
              {{ getFileIcon(item.mimeType) }}
            </v-icon>
          </template>
          
          <template v-slot:append="{ item }">
            <div class="d-flex align-center">
              <span v-if="!item.isDirectory" class="text-caption grey--text mr-2">
                {{ formatFileSize(item.size) }}
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
              <v-btn
                icon
                x-small
                @click.stop="removeItem(item)"
                v-tooltip="'Remove'"
              >
                <v-icon x-small color="error">mdi-delete</v-icon>
              </v-btn>
            </div>
          </template>
        </v-treeview>
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
export default {
  name: 'DirectoryViewer',
  
  props: {
    files: {
      type: Array,
      default: () => []
    },
    ignoredFiles: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      treeData: [],
      openNodes: [],
      previewDialog: false,
      previewFile: null,
      previewContent: null,
      isTextFile: false,
      isImageFile: false
    };
  },
  
  watch: {
    files: {
      handler() {
        this.buildTreeData();
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    buildTreeData() {
      // Reset tree data
      this.treeData = [];
      
      // Create a map to store directories
      const directories = new Map();
      
      // Process each file
      this.files.forEach((file, index) => {
        // Get file path parts
        const pathParts = file.webkitRelativePath 
          ? file.webkitRelativePath.split('/') 
          : ['', file.name];
        
        // Check if file is ignored
        const isIgnored = this.isFileIgnored(pathParts.join('/'));
        
        // Create file node
        const fileNode = {
          id: `file-${index}`,
          name: pathParts[pathParts.length - 1],
          isDirectory: false,
          path: pathParts.join('/'),
          size: file.size,
          mimeType: file.type,
          file: file,
          ignored: isIgnored
        };
        
        // If file is at root level
        if (pathParts.length === 2 && pathParts[0] === '') {
          this.treeData.push(fileNode);
          return;
        }
        
        // Create directory nodes
        let currentPath = '';
        let parentId = null;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
          const part = pathParts[i];
          if (!part) continue;
          
          currentPath = currentPath ? `${currentPath}/${part}` : part;
          const dirId = `dir-${currentPath}`;
          
          if (!directories.has(dirId)) {
            const dirNode = {
              id: dirId,
              name: part,
              isDirectory: true,
              path: currentPath,
              children: []
            };
            
            directories.set(dirId, dirNode);
            
            // Add to parent or root
            if (parentId) {
              const parentNode = directories.get(parentId);
              parentNode.children.push(dirNode);
            } else {
              this.treeData.push(dirNode);
            }
          }
          
          parentId = dirId;
        }
        
        // Add file to its parent directory
        if (parentId) {
          const parentNode = directories.get(parentId);
          parentNode.children.push(fileNode);
        }
      });
      
      // Open all nodes by default
      this.openNodes = Array.from(directories.keys());
    },
    
    isFileIgnored(filePath) {
      // Check if file matches any ignore pattern
      return this.ignoredFiles.some(pattern => {
        // Convert glob pattern to regex
        const regexPattern = pattern
          .replace(/\./g, '\\.')
          .replace(/\*/g, '.*')
          .replace(/\?/g, '.');
        
        const regex = new RegExp(`^${regexPattern}$`);
        return regex.test(filePath);
      });
    },
    
    expandAll() {
      // Get all directory IDs
      const allDirIds = [];
      const findDirs = (nodes) => {
        nodes.forEach(node => {
          if (node.isDirectory) {
            allDirIds.push(node.id);
            if (node.children) {
              findDirs(node.children);
            }
          }
        });
      };
      
      findDirs(this.treeData);
      this.openNodes = allDirIds;
    },
    
    collapseAll() {
      this.openNodes = [];
    },
    
    async previewFile(item) {
      this.previewFile = item;
      this.previewContent = null;
      this.previewDialog = true;
      this.isTextFile = false;
      this.isImageFile = false;
      
      try {
        // Check file type
        if (item.mimeType.startsWith('text/') || 
            item.mimeType === 'application/json' ||
            item.mimeType === 'application/javascript' ||
            item.mimeType === 'application/xml' ||
            item.name.endsWith('.md') ||
            item.name.endsWith('.yml') ||
            item.name.endsWith('.yaml') ||
            item.name.endsWith('.Dockerfile') ||
            item.name === 'Dockerfile') {
          // Text file
          this.isTextFile = true;
          const text = await this.readFileAsText(item.file);
          this.previewContent = text;
        } else if (item.mimeType.startsWith('image/')) {
          // Image file
          this.isImageFile = true;
          const dataUrl = await this.readFileAsDataURL(item.file);
          this.previewContent = dataUrl;
        } else {
          // Unsupported file type
          this.previewContent = 'Preview not available for this file type';
        }
      } catch (error) {
        console.error('Error previewing file:', error);
        this.previewContent = 'Error loading file preview';
      }
    },
    
    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
      });
    },
    
    readFileAsDataURL(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsDataURL(file);
      });
    },
    
    removeItem(item) {
      if (item.isDirectory) {
        // Remove directory and all its contents
        this.$emit('remove-directory', item.path);
      } else {
        // Remove single file
        this.$emit('remove-file', item.file);
      }
    },
    
    getFileIcon(mimeType) {
      if (mimeType.startsWith('image/')) {
        return 'mdi-file-image';
      } else if (mimeType.startsWith('text/')) {
        return 'mdi-file-document';
      } else if (mimeType === 'application/json') {
        return 'mdi-code-json';
      } else if (mimeType === 'application/javascript' || mimeType === 'application/typescript') {
        return 'mdi-language-javascript';
      } else if (mimeType === 'application/x-httpd-php') {
        return 'mdi-language-php';
      } else if (mimeType === 'application/x-python') {
        return 'mdi-language-python';
      } else {
        return 'mdi-file';
      }
    },
    
    formatFileSize(size) {
      if (size < 1024) {
        return `${size} B`;
      } else if (size < 1024 * 1024) {
        return `${(size / 1024).toFixed(2)} KB`;
      } else {
        return `${(size / (1024 * 1024)).toFixed(2)} MB`;
      }
    }
  }
};
</script>

<style scoped>
.directory-viewer {
  width: 100%;
}

.directory-tree {
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
