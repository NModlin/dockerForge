<template>
  <div class="tag-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-tag-multiple</v-icon>
              Tag Management
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Images
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-card outlined>
                    <v-card-title class="text-subtitle-1">
                      <v-icon left>mdi-filter</v-icon>
                      Filter Options
                      <v-spacer></v-spacer>
                      <v-btn
                        text
                        small
                        color="primary"
                        @click="resetFilters"
                      >
                        <v-icon left small>mdi-refresh</v-icon>
                        Reset Filters
                      </v-btn>
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="4">
                          <v-text-field
                            v-model="filters.search"
                            label="Search Tags"
                            prepend-icon="mdi-magnify"
                            clearable
                            outlined
                            dense
                          ></v-text-field>
                        </v-col>
                        
                        <v-col cols="12" md="4">
                          <v-select
                            v-model="filters.tagType"
                            :items="tagTypeOptions"
                            label="Tag Type"
                            prepend-icon="mdi-tag"
                            clearable
                            outlined
                            dense
                          ></v-select>
                        </v-col>
                        
                        <v-col cols="12" md="4">
                          <v-select
                            v-model="filters.sortBy"
                            :items="sortOptions"
                            label="Sort By"
                            prepend-icon="mdi-sort"
                            outlined
                            dense
                          ></v-select>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-row class="mt-4">
                <v-col cols="12">
                  <tag-list
                    :tags="filteredTags"
                    :loading="loading"
                    :can-manage-tags="true"
                    @view-tag="viewTagDetails"
                    @add-tag="addTag"
                    @delete-tag="deleteTag"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Tag Details Dialog -->
    <v-dialog v-model="tagDetailsDialog" max-width="800px">
      <v-card>
        <v-card-title class="headline">
          <v-icon left>mdi-tag</v-icon>
          Tag Details: {{ selectedTag ? selectedTag.name : '' }}
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
                    <v-list-item-title>Tag Name</v-list-item-title>
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
                    <v-list-item-subtitle>{{ selectedTag.digest }}</v-list-item-subtitle>
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
              <h3 class="text-subtitle-1">
                <v-icon left>mdi-history</v-icon>
                Tag History
              </h3>
              
              <v-timeline dense>
                <v-timeline-item
                  v-for="(event, index) in tagHistory"
                  :key="index"
                  :color="getEventColor(event.type)"
                  small
                >
                  <div class="d-flex align-center">
                    <div>
                      <div class="text-subtitle-2">{{ event.type }}</div>
                      <div class="text-caption">{{ formatDate(event.timestamp) }}</div>
                    </div>
                    <v-spacer></v-spacer>
                    <div class="text-body-2">{{ event.description }}</div>
                  </div>
                </v-timeline-item>
              </v-timeline>
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
import { mapState, mapActions } from 'vuex';
import { format, parseISO, subDays } from 'date-fns';
import TagList from '@/components/images/TagList.vue';

export default {
  name: 'TagManagement',
  
  components: {
    TagList
  },
  
  data() {
    return {
      loading: false,
      filters: {
        search: '',
        tagType: null,
        sortBy: 'created_desc'
      },
      tagTypeOptions: [
        { text: 'All Tags', value: null },
        { text: 'Latest', value: 'latest' },
        { text: 'Version Tags', value: 'version' },
        { text: 'Development Tags', value: 'development' },
        { text: 'Production Tags', value: 'production' }
      ],
      sortOptions: [
        { text: 'Created (Newest First)', value: 'created_desc' },
        { text: 'Created (Oldest First)', value: 'created_asc' },
        { text: 'Name (A-Z)', value: 'name_asc' },
        { text: 'Name (Z-A)', value: 'name_desc' },
        { text: 'Size (Largest First)', value: 'size_desc' },
        { text: 'Size (Smallest First)', value: 'size_asc' }
      ],
      tagDetailsDialog: false,
      selectedTag: null,
      tagHistory: [],
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  computed: {
    ...mapState('images', ['images']),
    
    allTags() {
      // Extract tags from all images
      const tags = [];
      
      this.images.forEach(image => {
        if (image.tags && image.tags.length > 0) {
          image.tags.forEach(tagName => {
            const [name, tag] = tagName.split(':');
            if (tag) {
              tags.push({
                name: tag,
                image_name: name,
                image_id: image.id,
                created_at: image.created_at,
                size: image.size,
                digest: image.digest,
                architecture: image.architecture,
                os: image.os,
                is_latest: tag === 'latest'
              });
            }
          });
        }
      });
      
      return tags;
    },
    
    filteredTags() {
      if (!this.allTags.length) return [];
      
      // Apply filters
      let filtered = [...this.allTags];
      
      // Apply search filter
      if (this.filters.search) {
        const searchLower = this.filters.search.toLowerCase();
        filtered = filtered.filter(tag => 
          tag.name.toLowerCase().includes(searchLower) ||
          tag.image_name.toLowerCase().includes(searchLower)
        );
      }
      
      // Apply tag type filter
      if (this.filters.tagType) {
        switch (this.filters.tagType) {
          case 'latest':
            filtered = filtered.filter(tag => tag.is_latest);
            break;
          case 'version':
            filtered = filtered.filter(tag => /^v?\d+(\.\d+)*$/.test(tag.name));
            break;
          case 'development':
            filtered = filtered.filter(tag => 
              ['dev', 'develop', 'development', 'test', 'testing'].includes(tag.name)
            );
            break;
          case 'production':
            filtered = filtered.filter(tag => 
              ['prod', 'production', 'stable', 'main', 'master'].includes(tag.name)
            );
            break;
        }
      }
      
      // Apply sorting
      if (this.filters.sortBy) {
        const [field, direction] = this.filters.sortBy.split('_');
        const multiplier = direction === 'desc' ? -1 : 1;
        
        filtered.sort((a, b) => {
          if (field === 'created') {
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return multiplier * (dateA - dateB);
          } else if (field === 'name') {
            return multiplier * a.name.localeCompare(b.name);
          } else if (field === 'size') {
            return multiplier * ((a.size || 0) - (b.size || 0));
          }
          return 0;
        });
      }
      
      return filtered;
    }
  },
  
  created() {
    this.fetchImages();
  },
  
  methods: {
    ...mapActions('images', ['getImages', 'addImageTag', 'deleteImageTag']),
    
    async fetchImages() {
      this.loading = true;
      try {
        await this.getImages();
      } catch (error) {
        this.showError('Failed to fetch images: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    resetFilters() {
      this.filters = {
        search: '',
        tagType: null,
        sortBy: 'created_desc'
      };
    },
    
    viewTagDetails(tag) {
      this.selectedTag = tag;
      this.generateTagHistory(tag);
      this.tagDetailsDialog = true;
    },
    
    generateTagHistory(tag) {
      // In a real implementation, this would fetch the tag history from the API
      // For now, we'll generate mock data
      const now = new Date();
      
      this.tagHistory = [
        {
          type: 'Created',
          timestamp: tag.created_at,
          description: `Tag ${tag.name} was created for image ${tag.image_name}`
        }
      ];
      
      // Add some mock history events
      if (tag.is_latest) {
        this.tagHistory.push({
          type: 'Updated',
          timestamp: subDays(now, 2).toISOString(),
          description: `Tag ${tag.name} was set as the latest tag`
        });
      }
      
      if (Math.random() > 0.5) {
        this.tagHistory.push({
          type: 'Pulled',
          timestamp: subDays(now, 1).toISOString(),
          description: `Tag ${tag.name} was pulled by user`
        });
      }
    },
    
    async addTag({ imageId, tagName, isLatest }) {
      try {
        await this.addImageTag({ imageId, tagName, isLatest });
        this.showSuccess(`Tag ${tagName} added successfully`);
        return true;
      } catch (error) {
        this.showError(`Failed to add tag: ${error.message}`);
        throw error;
      }
    },
    
    async deleteTag({ imageId, tagName }) {
      try {
        await this.deleteImageTag({ imageId, tagName });
        this.showSuccess(`Tag ${tagName} deleted successfully`);
        return true;
      } catch (error) {
        this.showError(`Failed to delete tag: ${error.message}`);
        throw error;
      }
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
      if (['dev', 'develop', 'development', 'test', 'testing'].includes(tag.name)) {
        return 'warning';
      }
      
      // Check if it's a production tag
      if (['prod', 'production', 'stable', 'main', 'master'].includes(tag.name)) {
        return 'success';
      }
      
      // Default color
      return 'grey';
    },
    
    getEventColor(eventType) {
      switch (eventType) {
        case 'Created':
          return 'success';
        case 'Updated':
          return 'primary';
        case 'Pulled':
          return 'info';
        case 'Deleted':
          return 'error';
        default:
          return 'grey';
      }
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
    
    goBack() {
      this.$router.push({ name: 'Images' });
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
.tag-management {
  height: 100%;
}
</style>
