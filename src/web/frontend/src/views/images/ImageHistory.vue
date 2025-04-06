<template>
  <div class="image-history">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="headline">
              <v-icon large left>mdi-history</v-icon>
              Image History
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="goBack">
                <v-icon left>mdi-arrow-left</v-icon>
                Back to Image Details
              </v-btn>
            </v-card-title>
            
            <v-card-text v-if="loading">
              <v-skeleton-loader type="article" />
            </v-card-text>
            
            <v-card-text v-else-if="!image">
              <v-alert type="error">Image not found</v-alert>
            </v-card-text>
            
            <template v-else>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
                    <v-card outlined>
                      <v-card-title class="text-subtitle-1">
                        <v-icon left>mdi-docker</v-icon>
                        Image Information
                      </v-card-title>
                      <v-divider></v-divider>
                      <v-card-text>
                        <v-row>
                          <v-col cols="12" md="6">
                            <v-list dense>
                              <v-list-item>
                                <v-list-item-content>
                                  <v-list-item-title>ID</v-list-item-title>
                                  <v-list-item-subtitle>{{ image.id }}</v-list-item-subtitle>
                                </v-list-item-content>
                              </v-list-item>
                              
                              <v-list-item>
                                <v-list-item-content>
                                  <v-list-item-title>Tags</v-list-item-title>
                                  <v-list-item-subtitle>
                                    <v-chip
                                      v-for="tag in image.tags"
                                      :key="tag"
                                      class="ma-1"
                                      small
                                      color="primary"
                                      text-color="white"
                                    >
                                      {{ tag }}
                                    </v-chip>
                                  </v-list-item-subtitle>
                                </v-list-item-content>
                              </v-list-item>
                            </v-list>
                          </v-col>
                          
                          <v-col cols="12" md="6">
                            <v-list dense>
                              <v-list-item>
                                <v-list-item-content>
                                  <v-list-item-title>Size</v-list-item-title>
                                  <v-list-item-subtitle>{{ formatSize(image.size) }}</v-list-item-subtitle>
                                </v-list-item-content>
                              </v-list-item>
                              
                              <v-list-item>
                                <v-list-item-content>
                                  <v-list-item-title>Created</v-list-item-title>
                                  <v-list-item-subtitle>{{ formatDate(image.created_at) }}</v-list-item-subtitle>
                                </v-list-item-content>
                              </v-list-item>
                            </v-list>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
              
              <v-divider></v-divider>
              
              <v-tabs v-model="activeTab" background-color="primary" dark>
                <v-tab>Timeline</v-tab>
                <v-tab>Command Details</v-tab>
                <v-tab>Comparison</v-tab>
              </v-tabs>
              
              <v-tabs-items v-model="activeTab">
                <!-- Timeline Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <image-history-timeline
                        :history="image.history || []"
                        @select-item="onSelectHistoryItem"
                      />
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Command Details Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <command-details :command-item="selectedHistoryItem" />
                    </v-card-text>
                  </v-card>
                </v-tab-item>
                
                <!-- Comparison Tab -->
                <v-tab-item>
                  <v-card flat>
                    <v-card-text>
                      <image-comparison :current-image-id="imageId" />
                    </v-card-text>
                  </v-card>
                </v-tab-item>
              </v-tabs-items>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    
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
import { format, parseISO } from 'date-fns';
import ImageHistoryTimeline from '@/components/images/ImageHistoryTimeline.vue';
import CommandDetails from '@/components/images/CommandDetails.vue';
import ImageComparison from '@/components/images/ImageComparison.vue';

export default {
  name: 'ImageHistory',
  
  components: {
    ImageHistoryTimeline,
    CommandDetails,
    ImageComparison
  },
  
  data() {
    return {
      activeTab: 0,
      loading: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
      selectedHistoryItem: null
    };
  },
  
  computed: {
    ...mapState('images', ['image']),
    
    imageId() {
      return this.$route.params.id;
    }
  },
  
  created() {
    this.fetchImageDetails();
  },
  
  methods: {
    ...mapActions('images', ['getImage']),
    
    async fetchImageDetails() {
      this.loading = true;
      try {
        await this.getImage(this.imageId);
      } catch (error) {
        this.showError('Failed to fetch image details: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    onSelectHistoryItem(item) {
      this.selectedHistoryItem = item;
      if (item) {
        this.activeTab = 1; // Switch to Command Details tab
      }
    },
    
    goBack() {
      this.$router.push({ name: 'ImageDetail', params: { id: this.imageId } });
    },
    
    formatSize(size) {
      if (!size) return 'Unknown';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let formattedSize = size;
      let unitIndex = 0;
      
      while (formattedSize >= 1024 && unitIndex < units.length - 1) {
        formattedSize /= 1024;
        unitIndex++;
      }
      
      return `${formattedSize.toFixed(2)} ${units[unitIndex]}`;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      try {
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
      } catch (error) {
        return dateString;
      }
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
.image-history {
  height: 100%;
}
</style>
