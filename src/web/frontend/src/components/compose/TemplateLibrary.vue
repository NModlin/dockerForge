<template>
  <div class="template-library">
    <v-card>
      <v-card-title class="headline">
        <v-icon left>mdi-file-document-multiple</v-icon>
        Template Library
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search templates"
          single-line
          hide-details
          class="mx-4"
          dense
          outlined
        ></v-text-field>
        <v-btn color="primary" @click="closeDialog">
          <v-icon left>mdi-close</v-icon>
          Close
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <v-container fluid class="pa-0">
          <v-row no-gutters>
            <!-- Categories Sidebar -->
            <v-col cols="3" class="categories-sidebar">
              <v-list dense nav>
                <v-list-item
                  @click="selectedCategory = 'all'"
                  :class="{ 'v-item--active': selectedCategory === 'all' }"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-view-grid</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>All Templates</v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-chip x-small>{{ filteredTemplates.length }}</v-chip>
                  </v-list-item-action>
                </v-list-item>
                
                <v-divider></v-divider>
                
                <v-list-item
                  v-for="category in categories"
                  :key="category.name"
                  @click="selectedCategory = category.name"
                  :class="{ 'v-item--active': selectedCategory === category.name }"
                >
                  <v-list-item-icon>
                    <v-icon>{{ getCategoryIcon(category.name) }}</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ formatCategoryName(category.name) }}</v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-chip x-small>{{ category.count }}</v-chip>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
              
              <v-divider></v-divider>
              
              <div class="pa-3">
                <v-btn block color="primary" @click="showImportDialog = true">
                  <v-icon left>mdi-import</v-icon>
                  Import Template
                </v-btn>
              </div>
            </v-col>
            
            <!-- Templates List -->
            <v-col cols="9" class="templates-list">
              <v-container fluid>
                <v-row>
                  <v-col cols="12">
                    <div class="d-flex align-center mb-3">
                      <h3 class="text-subtitle-1 font-weight-bold">
                        {{ formatCategoryName(selectedCategory) }} Templates
                      </h3>
                      <v-spacer></v-spacer>
                      <v-btn-toggle v-model="viewMode" mandatory dense>
                        <v-btn small value="grid">
                          <v-icon small>mdi-view-grid</v-icon>
                        </v-btn>
                        <v-btn small value="list">
                          <v-icon small>mdi-view-list</v-icon>
                        </v-btn>
                      </v-btn-toggle>
                    </div>
                  </v-col>
                </v-row>
                
                <!-- Grid View -->
                <v-row v-if="viewMode === 'grid'">
                  <v-col
                    v-for="template in displayedTemplates"
                    :key="template.name"
                    cols="12"
                    sm="6"
                    md="4"
                  >
                    <v-card
                      outlined
                      hover
                      class="template-card"
                      @click="selectTemplate(template)"
                    >
                      <v-card-title class="text-subtitle-1">
                        {{ template.name }}
                        <v-spacer></v-spacer>
                        <v-chip
                          x-small
                          :color="getDifficultyColor(template.difficulty)"
                          text-color="white"
                        >
                          {{ template.difficulty }}
                        </v-chip>
                      </v-card-title>
                      <v-card-text>
                        <div class="template-description">{{ template.description }}</div>
                        <div class="mt-2">
                          <v-chip
                            v-for="tag in template.tags.slice(0, 3)"
                            :key="tag"
                            x-small
                            class="mr-1 mb-1"
                          >
                            {{ tag }}
                          </v-chip>
                          <v-chip
                            v-if="template.tags.length > 3"
                            x-small
                            class="mr-1 mb-1"
                          >
                            +{{ template.tags.length - 3 }}
                          </v-chip>
                        </div>
                      </v-card-text>
                      <v-divider></v-divider>
                      <v-card-actions>
                        <v-btn
                          text
                          small
                          color="primary"
                          @click.stop="previewTemplate(template)"
                        >
                          <v-icon left small>mdi-eye</v-icon>
                          Preview
                        </v-btn>
                        <v-spacer></v-spacer>
                        <v-btn
                          text
                          small
                          color="primary"
                          @click.stop="customizeTemplate(template)"
                        >
                          <v-icon left small>mdi-pencil</v-icon>
                          Customize
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>
                
                <!-- List View -->
                <v-row v-else>
                  <v-col cols="12">
                    <v-list>
                      <v-list-item
                        v-for="template in displayedTemplates"
                        :key="template.name"
                        @click="selectTemplate(template)"
                      >
                        <v-list-item-icon>
                          <v-icon>{{ getCategoryIcon(template.category) }}</v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                          <v-list-item-title>{{ template.name }}</v-list-item-title>
                          <v-list-item-subtitle>{{ template.description }}</v-list-item-subtitle>
                          <div>
                            <v-chip
                              v-for="tag in template.tags.slice(0, 3)"
                              :key="tag"
                              x-small
                              class="mr-1 mt-1"
                            >
                              {{ tag }}
                            </v-chip>
                          </div>
                        </v-list-item-content>
                        <v-list-item-action>
                          <v-chip
                            x-small
                            :color="getDifficultyColor(template.difficulty)"
                            text-color="white"
                          >
                            {{ template.difficulty }}
                          </v-chip>
                        </v-list-item-action>
                        <v-list-item-action>
                          <v-btn icon @click.stop="previewTemplate(template)">
                            <v-icon>mdi-eye</v-icon>
                          </v-btn>
                        </v-list-item-action>
                        <v-list-item-action>
                          <v-btn icon @click.stop="customizeTemplate(template)">
                            <v-icon>mdi-pencil</v-icon>
                          </v-btn>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
                
                <!-- No Templates Message -->
                <v-row v-if="displayedTemplates.length === 0">
                  <v-col cols="12" class="text-center pa-5">
                    <v-icon size="64" color="grey lighten-1">mdi-file-document-outline</v-icon>
                    <h3 class="text-subtitle-1 grey--text text--darken-1 mt-3">
                      No templates found
                    </h3>
                    <p class="grey--text">
                      {{ search ? 'Try a different search term' : 'No templates available in this category' }}
                    </p>
                  </v-col>
                </v-row>
              </v-container>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
    
    <!-- Template Preview Dialog -->
    <v-dialog v-model="previewDialog" max-width="800px">
      <v-card>
        <v-card-title class="headline">
          <v-icon left>mdi-eye</v-icon>
          Template Preview: {{ selectedTemplate ? selectedTemplate.name : '' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="previewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <template-details
            v-if="selectedTemplate"
            :template="selectedTemplate"
            :show-actions="false"
          ></template-details>
          
          <div class="mt-4">
            <div class="d-flex align-center mb-2">
              <h3 class="text-subtitle-1 font-weight-bold">Template Content</h3>
              <v-spacer></v-spacer>
              <v-btn
                small
                text
                color="primary"
                @click="copyTemplateContent"
              >
                <v-icon left small>mdi-content-copy</v-icon>
                Copy
              </v-btn>
            </div>
            <v-sheet
              outlined
              class="code-preview pa-3"
              style="max-height: 400px; overflow-y: auto; font-family: monospace;"
            >
              <pre>{{ templateContent }}</pre>
            </v-sheet>
          </div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="selectTemplate(selectedTemplate)"
          >
            <v-icon left>mdi-check</v-icon>
            Use This Template
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Template Customization Dialog -->
    <v-dialog v-model="customizeDialog" max-width="1000px" persistent>
      <template-ai-assistant
        v-if="selectedTemplate"
        :template="selectedTemplate"
        @close="customizeDialog = false"
        @apply="applyCustomizedTemplate"
      ></template-ai-assistant>
    </v-dialog>
    
    <!-- Import Template Dialog -->
    <v-dialog v-model="showImportDialog" max-width="600px">
      <v-card>
        <v-card-title class="headline">
          <v-icon left>mdi-import</v-icon>
          Import Template
          <v-spacer></v-spacer>
          <v-btn icon @click="showImportDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form ref="importForm" v-model="importFormValid">
            <v-file-input
              v-model="importFile"
              label="Template File"
              accept=".yml,.yaml,.json"
              outlined
              dense
              :rules="[v => !!v || 'Template file is required']"
            ></v-file-input>
            
            <v-text-field
              v-model="importName"
              label="Template Name"
              outlined
              dense
              hint="Leave blank to use filename"
              persistent-hint
            ></v-text-field>
            
            <v-select
              v-model="importCategory"
              :items="categories.map(c => c.name)"
              label="Category"
              outlined
              dense
              :rules="[v => !!v || 'Category is required']"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="showImportDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :loading="importing"
            :disabled="!importFormValid || importing"
            @click="importTemplate"
          >
            <v-icon left>mdi-import</v-icon>
            Import
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import TemplateDetails from './TemplateDetails.vue';
import TemplateAIAssistant from './TemplateAIAssistant.vue';

export default {
  name: 'TemplateLibrary',
  
  components: {
    TemplateDetails,
    TemplateAIAssistant
  },
  
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      search: '',
      selectedCategory: 'all',
      viewMode: 'grid',
      templates: [],
      selectedTemplate: null,
      previewDialog: false,
      customizeDialog: false,
      templateContent: '',
      showImportDialog: false,
      importFile: null,
      importName: '',
      importCategory: 'custom',
      importFormValid: false,
      importing: false
    };
  },
  
  computed: {
    filteredTemplates() {
      let filtered = this.templates;
      
      // Filter by category
      if (this.selectedCategory !== 'all') {
        filtered = filtered.filter(t => t.category === this.selectedCategory);
      }
      
      // Filter by search term
      if (this.search) {
        const searchLower = this.search.toLowerCase();
        filtered = filtered.filter(t => 
          t.name.toLowerCase().includes(searchLower) ||
          t.description.toLowerCase().includes(searchLower) ||
          t.tags.some(tag => tag.toLowerCase().includes(searchLower))
        );
      }
      
      return filtered;
    },
    
    displayedTemplates() {
      return this.filteredTemplates;
    },
    
    categories() {
      // Get unique categories and count templates in each
      const categoryCounts = {};
      
      this.templates.forEach(template => {
        if (!categoryCounts[template.category]) {
          categoryCounts[template.category] = 0;
        }
        categoryCounts[template.category]++;
      });
      
      // Convert to array of objects
      return Object.keys(categoryCounts).map(name => ({
        name,
        count: categoryCounts[name]
      })).sort((a, b) => a.name.localeCompare(b.name));
    }
  },
  
  watch: {
    value(newVal) {
      if (newVal) {
        this.loadTemplates();
      }
    }
  },
  
  mounted() {
    if (this.value) {
      this.loadTemplates();
    }
  },
  
  methods: {
    async loadTemplates() {
      try {
        // Call API to get templates
        const response = await this.$http.get('/api/compose/templates');
        this.templates = response.data;
      } catch (error) {
        console.error('Failed to load templates:', error);
        this.$emit('error', 'Failed to load templates');
      }
    },
    
    formatCategoryName(category) {
      if (!category) return '';
      return category.charAt(0).toUpperCase() + category.slice(1);
    },
    
    getCategoryIcon(category) {
      const icons = {
        web: 'mdi-web',
        database: 'mdi-database',
        cache: 'mdi-memory',
        messaging: 'mdi-message-processing',
        monitoring: 'mdi-chart-line',
        development: 'mdi-code-braces',
        production: 'mdi-server',
        testing: 'mdi-test-tube',
        infrastructure: 'mdi-server-network',
        custom: 'mdi-puzzle'
      };
      
      return icons[category] || 'mdi-file-document';
    },
    
    getDifficultyColor(difficulty) {
      const colors = {
        beginner: 'green',
        intermediate: 'orange',
        advanced: 'red'
      };
      
      return colors[difficulty] || 'blue';
    },
    
    async previewTemplate(template) {
      this.selectedTemplate = template;
      
      try {
        // Get template content
        const response = await this.$http.get(`/api/compose/templates/${template.name}/content`);
        this.templateContent = response.data.content;
        this.previewDialog = true;
      } catch (error) {
        console.error('Failed to get template content:', error);
        this.$emit('error', 'Failed to get template content');
      }
    },
    
    customizeTemplate(template) {
      this.selectedTemplate = template;
      this.customizeDialog = true;
    },
    
    selectTemplate(template) {
      this.$emit('select', template);
      this.closeDialog();
    },
    
    applyCustomizedTemplate(customizedTemplate) {
      this.$emit('select', customizedTemplate);
      this.customizeDialog = false;
      this.closeDialog();
    },
    
    copyTemplateContent() {
      navigator.clipboard.writeText(this.templateContent);
      this.$emit('success', 'Template content copied to clipboard');
    },
    
    async importTemplate() {
      if (!this.$refs.importForm.validate()) return;
      
      this.importing = true;
      
      try {
        // Create form data
        const formData = new FormData();
        formData.append('file', this.importFile);
        
        if (this.importName) {
          formData.append('name', this.importName);
        }
        
        formData.append('category', this.importCategory);
        
        // Call API to import template
        await this.$http.post('/api/compose/templates/import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Reload templates
        await this.loadTemplates();
        
        this.$emit('success', 'Template imported successfully');
        this.showImportDialog = false;
      } catch (error) {
        console.error('Failed to import template:', error);
        this.$emit('error', 'Failed to import template');
      } finally {
        this.importing = false;
      }
    },
    
    closeDialog() {
      this.$emit('input', false);
    }
  }
};
</script>

<style scoped>
.template-library {
  height: 100%;
}

.categories-sidebar {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
  height: 100%;
  max-height: 600px;
  overflow-y: auto;
}

.templates-list {
  height: 100%;
  max-height: 600px;
  overflow-y: auto;
}

.template-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.template-description {
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.code-preview {
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style>
