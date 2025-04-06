<template>
  <div class="template-details">
    <v-card outlined class="mb-4">
      <v-card-text>
        <div class="d-flex align-center mb-3">
          <v-avatar color="primary" size="40" class="mr-3">
            <v-icon dark>{{ getCategoryIcon(template.category) }}</v-icon>
          </v-avatar>
          <div>
            <h3 class="text-h6 mb-0">{{ template.name }}</h3>
            <div class="text-caption grey--text">
              {{ formatCategoryName(template.category) }} Template
            </div>
          </div>
          <v-spacer></v-spacer>
          <v-chip
            :color="getDifficultyColor(template.difficulty)"
            text-color="white"
            small
          >
            {{ template.difficulty }}
          </v-chip>
        </div>
        
        <v-divider class="mb-3"></v-divider>
        
        <p class="text-body-2">{{ template.description }}</p>
        
        <div class="mt-3">
          <v-chip
            v-for="tag in template.tags"
            :key="tag"
            class="mr-1 mb-1"
            small
            outlined
          >
            {{ tag }}
          </v-chip>
        </div>
        
        <v-divider class="my-3"></v-divider>
        
        <div v-if="template.services && template.services.length > 0">
          <h4 class="text-subtitle-2 font-weight-bold mb-2">Services</h4>
          <v-chip
            v-for="service in template.services"
            :key="service"
            class="mr-1 mb-1"
            small
            color="blue lighten-4"
          >
            {{ service }}
          </v-chip>
        </div>
        
        <div v-if="template.variables && template.variables.length > 0" class="mt-3">
          <h4 class="text-subtitle-2 font-weight-bold mb-2">Variables</h4>
          <v-chip
            v-for="variable in template.variables"
            :key="variable"
            class="mr-1 mb-1"
            small
            color="green lighten-4"
          >
            {{ variable }}
          </v-chip>
        </div>
        
        <div v-if="template.created_at || template.updated_at" class="mt-3 text-caption grey--text">
          <div v-if="template.created_at">
            Created: {{ formatDate(template.created_at) }}
          </div>
          <div v-if="template.updated_at">
            Updated: {{ formatDate(template.updated_at) }}
          </div>
        </div>
      </v-card-text>
      
      <v-divider v-if="showActions"></v-divider>
      
      <v-card-actions v-if="showActions">
        <v-btn
          text
          color="primary"
          @click="$emit('preview')"
        >
          <v-icon left>mdi-eye</v-icon>
          Preview
        </v-btn>
        <v-btn
          text
          color="primary"
          @click="$emit('customize')"
        >
          <v-icon left>mdi-pencil</v-icon>
          Customize
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          @click="$emit('select')"
        >
          <v-icon left>mdi-check</v-icon>
          Use Template
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'TemplateDetails',
  
  props: {
    template: {
      type: Object,
      required: true
    },
    showActions: {
      type: Boolean,
      default: true
    }
  },
  
  methods: {
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
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch (error) {
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.template-details {
  width: 100%;
}
</style>
