<template>
  <div class="image-pull">
    <v-card>
      <v-card-title>
        <v-icon left>mdi-cloud-download</v-icon>
        Pull Docker Image
      </v-card-title>
      
      <v-card-text>
        <v-tabs v-model="activeTab">
          <v-tab>
            <v-icon left>mdi-magnify</v-icon>
            Search Docker Hub
          </v-tab>
          <v-tab>
            <v-icon left>mdi-text-box</v-icon>
            Manual Entry
          </v-tab>
        </v-tabs>
        
        <v-tabs-items v-model="activeTab">
          <!-- Search Docker Hub Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="searchQuery"
                      label="Search Docker Hub"
                      prepend-icon="mdi-magnify"
                      clearable
                      @keyup.enter="searchDockerHub"
                      :loading="searching"
                      :disabled="pulling"
                    ></v-text-field>
                  </v-col>
                </v-row>
                
                <v-row v-if="searchResults.length > 0">
                  <v-col cols="12">
                    <v-data-table
                      :headers="searchHeaders"
                      :items="searchResults"
                      :items-per-page="5"
                      :loading="searching"
                      class="elevation-1"
                    >
                      <template v-slot:item.name="{ item }">
                        <div class="d-flex align-center">
                          <v-avatar size="24" class="mr-2" v-if="item.official">
                            <v-icon color="primary">mdi-check-circle</v-icon>
                          </v-avatar>
                          {{ item.name }}
                          <v-chip x-small color="primary" text-color="white" class="ml-2" v-if="item.official">
                            Official
                          </v-chip>
                        </div>
                      </template>
                      
                      <template v-slot:item.description="{ item }">
                        <div class="text-truncate" style="max-width: 300px;">
                          {{ item.description || 'No description available' }}
                        </div>
                      </template>
                      
                      <template v-slot:item.stars="{ item }">
                        <div class="d-flex align-center">
                          <v-icon small color="amber">mdi-star</v-icon>
                          {{ item.stars.toLocaleString() }}
                        </div>
                      </template>
                      
                      <template v-slot:item.actions="{ item }">
                        <v-btn
                          small
                          color="primary"
                          @click="selectImage(item)"
                          :disabled="pulling"
                        >
                          Select
                        </v-btn>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
                
                <v-row v-else-if="searchPerformed && !searching">
                  <v-col cols="12" class="text-center">
                    <v-alert type="info" outlined>
                      No results found for "{{ searchQuery }}". Try a different search term.
                    </v-alert>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-tab-item>
          
          <!-- Manual Entry Tab -->
          <v-tab-item>
            <v-card flat>
              <v-card-text>
                <v-form ref="manualForm" v-model="validManualForm" lazy-validation>
                  <v-row>
                    <v-col cols="12">
                      <v-text-field
                        v-model="selectedImage.name"
                        label="Image Name"
                        hint="e.g., nginx, ubuntu, postgres"
                        persistent-hint
                        :rules="[v => !!v || 'Image name is required']"
                        required
                        :disabled="pulling"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </v-form>
              </v-card-text>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
        
        <!-- Tag Selection (shown when an image is selected) -->
        <v-row v-if="selectedImage.name">
          <v-col cols="12">
            <v-card outlined class="mb-4">
              <v-card-title class="subtitle-1">
                <v-icon left>mdi-tag-multiple</v-icon>
                Select Tag
              </v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" sm="8">
                    <v-select
                      v-model="selectedImage.tag"
                      :items="availableTags"
                      label="Tag"
                      :loading="loadingTags"
                      :disabled="pulling || loadingTags"
                      :hint="selectedImage.tag ? `Pull ${selectedImage.name}:${selectedImage.tag}` : 'Select a tag'"
                      persistent-hint
                    ></v-select>
                  </v-col>
                  <v-col cols="12" sm="4" class="d-flex align-center">
                    <v-btn
                      color="primary"
                      block
                      @click="refreshTags"
                      :disabled="!selectedImage.name || pulling"
                      :loading="loadingTags"
                    >
                      <v-icon left>mdi-refresh</v-icon>
                      Refresh Tags
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Pull Progress -->
        <v-row v-if="pulling">
          <v-col cols="12">
            <v-card outlined>
              <v-card-text>
                <div class="text-center mb-2">
                  <h3 class="subtitle-1">
                    Pulling {{ selectedImage.name }}:{{ selectedImage.tag || 'latest' }}
                  </h3>
                </div>
                
                <v-progress-linear
                  :indeterminate="pullProgress === 0"
                  :value="pullProgress"
                  height="20"
                  color="primary"
                  striped
                >
                  <template v-slot:default>
                    <span class="white--text">{{ pullProgress }}%</span>
                  </template>
                </v-progress-linear>
                
                <div class="text-center mt-2 text-caption">
                  {{ pullStatus }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          text
          @click="$emit('close')"
          :disabled="pulling"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="pullImage"
          :disabled="!canPull || pulling"
          :loading="pulling"
        >
          <v-icon left>mdi-cloud-download</v-icon>
          Pull Image
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'ImagePull',
  
  data() {
    return {
      activeTab: 0,
      searchQuery: '',
      searchResults: [],
      searchPerformed: false,
      searching: false,
      
      selectedImage: {
        name: '',
        tag: '',
      },
      
      availableTags: [],
      loadingTags: false,
      
      validManualForm: false,
      
      pulling: false,
      pullProgress: 0,
      pullStatus: 'Preparing to pull...',
      pullInterval: null,
      
      searchHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Description', value: 'description', sortable: false },
        { text: 'Stars', value: 'stars', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
      ],
    };
  },
  
  computed: {
    canPull() {
      return this.selectedImage.name && this.selectedImage.tag;
    },
  },
  
  methods: {
    ...mapActions({
      searchDockerHubAction: 'images/searchDockerHub',
      getImageTagsAction: 'images/getImageTags',
      pullImageAction: 'images/pullImage',
    }),
    
    async searchDockerHub() {
      if (!this.searchQuery) return;
      
      this.searching = true;
      this.searchResults = [];
      this.searchPerformed = true;
      
      try {
        const result = await this.searchDockerHubAction({
          query: this.searchQuery,
          page: 1,
          pageSize: 10,
        });
        
        this.searchResults = result.results || [];
      } catch (error) {
        this.$store.dispatch('showSnackbar', {
          text: `Failed to search Docker Hub: ${error.message}`,
          color: 'error',
        });
      } finally {
        this.searching = false;
      }
    },
    
    async selectImage(image) {
      this.selectedImage.name = image.name;
      this.selectedImage.tag = '';
      this.availableTags = [];
      
      await this.fetchTags();
    },
    
    async fetchTags() {
      if (!this.selectedImage.name) return;
      
      this.loadingTags = true;
      
      try {
        const tags = await this.getImageTagsAction(this.selectedImage.name);
        this.availableTags = tags || ['latest'];
        
        // Set default tag to latest if available
        if (this.availableTags.includes('latest')) {
          this.selectedImage.tag = 'latest';
        } else if (this.availableTags.length > 0) {
          this.selectedImage.tag = this.availableTags[0];
        }
      } catch (error) {
        this.$store.dispatch('showSnackbar', {
          text: `Failed to fetch tags: ${error.message}`,
          color: 'error',
        });
        this.availableTags = ['latest'];
        this.selectedImage.tag = 'latest';
      } finally {
        this.loadingTags = false;
      }
    },
    
    async refreshTags() {
      await this.fetchTags();
    },
    
    async pullImage() {
      if (this.activeTab === 1 && this.$refs.manualForm) {
        if (!this.$refs.manualForm.validate()) return;
      }
      
      if (!this.selectedImage.name) {
        this.$store.dispatch('showSnackbar', {
          text: 'Please select an image to pull',
          color: 'warning',
        });
        return;
      }
      
      const tag = this.selectedImage.tag || 'latest';
      
      this.pulling = true;
      this.pullProgress = 0;
      this.pullStatus = `Preparing to pull ${this.selectedImage.name}:${tag}...`;
      
      // Set up a simulated progress interval
      this.pullInterval = setInterval(() => {
        if (this.pullProgress < 90) {
          this.pullProgress += Math.floor(Math.random() * 10) + 1;
          
          // Update status messages based on progress
          if (this.pullProgress < 20) {
            this.pullStatus = `Connecting to registry...`;
          } else if (this.pullProgress < 40) {
            this.pullStatus = `Downloading manifest...`;
          } else if (this.pullProgress < 60) {
            this.pullStatus = `Downloading layers...`;
          } else if (this.pullProgress < 80) {
            this.pullStatus = `Extracting layers...`;
          } else {
            this.pullStatus = `Almost done...`;
          }
        }
      }, 1000);
      
      try {
        await this.pullImageAction({
          name: this.selectedImage.name,
          tag: tag,
        });
        
        // Complete the progress
        clearInterval(this.pullInterval);
        this.pullProgress = 100;
        this.pullStatus = `Successfully pulled ${this.selectedImage.name}:${tag}`;
        
        setTimeout(() => {
          this.$store.dispatch('showSnackbar', {
            text: `Successfully pulled ${this.selectedImage.name}:${tag}`,
            color: 'success',
          });
          
          this.$emit('pulled');
          this.$emit('close');
        }, 1000);
      } catch (error) {
        clearInterval(this.pullInterval);
        this.pullProgress = 0;
        this.pullStatus = `Failed to pull image: ${error.message}`;
        
        this.$store.dispatch('showSnackbar', {
          text: `Failed to pull image: ${error.message}`,
          color: 'error',
        });
      } finally {
        if (this.pullInterval) {
          clearInterval(this.pullInterval);
        }
        
        // Keep pulling true for a moment to show the final status
        setTimeout(() => {
          this.pulling = false;
        }, 1000);
      }
    },
  },
  
  beforeDestroy() {
    if (this.pullInterval) {
      clearInterval(this.pullInterval);
    }
  },
};
</script>

<style scoped>
.image-pull {
  max-width: 800px;
  margin: 0 auto;
}
</style>
