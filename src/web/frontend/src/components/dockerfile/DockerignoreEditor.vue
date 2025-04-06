<template>
  <div class="dockerignore-editor">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-file-hidden</v-icon>
        .dockerignore
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              icon
              x-small
              class="ml-2"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon x-small>mdi-help-circle</v-icon>
            </v-btn>
          </template>
          <span>
            Specify patterns to exclude files from the build context.<br>
            Each line is a pattern that follows the .gitignore format.
          </span>
        </v-tooltip>
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="addCommonPatterns"
        >
          Add Common Patterns
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-textarea
          v-model="dockerignoreContent"
          outlined
          rows="10"
          placeholder="# Add patterns to exclude files from the build context
# Example:
# .git
# node_modules
# *.log
# dist"
          class="font-family-monospace"
          @input="validateContent"
          hide-details
        ></v-textarea>
        
        <div v-if="validationErrors.length > 0" class="mt-2">
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
        
        <div v-if="ignoredFiles.length > 0" class="mt-4">
          <v-expansion-panels>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left>mdi-eye-off</v-icon>
                  {{ ignoredFiles.length }} files will be ignored
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list dense>
                  <v-list-item v-for="(file, index) in ignoredFiles" :key="index">
                    <v-list-item-icon>
                      <v-icon small>mdi-file-hidden</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>{{ file }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'DockerignoreEditor',
  
  props: {
    value: {
      type: String,
      default: ''
    },
    files: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      dockerignoreContent: '',
      validationErrors: [],
      ignoredFiles: []
    };
  },
  
  watch: {
    value: {
      handler(newValue) {
        if (newValue !== this.dockerignoreContent) {
          this.dockerignoreContent = newValue;
          this.validateContent();
        }
      },
      immediate: true
    },
    
    files: {
      handler() {
        this.updateIgnoredFiles();
      },
      deep: true
    }
  },
  
  methods: {
    validateContent() {
      this.validationErrors = [];
      
      // Split content into lines
      const lines = this.dockerignoreContent.split('\n');
      
      // Check for invalid patterns
      lines.forEach((line, index) => {
        // Skip empty lines and comments
        if (!line.trim() || line.trim().startsWith('#')) {
          return;
        }
        
        // Check for invalid characters
        if (line.includes('\\') && !line.endsWith('\\')) {
          this.validationErrors.push(`Line ${index + 1}: Invalid escape sequence`);
        }
        
        // Check for invalid negation
        if (line.startsWith('!') && line.length === 1) {
          this.validationErrors.push(`Line ${index + 1}: Invalid negation pattern`);
        }
      });
      
      // Update ignored files
      this.updateIgnoredFiles();
      
      // Emit changes
      this.$emit('input', this.dockerignoreContent);
      this.$emit('update:modelValue', this.dockerignoreContent);
      this.$emit('change', this.dockerignoreContent);
    },
    
    updateIgnoredFiles() {
      this.ignoredFiles = [];
      
      if (!this.dockerignoreContent.trim() || !this.files.length) {
        return;
      }
      
      // Get patterns from content
      const patterns = this.dockerignoreContent
        .split('\n')
        .filter(line => line.trim() && !line.trim().startsWith('#'))
        .map(line => line.trim());
      
      // Check each file against patterns
      this.files.forEach(file => {
        const filePath = file.webkitRelativePath || file.name;
        
        if (this.isFileIgnored(filePath, patterns)) {
          this.ignoredFiles.push(filePath);
        }
      });
    },
    
    isFileIgnored(filePath, patterns) {
      // Simple implementation of .dockerignore pattern matching
      // In a real implementation, this would be more sophisticated
      
      let ignored = false;
      
      for (const pattern of patterns) {
        // Handle negation
        if (pattern.startsWith('!')) {
          const negatedPattern = pattern.substring(1);
          if (this.matchPattern(filePath, negatedPattern)) {
            ignored = false;
            continue;
          }
        }
        
        // Regular pattern
        if (this.matchPattern(filePath, pattern)) {
          ignored = true;
        }
      }
      
      return ignored;
    },
    
    matchPattern(filePath, pattern) {
      // Convert glob pattern to regex
      // This is a simplified implementation
      const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*')
        .replace(/\?/g, '.');
      
      const regex = new RegExp(`^${regexPattern}$`);
      
      // Check if file matches pattern
      return regex.test(filePath) || filePath.includes(`/${pattern}`);
    },
    
    addCommonPatterns() {
      const commonPatterns = `# Common patterns for .dockerignore
.git
.gitignore
.github
.vscode
.idea
node_modules
npm-debug.log
yarn-debug.log
yarn-error.log
*.log
*.swp
*.bak
.DS_Store
Thumbs.db
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
dist
build
coverage
.coverage
htmlcov/
.pytest_cache/
.tox/
.nox/
.hypothesis/
.nyc_output
`;

      // Append common patterns to existing content
      if (this.dockerignoreContent.trim()) {
        this.dockerignoreContent += '\n\n' + commonPatterns;
      } else {
        this.dockerignoreContent = commonPatterns;
      }
      
      this.validateContent();
    }
  }
};
</script>

<style scoped>
.dockerignore-editor {
  width: 100%;
}
</style>
