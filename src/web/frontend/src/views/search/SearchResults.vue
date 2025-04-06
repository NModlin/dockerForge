<template>
  <div class="search-results">
    <h1 class="text-h4 mb-4">Search Results</h1>
    
    <!-- Search Form -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="searchQuery"
              label="Search"
              prepend-icon="mdi-magnify"
              clearable
              @keydown.enter="performSearch"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="searchType"
              :items="searchTypes"
              label="Type"
              prepend-icon="mdi-filter-variant"
              @change="performSearch"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>
    
    <!-- No Results -->
    <v-card v-else-if="results.length === 0" class="text-center pa-5">
      <v-icon size="64" color="grey lighten-1">mdi-file-search-outline</v-icon>
      <h3 class="text-h5 mt-4">No results found</h3>
      <p class="text-body-1 mt-2">Try adjusting your search or filter to find what you're looking for.</p>
    </v-card>
    
    <!-- Results -->
    <template v-else>
      <p class="text-body-2 mb-4">Found {{ totalResults }} results for "{{ originalQuery }}"</p>
      
      <!-- Container Results -->
      <v-card v-if="containerResults.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-docker</v-icon>
          Containers ({{ containerResults.length }})
        </v-card-title>
        <v-list two-line>
          <v-list-item
            v-for="container in containerResults"
            :key="container.id"
            :to="`/containers/${container.id}`"
          >
            <v-list-item-avatar>
              <v-icon :color="getStatusColor(container.status)">mdi-cube</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ container.name }}</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip x-small :color="getStatusColor(container.status)" text-color="white" class="mr-2">
                  {{ container.status }}
                </v-chip>
                {{ container.image }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon>
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card>
      
      <!-- Image Results -->
      <v-card v-if="imageResults.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-package-variant-closed</v-icon>
          Images ({{ imageResults.length }})
        </v-card-title>
        <v-list two-line>
          <v-list-item
            v-for="image in imageResults"
            :key="image.id"
            :to="`/images/${image.id}`"
          >
            <v-list-item-avatar>
              <v-icon color="primary">mdi-package-variant-closed</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>
                {{ image.tags && image.tags.length > 0 ? image.tags[0] : image.id.substring(0, 12) }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ formatSize(image.size) }} • Created {{ formatDate(image.created_at) }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon>
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card>
      
      <!-- Volume Results -->
      <v-card v-if="volumeResults.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-database</v-icon>
          Volumes ({{ volumeResults.length }})
        </v-card-title>
        <v-list two-line>
          <v-list-item
            v-for="volume in volumeResults"
            :key="volume.id"
            :to="`/volumes/${volume.id}`"
          >
            <v-list-item-avatar>
              <v-icon color="info">mdi-database</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ volume.name }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ volume.driver }} • Created {{ formatDate(volume.created_at) }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon>
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card>
      
      <!-- Network Results -->
      <v-card v-if="networkResults.length > 0" class="mb-4">
        <v-card-title>
          <v-icon left>mdi-lan</v-icon>
          Networks ({{ networkResults.length }})
        </v-card-title>
        <v-list two-line>
          <v-list-item
            v-for="network in networkResults"
            :key="network.id"
            :to="`/networks/${network.id}`"
          >
            <v-list-item-avatar>
              <v-icon color="success">mdi-lan</v-icon>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ network.name }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ network.driver }} • {{ network.scope }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon>
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-card>
    </template>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'SearchResults',
  data() {
    return {
      searchQuery: '',
      searchType: 'all',
      searchTypes: [
        { text: 'All', value: 'all' },
        { text: 'Containers', value: 'containers' },
        { text: 'Images', value: 'images' },
        { text: 'Volumes', value: 'volumes' },
        { text: 'Networks', value: 'networks' }
      ],
      originalQuery: '',
      loading: true,
      error: null,
      results: [],
      containerResults: [],
      imageResults: [],
      volumeResults: [],
      networkResults: []
    };
  },
  computed: {
    totalResults() {
      return this.results.length;
    }
  },
  created() {
    // Get search parameters from URL
    const query = this.$route.query.q;
    const type = this.$route.query.type || 'all';
    
    if (query) {
      this.searchQuery = query;
      this.searchType = type;
      this.originalQuery = query;
      this.performSearch();
    } else {
      this.loading = false;
    }
  },
  methods: {
    ...mapActions({
      searchContainers: 'containers/search',
      searchImages: 'images/search',
      searchVolumes: 'volumes/search',
      searchNetworks: 'networks/search'
    }),
    async performSearch() {
      if (!this.searchQuery.trim()) return;
      
      this.loading = true;
      this.error = null;
      this.results = [];
      this.containerResults = [];
      this.imageResults = [];
      this.volumeResults = [];
      this.networkResults = [];
      
      // Update URL with search parameters
      this.$router.replace({
        query: {
          q: this.searchQuery,
          type: this.searchType
        }
      });
      
      this.originalQuery = this.searchQuery;
      
      try {
        // Search based on type
        if (this.searchType === 'all' || this.searchType === 'containers') {
          try {
            const containerResults = await this.searchContainers(this.searchQuery);
            this.containerResults = containerResults || [];
            this.results = [...this.results, ...this.containerResults];
          } catch (error) {
            console.error('Error searching containers:', error);
          }
        }
        
        if (this.searchType === 'all' || this.searchType === 'images') {
          try {
            const imageResults = await this.searchImages(this.searchQuery);
            this.imageResults = imageResults || [];
            this.results = [...this.results, ...this.imageResults];
          } catch (error) {
            console.error('Error searching images:', error);
          }
        }
        
        if (this.searchType === 'all' || this.searchType === 'volumes') {
          try {
            const volumeResults = await this.searchVolumes(this.searchQuery);
            this.volumeResults = volumeResults || [];
            this.results = [...this.results, ...this.volumeResults];
          } catch (error) {
            console.error('Error searching volumes:', error);
          }
        }
        
        if (this.searchType === 'all' || this.searchType === 'networks') {
          try {
            const networkResults = await this.searchNetworks(this.searchQuery);
            this.networkResults = networkResults || [];
            this.results = [...this.results, ...this.networkResults];
          } catch (error) {
            console.error('Error searching networks:', error);
          }
        }
      } catch (error) {
        this.error = `Error performing search: ${error.message}`;
        console.error('Search error:', error);
      } finally {
        this.loading = false;
      }
    },
    getStatusColor(status) {
      if (status === 'running') return 'success';
      if (status === 'paused') return 'warning';
      if (status === 'exited' || status === 'dead') return 'error';
      return 'grey';
    },
    formatSize(bytes) {
      if (bytes === 0) return '0 B';
      
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays < 1) {
        return 'today';
      } else if (diffDays === 1) {
        return 'yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else {
        return date.toLocaleDateString();
      }
    }
  },
  watch: {
    // Watch for route changes to update search
    '$route.query': {
      handler(newQuery) {
        if (newQuery.q && newQuery.q !== this.searchQuery) {
          this.searchQuery = newQuery.q;
          this.searchType = newQuery.type || 'all';
          this.performSearch();
        }
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.search-results {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
