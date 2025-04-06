<template>
  <v-card class="template-ai-assistant">
    <v-card-title class="headline">
      <v-icon left>mdi-robot</v-icon>
      AI-Assisted Template Customization
      <v-spacer></v-spacer>
      <v-btn icon @click="$emit('close')">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    
    <v-divider></v-divider>
    
    <v-card-text class="pa-0">
      <v-container fluid>
        <v-row>
          <!-- Left Panel: Template Info and Instructions -->
          <v-col cols="12" md="5" class="pa-4">
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Template Information</h3>
            <template-details
              :template="template"
              :show-actions="false"
            ></template-details>
            
            <h3 class="text-subtitle-1 font-weight-bold mt-4 mb-3">Customization Instructions</h3>
            <v-textarea
              v-model="instructions"
              outlined
              label="Describe how you want to customize this template"
              hint="Be specific about what changes you want to make"
              persistent-hint
              rows="6"
              counter
              :rules="[v => !!v || 'Instructions are required']"
            ></v-textarea>
            
            <div class="mt-4">
              <h4 class="text-subtitle-2 font-weight-bold mb-2">Suggestion Prompts</h4>
              <v-chip-group column>
                <v-chip
                  v-for="(prompt, index) in suggestionPrompts"
                  :key="index"
                  outlined
                  @click="addSuggestionPrompt(prompt)"
                >
                  {{ prompt }}
                </v-chip>
              </v-chip-group>
            </div>
            
            <v-btn
              color="primary"
              block
              class="mt-4"
              :loading="loading"
              :disabled="!instructions || loading"
              @click="customizeTemplate"
            >
              <v-icon left>mdi-robot</v-icon>
              Generate Customized Template
            </v-btn>
          </v-col>
          
          <!-- Right Panel: Template Preview -->
          <v-col cols="12" md="7" class="pa-0 template-preview-panel">
            <div class="d-flex align-center pa-4">
              <h3 class="text-subtitle-1 font-weight-bold">
                {{ customizedTemplate ? 'Customized Template' : 'Original Template' }}
              </h3>
              <v-spacer></v-spacer>
              <v-btn
                text
                small
                color="primary"
                :disabled="!customizedTemplate"
                @click="copyTemplateContent"
              >
                <v-icon left small>mdi-content-copy</v-icon>
                Copy
              </v-btn>
            </div>
            
            <v-divider></v-divider>
            
            <div class="template-editor-container pa-4">
              <div ref="editor" class="template-editor"></div>
            </div>
            
            <v-divider></v-divider>
            
            <div class="pa-4">
              <v-alert
                v-if="error"
                type="error"
                dense
                dismissible
                class="mb-3"
              >
                {{ error }}
              </v-alert>
              
              <div class="d-flex">
                <v-spacer></v-spacer>
                <v-btn
                  text
                  @click="$emit('close')"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="primary"
                  :disabled="!customizedTemplate"
                  @click="applyTemplate"
                >
                  <v-icon left>mdi-check</v-icon>
                  Apply Template
                </v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
import * as monaco from 'monaco-editor';
import * as yaml from 'js-yaml';
import TemplateDetails from './TemplateDetails.vue';

export default {
  name: 'TemplateAIAssistant',
  
  components: {
    TemplateDetails
  },
  
  props: {
    template: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      instructions: '',
      loading: false,
      error: null,
      editor: null,
      originalTemplate: null,
      customizedTemplate: null,
      suggestionPrompts: [
        'Add environment variables',
        'Add volume mounts',
        'Configure for production',
        'Add health checks',
        'Optimize for performance',
        'Add security settings',
        'Configure networking'
      ]
    };
  },
  
  mounted() {
    this.initEditor();
    this.loadTemplateContent();
  },
  
  beforeDestroy() {
    if (this.editor) {
      this.editor.dispose();
    }
  },
  
  methods: {
    initEditor() {
      // Register YAML language if not already registered
      if (!monaco.languages.getLanguages().some(lang => lang.id === 'yaml')) {
        monaco.languages.register({ id: 'yaml' });
        
        // Define YAML language configuration
        monaco.languages.setMonarchTokensProvider('yaml', {
          tokenizer: {
            root: [
              [/^[\t ]*#.*$/, 'comment'],
              [/^[\t ]*-/, 'delimiter'],
              [/^[\t ]*[\w]+:/, 'type'],
              [/[\w]+:/, 'type'],
              [/[\w]+/, 'string'],
              [/".*?"/, 'string'],
              [/'.*?'/, 'string'],
            ]
          }
        });
      }
      
      // Create Monaco editor
      this.editor = monaco.editor.create(this.$refs.editor, {
        value: '',
        language: 'yaml',
        theme: 'vs',
        automaticLayout: true,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        lineNumbers: 'on',
        renderLineHighlight: 'all',
        tabSize: 2,
        readOnly: false,
        wordWrap: 'on'
      });
    },
    
    async loadTemplateContent() {
      try {
        // Get template content
        const response = await this.$http.get(`/api/compose/templates/${this.template.name}/content`);
        this.originalTemplate = response.data.content;
        
        // Set editor content
        if (this.editor) {
          this.editor.setValue(this.originalTemplate);
        }
      } catch (error) {
        console.error('Failed to get template content:', error);
        this.error = 'Failed to load template content';
      }
    },
    
    addSuggestionPrompt(prompt) {
      if (this.instructions) {
        this.instructions += '\n' + prompt;
      } else {
        this.instructions = prompt;
      }
    },
    
    async customizeTemplate() {
      if (!this.instructions) {
        this.error = 'Please provide customization instructions';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        // Call API to customize template
        const response = await this.$http.post(`/api/compose/templates/${this.template.name}/customize`, {
          instructions: this.instructions
        });
        
        this.customizedTemplate = response.data.content;
        
        // Update editor content
        if (this.editor) {
          this.editor.setValue(this.customizedTemplate);
        }
      } catch (error) {
        console.error('Failed to customize template:', error);
        this.error = error.response?.data?.message || 'Failed to customize template';
      } finally {
        this.loading = false;
      }
    },
    
    copyTemplateContent() {
      const content = this.customizedTemplate || this.originalTemplate;
      if (content) {
        navigator.clipboard.writeText(content);
        this.$emit('success', 'Template content copied to clipboard');
      }
    },
    
    applyTemplate() {
      if (!this.customizedTemplate) {
        this.error = 'No customized template to apply';
        return;
      }
      
      try {
        // Parse YAML to validate
        const parsed = yaml.load(this.customizedTemplate);
        
        // Emit event with customized template
        this.$emit('apply', {
          ...this.template,
          content: this.customizedTemplate,
          customized: true
        });
      } catch (error) {
        console.error('Invalid YAML:', error);
        this.error = `Invalid YAML: ${error.message}`;
      }
    }
  }
};
</script>

<style scoped>
.template-ai-assistant {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.template-preview-panel {
  background-color: #f5f5f5;
  border-left: 1px solid rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.template-editor-container {
  flex: 1;
  min-height: 500px;
}

.template-editor {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
