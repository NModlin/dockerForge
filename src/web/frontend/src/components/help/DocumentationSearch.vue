<template>
  <div class="documentation-search">
    <v-text-field
      v-model="searchQuery"
      label="Search documentation"
      prepend-icon="mdi-magnify"
      clearable
      outlined
      dense
      hide-details
      @keydown.enter="performSearch"
    ></v-text-field>
    
    <div v-if="isSearching" class="text-center my-4">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <p class="mt-2">Searching documentation...</p>
    </div>
    
    <div v-else-if="searchResults.length > 0" class="search-results mt-4">
      <v-subheader>{{ searchResults.length }} results found</v-subheader>
      
      <v-list two-line>
        <v-list-item
          v-for="(result, i) in searchResults"
          :key="i"
          @click="navigateToResult(result)"
        >
          <v-list-item-icon>
            <v-icon>{{ getResultIcon(result.type) }}</v-icon>
          </v-list-item-icon>
          
          <v-list-item-content>
            <v-list-item-title v-html="highlightMatch(result.title)"></v-list-item-title>
            <v-list-item-subtitle v-html="highlightMatch(result.snippet)"></v-list-item-subtitle>
            <div class="caption text--secondary mt-1">
              {{ result.category }} • {{ result.section }}
            </div>
          </v-list-item-content>
          
          <v-list-item-action>
            <v-btn icon>
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </div>
    
    <div v-else-if="hasSearched" class="text-center my-4">
      <v-icon size="64" color="grey lighten-1">mdi-file-search-outline</v-icon>
      <p class="mt-2">No results found for "{{ searchQuery }}"</p>
      <p class="subtitle-2 grey--text">Try different keywords or browse the documentation categories</p>
    </div>
    
    <div v-else-if="!searchQuery" class="text-center my-4">
      <v-icon size="64" color="grey lighten-1">mdi-book-search-outline</v-icon>
      <p class="mt-2">Search the documentation</p>
      <p class="subtitle-2 grey--text">Enter keywords to find help on specific topics</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DocumentationSearch',
  data() {
    return {
      searchQuery: '',
      isSearching: false,
      hasSearched: false,
      searchResults: [],
      // Mock documentation data for demonstration
      documentationData: [
        {
          id: 'dashboard-overview',
          title: 'Dashboard Overview',
          content: 'The Dashboard provides an overview of your Docker environment, including container status, resource usage, and recent events.',
          type: 'guide',
          category: 'User Guide',
          section: 'Dashboard',
          path: '/help/user-guide/dashboard'
        },
        {
          id: 'container-management',
          title: 'Container Management',
          content: 'Learn how to create, start, stop, and manage Docker containers using DockerForge.',
          type: 'guide',
          category: 'User Guide',
          section: 'Containers',
          path: '/help/user-guide/containers'
        },
        {
          id: 'image-management',
          title: 'Image Management',
          content: 'Learn how to pull, build, and manage Docker images using DockerForge.',
          type: 'guide',
          category: 'User Guide',
          section: 'Images',
          path: '/help/user-guide/images'
        },
        {
          id: 'security-scanning',
          title: 'Security Scanning',
          content: 'Learn how to scan containers and images for vulnerabilities and remediate security issues.',
          type: 'guide',
          category: 'User Guide',
          section: 'Security',
          path: '/help/user-guide/security'
        },
        {
          id: 'resource-monitoring',
          title: 'Resource Monitoring',
          content: 'Monitor CPU, memory, disk, and network usage of your Docker containers and host system.',
          type: 'guide',
          category: 'User Guide',
          section: 'Monitoring',
          path: '/help/user-guide/monitoring'
        },
        {
          id: 'compose-projects',
          title: 'Docker Compose Projects',
          content: 'Manage multi-container applications using Docker Compose in DockerForge.',
          type: 'guide',
          category: 'User Guide',
          section: 'Compose',
          path: '/help/user-guide/compose'
        },
        {
          id: 'api-reference',
          title: 'API Reference',
          content: 'Complete reference for the DockerForge REST API endpoints and parameters.',
          type: 'reference',
          category: 'API Documentation',
          section: 'Reference',
          path: '/help/api/reference'
        },
        {
          id: 'keyboard-shortcuts',
          title: 'Keyboard Shortcuts',
          content: 'List of keyboard shortcuts for efficient navigation and operation in DockerForge.',
          type: 'reference',
          category: 'User Guide',
          section: 'Reference',
          path: '/help/user-guide/shortcuts'
        },
        {
          id: 'troubleshooting',
          title: 'Troubleshooting Guide',
          content: 'Solutions to common problems and issues when using DockerForge.',
          type: 'guide',
          category: 'User Guide',
          section: 'Troubleshooting',
          path: '/help/user-guide/troubleshooting'
        },
        {
          id: 'chat-commands',
          title: 'Chat Commands Reference',
          content: 'List of available commands for the AI Chat Assistant in DockerForge.',
          type: 'reference',
          category: 'AI Assistant',
          section: 'Reference',
          path: '/help/ai-assistant/commands'
        }
      ]
    };
  },
  methods: {
    performSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = [];
        this.hasSearched = false;
        return;
      }
      
      this.isSearching = true;
      this.hasSearched = true;
      
      // Simulate API delay
      setTimeout(() => {
        const query = this.searchQuery.toLowerCase();
        
        // Search in documentation data
        this.searchResults = this.documentationData
          .filter(item => {
            return (
              item.title.toLowerCase().includes(query) ||
              item.content.toLowerCase().includes(query) ||
              item.category.toLowerCase().includes(query) ||
              item.section.toLowerCase().includes(query)
            );
          })
          .map(item => {
            // Create a snippet from the content
            let snippet = item.content;
            const queryIndex = item.content.toLowerCase().indexOf(query);
            
            if (queryIndex > 30) {
              snippet = '...' + item.content.substring(queryIndex - 30);
            }
            
            if (snippet.length > 120) {
              snippet = snippet.substring(0, 120) + '...';
            }
            
            return {
              ...item,
              snippet
            };
          });
        
        this.isSearching = false;
      }, 500);
    },
    
    navigateToResult(result) {
      this.$router.push(result.path);
      this.$emit('result-selected', result);
    },
    
    getResultIcon(type) {
      switch (type) {
        case 'guide': return 'mdi-book-open-page-variant';
        case 'reference': return 'mdi-text-box';
        case 'tutorial': return 'mdi-school';
        case 'faq': return 'mdi-frequently-asked-questions';
        default: return 'mdi-file-document';
      }
    },
    
    highlightMatch(text) {
      if (!this.searchQuery.trim()) return text;
      
      const regex = new RegExp(`(${this.escapeRegExp(this.searchQuery)})`, 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    },
    
    escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
  }
};
</script>

<style scoped>
.documentation-search {
  max-width: 800px;
  margin: 0 auto;
}

:deep(mark) {
  background-color: rgba(var(--v-primary-base), 0.2);
  color: inherit;
  padding: 0 2px;
  border-radius: 2px;
}
</style>
