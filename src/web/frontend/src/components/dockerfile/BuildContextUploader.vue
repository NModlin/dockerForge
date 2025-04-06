<template>
  <div class="build-context-uploader">
    <v-card outlined class="upload-zone" :class="{ 'active-drop': isDragging }">
      <div
        class="upload-area pa-6"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click="triggerFileInput"
      >
        <input
          type="file"
          ref="fileInput"
          multiple
          @change="onFileSelected"
          style="display: none"
        />
        <div class="text-center">
          <v-icon size="64" color="primary">mdi-cloud-upload</v-icon>
          <h3 class="text-h5 mt-4">
            Drag and drop files here
          </h3>
          <p class="text-body-1 mt-2">
            or click to select files for your build context
          </p>
          <p class="text-caption mt-4">
            Maximum file size: 10MB per file, 50MB total
          </p>
        </div>
      </div>
    </v-card>

    <div v-if="files.length > 0" class="mt-4">
      <h3 class="text-h6 mb-2">Uploaded Files</h3>
      <v-list dense>
        <v-list-item v-for="(file, index) in files" :key="index">
          <v-list-item-icon>
            <v-icon>{{ getFileIcon(file.type) }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ file.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ formatFileSize(file.size) }}</v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn icon small @click="removeFile(index)">
              <v-icon small color="error">mdi-delete</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
      
      <div class="d-flex justify-end mt-2">
        <v-btn color="error" text @click="clearFiles">
          <v-icon left>mdi-delete-sweep</v-icon>
          Clear All
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BuildContextUploader',
  
  props: {
    value: {
      type: Array,
      default: () => []
    },
    maxFileSize: {
      type: Number,
      default: 10 * 1024 * 1024 // 10MB
    },
    maxTotalSize: {
      type: Number,
      default: 50 * 1024 * 1024 // 50MB
    }
  },
  
  data() {
    return {
      files: [],
      isDragging: false
    };
  },
  
  watch: {
    value: {
      handler(newValue) {
        if (newValue && newValue !== this.files) {
          this.files = newValue;
        }
      },
      immediate: true
    }
  },
  
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    
    onDragOver(event) {
      this.isDragging = true;
    },
    
    onDragLeave(event) {
      this.isDragging = false;
    },
    
    onDrop(event) {
      this.isDragging = false;
      const droppedFiles = event.dataTransfer.files;
      this.processFiles(droppedFiles);
    },
    
    onFileSelected(event) {
      const selectedFiles = event.target.files;
      this.processFiles(selectedFiles);
      // Reset the input to allow selecting the same file again
      this.$refs.fileInput.value = '';
    },
    
    processFiles(fileList) {
      const newFiles = Array.from(fileList);
      
      // Check file sizes
      const oversizedFiles = newFiles.filter(file => file.size > this.maxFileSize);
      if (oversizedFiles.length > 0) {
        this.$emit('error', `Some files exceed the maximum size limit of ${this.formatFileSize(this.maxFileSize)}`);
        return;
      }
      
      // Check total size
      const currentTotalSize = this.files.reduce((total, file) => total + file.size, 0);
      const newTotalSize = newFiles.reduce((total, file) => total + file.size, currentTotalSize);
      if (newTotalSize > this.maxTotalSize) {
        this.$emit('error', `Total size exceeds the maximum limit of ${this.formatFileSize(this.maxTotalSize)}`);
        return;
      }
      
      // Add files to the list
      this.files = [...this.files, ...newFiles];
      this.emitChange();
    },
    
    removeFile(index) {
      this.files.splice(index, 1);
      this.emitChange();
    },
    
    clearFiles() {
      this.files = [];
      this.emitChange();
    },
    
    emitChange() {
      this.$emit('input', this.files);
      this.$emit('update:modelValue', this.files);
      this.$emit('change', this.files);
    },
    
    getFileIcon(fileType) {
      if (fileType.includes('image')) {
        return 'mdi-file-image';
      } else if (fileType.includes('text')) {
        return 'mdi-file-document';
      } else if (fileType.includes('application/json')) {
        return 'mdi-code-json';
      } else if (fileType.includes('application/javascript') || fileType.includes('application/typescript')) {
        return 'mdi-language-javascript';
      } else if (fileType.includes('application/x-httpd-php')) {
        return 'mdi-language-php';
      } else if (fileType.includes('application/x-python')) {
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
.build-context-uploader {
  width: 100%;
}

.upload-zone {
  border: 2px dashed #ccc;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.upload-zone.active-drop {
  border-color: var(--v-primary-base);
  background-color: rgba(var(--v-primary-base), 0.05);
}

.upload-area {
  cursor: pointer;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
