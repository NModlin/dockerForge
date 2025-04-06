<template>
  <div class="dockerfile-editor">
    <div class="editor-container" ref="editorContainer"></div>
    <div v-if="validationErrors.length > 0" class="validation-errors mt-2">
      <v-alert
        v-for="(error, index) in validationErrors"
        :key="index"
        type="error"
        dense
        text
        class="mb-1"
      >
        {{ error }}
      </v-alert>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DockerfileEditor',
  
  props: {
    value: {
      type: String,
      default: ''
    },
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      editor: null,
      monaco: null,
      validationErrors: [],
      defaultDockerfileContent: `# Use an official base image
FROM node:14-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Define command to run the application
CMD ["npm", "start"]
`
    };
  },
  
  watch: {
    value(newValue) {
      if (this.editor && newValue !== this.editor.getValue()) {
        this.editor.setValue(newValue);
      }
    }
  },
  
  mounted() {
    this.initMonaco();
  },
  
  beforeUnmount() {
    if (this.editor) {
      this.editor.dispose();
    }
  },
  
  methods: {
    async initMonaco() {
      // We'll need to dynamically import Monaco Editor
      // For now, we'll use a placeholder implementation
      // In a real implementation, we would use:
      // const monaco = await import('monaco-editor');
      // this.monaco = monaco;
      
      // For now, we'll use a textarea as a placeholder
      const editorContainer = this.$refs.editorContainer;
      const textarea = document.createElement('textarea');
      textarea.style.width = '100%';
      textarea.style.height = '400px';
      textarea.style.fontFamily = 'monospace';
      textarea.value = this.value || this.defaultDockerfileContent;
      textarea.readOnly = this.readOnly;
      
      textarea.addEventListener('input', () => {
        this.$emit('input', textarea.value);
        this.$emit('update:modelValue', textarea.value);
        this.validateDockerfile(textarea.value);
      });
      
      editorContainer.appendChild(textarea);
      this.editor = {
        getValue: () => textarea.value,
        setValue: (value) => {
          textarea.value = value;
        },
        dispose: () => {
          editorContainer.removeChild(textarea);
        }
      };
      
      // Initial validation
      this.validateDockerfile(this.value || this.defaultDockerfileContent);
    },
    
    async validateDockerfile(content) {
      try {
        // In a real implementation, we would call an API endpoint
        // For now, we'll do some basic validation
        this.validationErrors = [];
        
        const lines = content.split('\n');
        let hasFrom = false;
        
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          
          // Skip comments and empty lines
          if (line.startsWith('#') || line === '') {
            continue;
          }
          
          // Check for FROM instruction
          if (line.startsWith('FROM ')) {
            hasFrom = true;
          }
          
          // Check for invalid instructions
          const instruction = line.split(' ')[0].toUpperCase();
          const validInstructions = ['FROM', 'RUN', 'CMD', 'LABEL', 'MAINTAINER', 'EXPOSE', 
                                    'ENV', 'ADD', 'COPY', 'ENTRYPOINT', 'VOLUME', 'USER', 
                                    'WORKDIR', 'ARG', 'ONBUILD', 'STOPSIGNAL', 'HEALTHCHECK', 'SHELL'];
          
          if (!validInstructions.includes(instruction)) {
            this.validationErrors.push(`Line ${i + 1}: Unknown instruction: ${instruction}`);
          }
        }
        
        if (!hasFrom) {
          this.validationErrors.push('Dockerfile must contain at least one FROM instruction');
        }
        
      } catch (error) {
        console.error('Error validating Dockerfile:', error);
        this.validationErrors = ['Error validating Dockerfile'];
      }
    }
  }
};
</script>

<style scoped>
.dockerfile-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-container {
  width: 100%;
  height: 400px;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
}

.validation-errors {
  max-height: 150px;
  overflow-y: auto;
}
</style>
