<template>
  <div class="tag-browser">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-tag-search</v-icon>
        Tag Browser
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="refreshTags"
          :loading="loading"
        >
          <v-icon left small>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-autocomplete
              v-model="selectedRepository"
              :items="repositories"
              label="Repository"
              placeholder="Select a repository"
              prepend-icon="mdi-database"
              clearable
              outlined
              dense
              :loading="loading"
              @change="onRepositoryChange"
            ></v-autocomplete>
          </v-col>
        </v-row>
        
        <v-row v-if="selectedRepository">
          <v-col cols="12">
            <v-card outlined>
              <v-tabs v-model="activeTab" background-color="primary" dark>
                <v-tab>
                  <v-icon left>mdi-tag-multiple</v-icon>
                  Tags
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-chart-timeline-variant</v-icon>
                  Timeline
                </v-tab>
                <v-tab>
                  <v-icon left>mdi-information</v-icon>
                  Repository Info
                </v-tab>
              </v-tabs>
              
              <v-tabs-items v-model="activeTab">
                <!-- Tags Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12">
                          <v-text-field
                            v-model="tagSearch"
                            label="Search Tags"
                            prepend-icon="mdi-magnify"
                            clearable
                            outlined
                            dense
                          ></v-text-field>
                        </v-col>
                      </v-row>
                      
                      <v-row>
                        <v-col cols="12">
                          <div v-if="loading" class="text-center pa-6">
                            <v-progress-circular indeterminate color="primary"></v-progress-circular>
                            <p class="text-body-2 mt-2">Loading tags...</p>
                          </div>
                          
                          <div v-else-if="!filteredTags.length" class="text-center pa-6">
                            <v-icon large color="grey lighten-1">mdi-tag-outline</v-icon>
                            <p class="text-body-2 mt-2 grey--text">No tags found</p>
                            <p v-if="tagSearch" class="text-caption grey--text">
                              Try adjusting your search query
                            </p>
                          </div>
                          
                          <div v-else class="tag-grid">
                            <v-hover
                              v-for="tag in filteredTags"
                              :key="tag.name"
                              v-slot="{ hover }"
                            >
                              <v-card
                                outlined
                                :elevation="hover ? 4 : 0"
                                class="tag-card"
                                :class="{ 'on-hover': hover }"
                                @click="selectTag(tag)"
                              >
                                <v-card-text class="pa-3">
                                  <div class="d-flex align-center">
                                    <v-chip
                                      small
                                      :color="getTagColor(tag)"
                                      text-color="white"
                                      class="mr-2"
                                    >
                                      {{ tag.name }}
                                    </v-chip>
                                    <v-icon
                                      v-if="tag.is_latest"
                                      small
                                      color="success"
                                    >
                                      mdi-star
                                    </v-icon>
                                    <v-spacer></v-spacer>
                                    <v-btn
                                      v-if="hover"
                                      icon
                                      x-small
                                      @click.stop="pullTag(tag)"
                                      color="primary"
                                    >
                                      <v-icon x-small>mdi-download</v-icon>
                                    </v-btn>
                                  </div>
                                  
                                  <div class="mt-2 text-caption">
                                    <div>{{ formatDate(tag.created_at) }}</div>
                                    <div>{{ formatSize(tag.size) }}</div>
                                  </div>
                                </v-card-text>
                              </v-card>
                            </v-hover>
                          </div>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Timeline Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <div v-if="loading" class="text-center pa-6">
                        <v-progress-circular indeterminate color="primary"></v-progress-circular>
                        <p class="text-body-2 mt-2">Loading timeline...</p>
                      </div>
                      
                      <div v-else>
                        <v-timeline dense>
                          <v-timeline-item
                            v-for="(tag, index) in sortedTags"
                            :key="index"
                            :color="getTagColor(tag)"
                            small
                          >
                            <div class="d-flex align-center">
                              <div>
                                <div class="text-subtitle-2">
                                  {{ tag.name }}
                                  <v-icon
                                    v-if="tag.is_latest"
                                    x-small
                                    color="success"
                                    class="ml-1"
                                  >
                                    mdi-star
                                  </v-icon>
                                </div>
                                <div class="text-caption">{{ formatDate(tag.created_at) }}</div>
                              </div>
                              <v-spacer></v-spacer>
                              <v-btn
                                icon
                                x-small
                                @click="selectTag(tag)"
                                color="primary"
                              >
                                <v-icon x-small>mdi-eye</v-icon>
                              </v-btn>
                            </div>
                          </v-timeline-item>
                        </v-timeline>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Repository Info Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <div v-if="loading" class="text-center pa-6">
                        <v-progress-circular indeterminate color="primary"></v-progress-circular>
                        <p class="text-body-2 mt-2">Loading repository info...</p>
                      </div>
                      
                      <div v-else>
                        <v-row>
                          <v-col cols="12" md="6">
                            <v-card outlined>
                              <v-card-title class="text-subtitle-2">
                                <v-icon left small>mdi-information</v-icon>
                                Repository Details
                              </v-card-title>
                              <v-divider></v-divider>
                              <v-card-text>
                                <v-list dense>
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Name</v-list-item-title>
                                      <v-list-item-subtitle>{{ selectedRepository }}</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Tag Count</v-list-item-title>
                                      <v-list-item-subtitle>{{ repositoryTags.length }}</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Latest Tag</v-list-item-title>
                                      <v-list-item-subtitle>
                                        <v-chip
                                          x-small
                                          color="success"
                                          text-color="white"
                                          v-if="latestTag"
                                        >
                                          {{ latestTag.name }}
                                        </v-chip>
                                        <span v-else>None</span>
                                      </v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Last Updated</v-list-item-title>
                                      <v-list-item-subtitle>{{ lastUpdated }}</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                </v-list>
                              </v-card-text>
                            </v-card>
                          </v-col>
                          
                          <v-col cols="12" md="6">
                            <v-card outlined>
                              <v-card-title class="text-subtitle-2">
                                <v-icon left small>mdi-chart-pie</v-icon>
                                Tag Statistics
                              </v-card-title>
                              <v-divider></v-divider>
                              <v-card-text>
                                <div class="text-center pa-4">
                                  <v-progress-circular
                                    :rotate="-90"
                                    :size="150"
                                    :width="15"
                                    :value="versionTagPercentage"
                                    color="primary"
                                  >
                                    {{ versionTagPercentage }}%
                                  </v-progress-circular>
                                  <p class="text-caption mt-2">Version Tags</p>
                                </div>
                                
                                <v-list dense>
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Version Tags</v-list-item-title>
                                      <v-list-item-subtitle>{{ versionTagCount }} ({{ versionTagPercentage }}%)</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Development Tags</v-list-item-title>
                                      <v-list-item-subtitle>{{ devTagCount }} ({{ devTagPercentage }}%)</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Production Tags</v-list-item-title>
                                      <v-list-item-subtitle>{{ prodTagCount }} ({{ prodTagPercentage }}%)</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                  
                                  <v-list-item>
                                    <v-list-item-content>
                                      <v-list-item-title>Other Tags</v-list-item-title>
                                      <v-list-item-subtitle>{{ otherTagCount }} ({{ otherTagPercentage }}%)</v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                </v-list>
                              </v-card-text>
                            </v-card>
                          </v-col>
                        </v-row>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Tag Details Dialog -->
    <v-dialog v-model="tagDetailsDialog" max-width="700px">
      <v-card>
        <v-card-title class="headline">
          <v-icon left>mdi-tag</v-icon>
          {{ selectedTag ? `${selectedRepository}:${selectedTag.name}` : '' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="tagDetailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text v-if="selectedTag">
          <v-row>
            <v-col cols="12" md="6">
              <v-list dense>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Tag</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        small
                        :color="getTagColor(selectedTag)"
                        text-color="white"
                      >
                        {{ selectedTag.name }}
                      </v-chip>
                      <v-icon
                        v-if="selectedTag.is_latest"
                        small
                        color="success"
                        class="ml-2"
                      >
                        mdi-star
                      </v-icon>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Created</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(selectedTag.created_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Size</v-list-item-title>
                    <v-list-item-subtitle>{{ formatSize(selectedTag.size) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-list dense>
                <v-list-item v-if="selectedTag.digest">
                  <v-list-item-content>
                    <v-list-item-title>Digest</v-list-item-title>
                    <v-list-item-subtitle class="text-truncate">{{ selectedTag.digest }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="selectedTag.architecture">
                  <v-list-item-content>
                    <v-list-item-title>Architecture</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedTag.architecture }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="selectedTag.os">
                  <v-list-item-content>
                    <v-list-item-title>OS</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedTag.os }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>
          
          <v-row>
            <v-col cols="12">
              <v-btn
                color="primary"
                block
                @click="pullTag(selectedTag)"
              >
                <v-icon left>mdi-download</v-icon>
                Pull Image
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
    
    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { format, parseISO } from 'date-fns';

export default {
  name: 'TagBrowser',
  
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      repositories: [
        'nginx',
        'redis',
        'postgres',
        'ubuntu',
        'node',
        'python',
        'alpine',
        'mysql',
        'mongo',
        'httpd'
      ],
      selectedRepository: null,
      repositoryTags: [],
      activeTab: 0,
      tagSearch: '',
      selectedTag: null,
      tagDetailsDialog: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  computed: {
    filteredTags() {
      if (!this.repositoryTags.length) return [];
      
      // Apply search filter
      if (!this.tagSearch) return this.repositoryTags;
      
      const searchLower = this.tagSearch.toLowerCase();
      return this.repositoryTags.filter(tag => 
        tag.name.toLowerCase().includes(searchLower)
      );
    },
    
    sortedTags() {
      // Sort tags by creation date (newest first)
      return [...this.repositoryTags].sort((a, b) => {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA;
      });
    },
    
    latestTag() {
      return this.repositoryTags.find(tag => tag.is_latest);
    },
    
    lastUpdated() {
      if (!this.repositoryTags.length) return 'Never';
      
      // Find the most recent tag
      const dates = this.repositoryTags
        .map(tag => new Date(tag.created_at || 0))
        .sort((a, b) => b - a);
      
      return dates.length > 0 ? format(dates[0], 'MMM d, yyyy HH:mm') : 'Unknown';
    },
    
    versionTagCount() {
      return this.repositoryTags.filter(tag => /^v?\d+(\.\d+)*$/.test(tag.name)).length;
    },
    
    devTagCount() {
      return this.repositoryTags.filter(tag => 
        ['dev', 'develop', 'development', 'test', 'testing'].includes(tag.name)
      ).length;
    },
    
    prodTagCount() {
      return this.repositoryTags.filter(tag => 
        ['prod', 'production', 'stable', 'main', 'master'].includes(tag.name)
      ).length;
    },
    
    otherTagCount() {
      return this.repositoryTags.length - this.versionTagCount - this.devTagCount - this.prodTagCount;
    },
    
    versionTagPercentage() {
      return this.repositoryTags.length > 0 
        ? Math.round((this.versionTagCount / this.repositoryTags.length) * 100) 
        : 0;
    },
    
    devTagPercentage() {
      return this.repositoryTags.length > 0 
        ? Math.round((this.devTagCount / this.repositoryTags.length) * 100) 
        : 0;
    },
    
    prodTagPercentage() {
      return this.repositoryTags.length > 0 
        ? Math.round((this.prodTagCount / this.repositoryTags.length) * 100) 
        : 0;
    },
    
    otherTagPercentage() {
      return this.repositoryTags.length > 0 
        ? Math.round((this.otherTagCount / this.repositoryTags.length) * 100) 
        : 0;
    }
  },
  
  methods: {
    async onRepositoryChange() {
      if (!this.selectedRepository) {
        this.repositoryTags = [];
        return;
      }
      
      await this.fetchRepositoryTags();
    },
    
    async refreshTags() {
      if (!this.selectedRepository) return;
      
      await this.fetchRepositoryTags();
    },
    
    async fetchRepositoryTags() {
      // In a real implementation, this would call an API to get the tags
      // For now, we'll generate mock data
      this.repositoryTags = this.generateMockTags(this.selectedRepository);
    },
    
    generateMockTags(repository) {
      const now = new Date();
      const tags = [];
      
      // Add latest tag
      tags.push({
        name: 'latest',
        created_at: now.toISOString(),
        size: Math.floor(Math.random() * 500000000) + 50000000, // 50-550MB
        digest: `sha256:${this.generateRandomHash()}`,
        architecture: 'amd64',
        os: 'linux',
        is_latest: true
      });
      
      // Add version tags
      const versions = ['1.0.0', '1.1.0', '1.2.0', '2.0.0', 'v3.0.0', 'v3.1.0'];
      versions.forEach((version, index) => {
        const date = new Date(now);
        date.setDate(date.getDate() - (index + 1) * 7); // Each version is a week apart
        
        tags.push({
          name: version,
          created_at: date.toISOString(),
          size: Math.floor(Math.random() * 500000000) + 50000000, // 50-550MB
          digest: `sha256:${this.generateRandomHash()}`,
          architecture: 'amd64',
          os: 'linux',
          is_latest: false
        });
      });
      
      // Add development tags
      const devTags = ['dev', 'test', 'staging'];
      devTags.forEach((tag, index) => {
        const date = new Date(now);
        date.setDate(date.getDate() - index * 3); // Each dev tag is 3 days apart
        
        tags.push({
          name: tag,
          created_at: date.toISOString(),
          size: Math.floor(Math.random() * 500000000) + 50000000, // 50-550MB
          digest: `sha256:${this.generateRandomHash()}`,
          architecture: 'amd64',
          os: 'linux',
          is_latest: false
        });
      });
      
      // Add other tags
      const otherTags = ['slim', 'alpine', 'bullseye', 'buster'];
      otherTags.forEach((tag, index) => {
        const date = new Date(now);
        date.setDate(date.getDate() - index * 14); // Each other tag is 2 weeks apart
        
        tags.push({
          name: tag,
          created_at: date.toISOString(),
          size: Math.floor(Math.random() * 500000000) + 50000000, // 50-550MB
          digest: `sha256:${this.generateRandomHash()}`,
          architecture: 'amd64',
          os: 'linux',
          is_latest: false
        });
      });
      
      return tags;
    },
    
    generateRandomHash() {
      const chars = '0123456789abcdef';
      let hash = '';
      for (let i = 0; i < 64; i++) {
        hash += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return hash;
    },
    
    selectTag(tag) {
      this.selectedTag = tag;
      this.tagDetailsDialog = true;
    },
    
    async pullTag(tag) {
      // In a real implementation, this would call an API to pull the image
      // For now, we'll just show a success message
      this.showSuccess(`Started pulling ${this.selectedRepository}:${tag.name}`);
      
      // Emit event to parent component
      this.$emit('pull-tag', {
        repository: this.selectedRepository,
        tag: tag.name
      });
    },
    
    getTagColor(tag) {
      if (tag.is_latest) {
        return 'success';
      }
      
      // Check if it's a version tag (e.g., v1.0.0, 1.0, etc.)
      if (/^v?\d+(\.\d+)*$/.test(tag.name)) {
        return 'primary';
      }
      
      // Check if it's a development tag
      if (['dev', 'develop', 'development', 'test', 'testing', 'staging'].includes(tag.name)) {
        return 'warning';
      }
      
      // Check if it's a production tag
      if (['prod', 'production', 'stable', 'main', 'master'].includes(tag.name)) {
        return 'success';
      }
      
      // Default color
      return 'grey';
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
      try {
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
      } catch (error) {
        return dateString;
      }
    },
    
    formatSize(size) {
      if (size === undefined || size === null) return 'Unknown';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let formattedSize = size;
      let unitIndex = 0;
      
      while (formattedSize >= 1024 && unitIndex < units.length - 1) {
        formattedSize /= 1024;
        unitIndex++;
      }
      
      return `${formattedSize.toFixed(2)} ${units[unitIndex]}`;
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

<style scoped>
.tag-browser {
  width: 100%;
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.tag-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.tag-card.on-hover {
  background-color: #f5f5f5;
}
</style>
