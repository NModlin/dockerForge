<template>
  <div class="compose-editor">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-file-code</v-icon>
              {{ isNewFile ? 'Create Compose File' : 'Edit Compose File' }}
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Compose Files
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-form ref="form" v-model="valid" @submit.prevent="saveComposeFile">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="composeFile.name"
                      label="Project Name"
                      :rules="[v => !!v || 'Project name is required']"
                      required
                      outlined
                      dense
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="composeFile.path"
                      label="File Path"
                      :rules="[v => !!v || 'File path is required']"
                      required
                      outlined
                      dense
                      hint="e.g., /path/to/docker-compose.yml"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                </v-row>
                
                <v-row>
                  <v-col cols="12">
                    <v-textarea
                      v-model="composeFile.description"
                      label="Description"
                      outlined
                      dense
                      rows="2"
                      auto-grow
                    ></v-textarea>
                  </v-col>
                </v-row>
                
                <v-row>
                  <v-col cols="12">
                    <div class="editor-container">
                      <div class="editor-header d-flex align-center pa-2">
                        <v-icon left>mdi-code-yaml</v-icon>
                        <span class="text-subtitle-2">docker-compose.yml</span>
                        <v-spacer></v-spacer>
                        <v-btn
                          small
                          text
                          color="primary"
                          @click="formatYaml"
                          :disabled="!composeFile.content"
                        >
                          <v-icon left small>mdi-format-align-left</v-icon>
                          Format
                        </v-btn>
                        <v-btn
                          small
                          text
                          color="primary"
                          @click="validateYaml"
                          :disabled="!composeFile.content"
                        >
                          <v-icon left small>mdi-check-circle</v-icon>
                          Validate
                        </v-btn>
                        <v-btn
                          small
                          text
                          color="primary"
                          @click="loadTemplate"
                        >
                          <v-icon left small>mdi-file-document</v-icon>
                          Load Template
                        </v-btn>
                      </div>
                      
                      <div class="editor-wrapper">
                        <div ref="editor" class="monaco-editor"></div>
                      </div>
                      
                      <div v-if="validationErrors.length > 0" class="validation-errors pa-2">
                        <div class="text-subtitle-2 mb-2">Validation Errors</div>
                        <v-list dense>
                          <v-list-item
                            v-for="(error, index) in validationErrors"
                            :key="index"
                            class="error-item"
                            @click="goToLine(error.line)"
                          >
                            <v-list-item-icon>
                              <v-icon color="error">mdi-alert-circle</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              <v-list-item-title>Line {{ error.line }}: {{ error.message }}</v-list-item-title>
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </div>
                    </div>
                  </v-col>
                </v-row>
                
                <v-row class="mt-4">
                  <v-col cols="12" class="text-right">
                    <v-btn
                      color="primary"
                      large
                      :disabled="!valid || saving"
                      :loading="saving"
                      type="submit"
                    >
                      <v-icon left>mdi-content-save</v-icon>
                      {{ isNewFile ? 'Create' : 'Save' }}
                    </v-btn>

                    <v-btn
                      text
                      large
                      color="grey darken-1"
                      class="ml-4"
                      @click="resetForm"
                      :disabled="saving"
                    >
                      Reset
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Template Library Dialog -->
    <template-library
      v-model="templateDialog"
      @select="selectTemplate"
      @error="showError"
      @success="showSuccess"
    ></template-library>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="5000"
      bottom
      right
    >
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import * as monaco from 'monaco-editor';
import * as yaml from 'js-yaml';
import TemplateLibrary from '../../components/compose/TemplateLibrary.vue';

// Register YAML language
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

// Define YAML completion provider
monaco.languages.registerCompletionItemProvider('yaml', {
  provideCompletionItems: function(model, position) {
    const textUntilPosition = model.getValueInRange({
      startLineNumber: position.lineNumber,
      startColumn: 1,
      endLineNumber: position.lineNumber,
      endColumn: position.column
    });
    
    const suggestions = [];
    
    // Top-level keywords
    if (position.column === 1 || textUntilPosition.trim() === '') {
      suggestions.push(
        {
          label: 'version',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'version: \'3\'',
          documentation: 'Compose file version'
        },
        {
          label: 'services',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'services:\n  ',
          documentation: 'Container services'
        },
        {
          label: 'networks',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'networks:\n  ',
          documentation: 'Network definitions'
        },
        {
          label: 'volumes',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'volumes:\n  ',
          documentation: 'Volume definitions'
        }
      );
    }
    
    // Service properties
    if (textUntilPosition.includes('services:')) {
      suggestions.push(
        {
          label: 'image',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'image: ',
          documentation: 'Docker image to use'
        },
        {
          label: 'build',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'build: ',
          documentation: 'Build configuration'
        },
        {
          label: 'ports',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'ports:\n    - ',
          documentation: 'Port mappings'
        },
        {
          label: 'environment',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'environment:\n    - ',
          documentation: 'Environment variables'
        },
        {
          label: 'volumes',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'volumes:\n    - ',
          documentation: 'Volume mappings'
        },
        {
          label: 'depends_on',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'depends_on:\n    - ',
          documentation: 'Service dependencies'
        },
        {
          label: 'networks',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'networks:\n    - ',
          documentation: 'Networks to join'
        }
      );
    }
    
    return { suggestions };
  }
});

export default {
  name: 'ComposeEditor',
  
  components: {
    TemplateLibrary
  },
  
  data() {
    return {
      valid: false,
      saving: false,
      editor: null,
      composeFile: {
        name: '',
        path: '',
        description: '',
        content: ''
      },
      validationErrors: [],
      templateDialog: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  computed: {
    ...mapState('compose', ['composeFiles', 'loading']),
    
    isNewFile() {
      return !this.$route.params.id;
    },
    
    fileId() {
      return this.$route.params.id;
    }
  },
  
  mounted() {
    this.initEditor();
    
    if (!this.isNewFile) {
      this.loadComposeFile();
    }
  },
  
  beforeDestroy() {
    if (this.editor) {
      this.editor.dispose();
    }
  },
  
  methods: {
    ...mapActions('compose', [
      'getComposeFile',
      'createComposeFile',
      'updateComposeFile'
    ]),
    
    initEditor() {
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
        wordWrap: 'on'
      });
      
      // Listen for content changes
      this.editor.onDidChangeModelContent(() => {
        this.composeFile.content = this.editor.getValue();
      });
      
      // Set initial content
      if (this.composeFile.content) {
        this.editor.setValue(this.composeFile.content);
      }
    },
    
    async loadComposeFile() {
      try {
        const composeFile = await this.getComposeFile(this.fileId);
        
        this.composeFile = {
          name: composeFile.name,
          path: composeFile.path,
          description: composeFile.description,
          content: composeFile.content
        };
        
        // Update editor content
        if (this.editor && this.composeFile.content) {
          this.editor.setValue(this.composeFile.content);
        }
      } catch (error) {
        this.showError(`Failed to load compose file: ${error.message}`);
      }
    },
    
    goBack() {
      this.$router.push({ name: 'ComposeList' });
    },
    
    resetForm() {
      if (this.isNewFile) {
        this.composeFile = {
          name: '',
          path: '',
          description: '',
          content: ''
        };
        
        if (this.editor) {
          this.editor.setValue('');
        }
      } else {
        this.loadComposeFile();
      }
      
      this.validationErrors = [];
      this.$refs.form.resetValidation();
    },
    
    formatYaml() {
      try {
        const content = this.editor.getValue();
        const parsed = yaml.load(content);
        const formatted = yaml.dump(parsed, {
          indent: 2,
          lineWidth: -1,
          noRefs: true
        });
        
        this.editor.setValue(formatted);
        this.showSuccess('YAML formatted successfully');
      } catch (error) {
        this.showError(`Failed to format YAML: ${error.message}`);
      }
    },
    
    validateYaml() {
      try {
        const content = this.editor.getValue();
        yaml.load(content);
        
        // Check for required fields
        const parsed = yaml.load(content);
        this.validationErrors = [];
        
        if (!parsed) {
          this.validationErrors.push({
            line: 1,
            message: 'Empty YAML document'
          });
        } else {
          if (!parsed.version) {
            this.validationErrors.push({
              line: 1,
              message: 'Missing required field: version'
            });
          }
          
          if (!parsed.services) {
            this.validationErrors.push({
              line: 1,
              message: 'Missing required field: services'
            });
          } else if (Object.keys(parsed.services).length === 0) {
            this.validationErrors.push({
              line: 1,
              message: 'No services defined'
            });
          }
        }
        
        if (this.validationErrors.length === 0) {
          this.showSuccess('YAML validation successful');
        }
      } catch (error) {
        this.validationErrors = [{
          line: 1,
          message: error.message
        }];
      }
    },
    
    goToLine(lineNumber) {
      if (this.editor) {
        this.editor.revealLineInCenter(lineNumber);
        this.editor.setPosition({ lineNumber, column: 1 });
        this.editor.focus();
      }
    },
    
    loadTemplate() {
      this.templateDialog = true;
    },
    
    selectTemplate(template) {
      if (this.editor) {
        this.editor.setValue(template.content);
        this.composeFile.content = template.content;
      }
      
      this.templateDialog = false;
      this.showSuccess(`Template '${template.name}' loaded successfully`);
    },
    
    async handleSaveComposeFile() {
      if (!this.valid) return;
      
      // Validate YAML before saving
      try {
        yaml.load(this.composeFile.content);
      } catch (error) {
        this.showError(`Invalid YAML: ${error.message}`);
        return;
      }
      
      this.saving = true;
      
      try {
        if (this.isNewFile) {
          // Create new compose file
          await this.createComposeFile({
            name: this.composeFile.name,
            path: this.composeFile.path,
            description: this.composeFile.description,
            content: this.composeFile.content
          });
          
          this.showSuccess('Compose file created successfully');
          this.$router.push({ name: 'ComposeList' });
        } else {
          // Update existing compose file
          await this.updateComposeFile({
            fileId: this.fileId,
            fileData: {
              name: this.composeFile.name,
              path: this.composeFile.path,
              description: this.composeFile.description,
              content: this.composeFile.content
            }
          });
          
          this.showSuccess('Compose file updated successfully');
        }
      } catch (error) {
        this.showError(`Failed to save compose file: ${error.message}`);
      } finally {
        this.saving = false;
      }
    },
    
    async saveComposeFile() {
      await this.handleSaveComposeFile();
    },
    
    showSuccess(message) {
      this.snackbarText = message;
      this.snackbarColor = 'success';
      this.snackbar = true;
    },
    
    showError(message) {
      this.snackbarText = message;
      this.snackbarColor = 'error';
      this.snackbar = true;
    }
  }
};
</script>

<style>
.compose-editor {
  height: 100%;
}

.editor-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.editor-header {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.editor-wrapper {
  height: 500px;
  width: 100%;
}

.monaco-editor {
  height: 100%;
  width: 100%;
}

.validation-errors {
  background-color: #ffebee;
  border-top: 1px solid #e0e0e0;
  max-height: 200px;
  overflow-y: auto;
}

.error-item {
  cursor: pointer;
}

.error-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
