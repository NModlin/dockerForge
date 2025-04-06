<template>
  <div class="image-comparison">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-compare</v-icon>
        Image Comparison
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="refreshComparison"
          :loading="loading"
        >
          <v-icon left small>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="baseImageId"
              :items="availableImages"
              label="Base Image"
              outlined
              dense
              :disabled="loading"
              @change="onComparisonChange"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-select
              v-model="targetImageId"
              :items="availableImages"
              label="Target Image"
              outlined
              dense
              :disabled="loading"
              @change="onComparisonChange"
            ></v-select>
          </v-col>
        </v-row>
        
        <div v-if="loading" class="text-center pa-6">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="text-body-2 mt-2">Comparing images...</p>
        </div>
        
        <div v-else-if="!baseImageId || !targetImageId" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-compare</v-icon>
          <p class="text-body-2 mt-2 grey--text">Select two images to compare</p>
        </div>
        
        <div v-else-if="baseImageId === targetImageId" class="text-center pa-6">
          <v-icon large color="warning">mdi-alert</v-icon>
          <p class="text-body-2 mt-2">Please select different images to compare</p>
        </div>
        
        <div v-else>
          <!-- Comparison Summary -->
          <v-card outlined class="mt-4">
            <v-card-title class="text-subtitle-2">
              <v-icon left small>mdi-information</v-icon>
              Comparison Summary
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <v-card outlined class="text-center pa-2">
                    <div class="text-caption">Size Difference</div>
                    <div class="text-h6" :class="sizeDifferenceClass">
                      {{ sizeDifference }}
                    </div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-card outlined class="text-center pa-2">
                    <div class="text-caption">Layer Difference</div>
                    <div class="text-h6">
                      {{ layerDifference }}
                    </div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-card outlined class="text-center pa-2">
                    <div class="text-caption">Common Base</div>
                    <div class="text-h6">
                      {{ commonBase ? 'Yes' : 'No' }}
                    </div>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          
          <!-- Layer Comparison -->
          <v-card outlined class="mt-4">
            <v-card-title class="text-subtitle-2">
              <v-icon left small>mdi-layers</v-icon>
              Layer Comparison
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-0">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Command</th>
                      <th>Size</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(layer, index) in comparisonLayers" :key="index" :class="getLayerRowClass(layer)">
                      <td>
                        <v-chip
                          x-small
                          :color="getLayerStatusColor(layer.status)"
                          text-color="white"
                        >
                          {{ layer.status }}
                        </v-chip>
                      </td>
                      <td>
                        <div class="layer-command">{{ layer.command }}</div>
                      </td>
                      <td>{{ formatSize(layer.size) }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
          
          <!-- Size Comparison Chart -->
          <v-card outlined class="mt-4">
            <v-card-title class="text-subtitle-2">
              <v-icon left small>mdi-chart-bar</v-icon>
              Size Comparison
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <div class="size-comparison">
                <div class="size-bar-container">
                  <div class="size-bar-label">Base</div>
                  <div class="size-bar-wrapper">
                    <div
                      class="size-bar"
                      :style="{
                        width: `${(baseImage.size / Math.max(baseImage.size, targetImage.size)) * 100}%`,
                        backgroundColor: '#2196F3'
                      }"
                    ></div>
                  </div>
                  <div class="size-bar-value">{{ formatSize(baseImage.size) }}</div>
                </div>
                
                <div class="size-bar-container">
                  <div class="size-bar-label">Target</div>
                  <div class="size-bar-wrapper">
                    <div
                      class="size-bar"
                      :style="{
                        width: `${(targetImage.size / Math.max(baseImage.size, targetImage.size)) * 100}%`,
                        backgroundColor: '#4CAF50'
                      }"
                    ></div>
                  </div>
                  <div class="size-bar-value">{{ formatSize(targetImage.size) }}</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'ImageComparison',
  
  props: {
    currentImageId: {
      type: String,
      default: null
    }
  },
  
  data() {
    return {
      baseImageId: null,
      targetImageId: null,
      loading: false,
      baseImage: {
        id: null,
        size: 0,
        layers: []
      },
      targetImage: {
        id: null,
        size: 0,
        layers: []
      },
      comparisonLayers: []
    };
  },
  
  computed: {
    ...mapState('images', ['images']),
    
    availableImages() {
      return this.images.map(image => {
        const tag = image.tags && image.tags.length > 0 ? image.tags[0] : 'untagged';
        return {
          text: `${tag} (${image.short_id})`,
          value: image.id
        };
      });
    },
    
    sizeDifference() {
      const diff = this.targetImage.size - this.baseImage.size;
      const sign = diff >= 0 ? '+' : '';
      return `${sign}${this.formatSize(diff)}`;
    },
    
    sizeDifferenceClass() {
      const diff = this.targetImage.size - this.baseImage.size;
      if (diff > 0) return 'red--text';
      if (diff < 0) return 'green--text';
      return '';
    },
    
    layerDifference() {
      const added = this.comparisonLayers.filter(l => l.status === 'ADDED').length;
      const removed = this.comparisonLayers.filter(l => l.status === 'REMOVED').length;
      const modified = this.comparisonLayers.filter(l => l.status === 'MODIFIED').length;
      
      return `+${added} -${removed} ~${modified}`;
    },
    
    commonBase() {
      // Check if images share common base layers
      if (!this.baseImage.layers.length || !this.targetImage.layers.length) {
        return false;
      }
      
      // Check if the first layer (base image) is the same
      const baseFirstLayer = this.baseImage.layers[this.baseImage.layers.length - 1];
      const targetFirstLayer = this.targetImage.layers[this.targetImage.layers.length - 1];
      
      if (!baseFirstLayer || !targetFirstLayer) {
        return false;
      }
      
      return baseFirstLayer.CreatedBy === targetFirstLayer.CreatedBy;
    }
  },
  
  watch: {
    currentImageId: {
      handler(newId) {
        if (newId && !this.baseImageId) {
          this.baseImageId = newId;
          
          // Try to find a related image for comparison
          const currentImage = this.images.find(img => img.id === newId);
          if (currentImage && currentImage.tags && currentImage.tags.length > 0) {
            const currentTag = currentImage.tags[0];
            const tagParts = currentTag.split(':');
            const imageName = tagParts[0];
            
            // Look for another image with the same name but different tag
            const relatedImage = this.images.find(img => {
              if (img.id === newId) return false;
              if (!img.tags || img.tags.length === 0) return false;
              
              const imgTag = img.tags[0];
              const imgTagParts = imgTag.split(':');
              return imgTagParts[0] === imageName;
            });
            
            if (relatedImage) {
              this.targetImageId = relatedImage.id;
              this.onComparisonChange();
            }
          }
        }
      },
      immediate: true
    },
    
    images: {
      handler() {
        if (this.baseImageId && this.targetImageId) {
          this.onComparisonChange();
        }
      },
      deep: true
    }
  },
  
  methods: {
    onComparisonChange() {
      if (this.baseImageId && this.targetImageId && this.baseImageId !== this.targetImageId) {
        this.refreshComparison();
      }
    },
    
    async refreshComparison() {
      if (!this.baseImageId || !this.targetImageId || this.baseImageId === this.targetImageId) {
        return;
      }
      
      this.loading = true;
      
      try {
        // Get base image details
        const baseImage = this.images.find(img => img.id === this.baseImageId);
        const targetImage = this.images.find(img => img.id === this.targetImageId);
        
        if (!baseImage || !targetImage) {
          throw new Error('Images not found');
        }
        
        // In a real implementation, we would call an API to get detailed comparison
        // For now, we'll simulate the comparison
        await this.simulateComparison(baseImage, targetImage);
      } catch (error) {
        console.error('Error comparing images:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async simulateComparison(baseImage, targetImage) {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Set base image data
      this.baseImage = {
        id: baseImage.id,
        size: baseImage.size,
        layers: baseImage.history || []
      };
      
      // Set target image data
      this.targetImage = {
        id: targetImage.id,
        size: targetImage.size,
        layers: targetImage.history || []
      };
      
      // Generate comparison layers
      this.comparisonLayers = this.generateComparisonLayers(
        this.baseImage.layers,
        this.targetImage.layers
      );
    },
    
    generateComparisonLayers(baseLayers, targetLayers) {
      const comparison = [];
      
      // Process base layers (look for removed or modified)
      baseLayers.forEach(baseLayer => {
        const command = this.getLayerCommand(baseLayer);
        
        // Look for matching layer in target
        const matchingLayer = targetLayers.find(targetLayer => 
          this.getLayerCommand(targetLayer) === command
        );
        
        if (!matchingLayer) {
          // Layer was removed
          comparison.push({
            status: 'REMOVED',
            command,
            size: baseLayer.Size,
            layer: baseLayer
          });
        } else if (matchingLayer.Size !== baseLayer.Size) {
          // Layer was modified
          comparison.push({
            status: 'MODIFIED',
            command,
            size: matchingLayer.Size - baseLayer.Size,
            layer: matchingLayer
          });
        } else {
          // Layer is unchanged
          comparison.push({
            status: 'UNCHANGED',
            command,
            size: baseLayer.Size,
            layer: baseLayer
          });
        }
      });
      
      // Process target layers (look for added)
      targetLayers.forEach(targetLayer => {
        const command = this.getLayerCommand(targetLayer);
        
        // Check if this layer exists in base
        const existsInBase = baseLayers.some(baseLayer => 
          this.getLayerCommand(baseLayer) === command
        );
        
        if (!existsInBase) {
          // Layer was added
          comparison.push({
            status: 'ADDED',
            command,
            size: targetLayer.Size,
            layer: targetLayer
          });
        }
      });
      
      // Sort by status (ADDED, REMOVED, MODIFIED, UNCHANGED)
      comparison.sort((a, b) => {
        const statusOrder = {
          'ADDED': 0,
          'REMOVED': 1,
          'MODIFIED': 2,
          'UNCHANGED': 3
        };
        
        return statusOrder[a.status] - statusOrder[b.status];
      });
      
      return comparison;
    },
    
    getLayerCommand(layer) {
      if (!layer || !layer.CreatedBy) return 'Unknown';
      
      // Extract command from CreatedBy field
      let command = layer.CreatedBy;
      
      // Remove "/bin/sh -c " prefix if present
      if (command.startsWith('/bin/sh -c ')) {
        command = command.substring('/bin/sh -c '.length);
      }
      
      // Remove "#(nop) " prefix if present
      if (command.startsWith('#(nop) ')) {
        command = command.substring('#(nop) '.length);
      }
      
      return command;
    },
    
    getLayerStatusColor(status) {
      switch (status) {
        case 'ADDED':
          return 'success';
        case 'REMOVED':
          return 'error';
        case 'MODIFIED':
          return 'warning';
        case 'UNCHANGED':
          return 'grey';
        default:
          return 'grey';
      }
    },
    
    getLayerRowClass(layer) {
      switch (layer.status) {
        case 'ADDED':
          return 'added-row';
        case 'REMOVED':
          return 'removed-row';
        case 'MODIFIED':
          return 'modified-row';
        default:
          return '';
      }
    },
    
    formatSize(size) {
      if (size === undefined || size === null) return 'Unknown';
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let formattedSize = Math.abs(size);
      let unitIndex = 0;
      
      while (formattedSize >= 1024 && unitIndex < units.length - 1) {
        formattedSize /= 1024;
        unitIndex++;
      }
      
      const sign = size < 0 ? '-' : '';
      return `${sign}${formattedSize.toFixed(2)} ${units[unitIndex]}`;
    }
  }
};
</script>

<style scoped>
.image-comparison {
  width: 100%;
}

.layer-command {
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 500px;
}

.added-row {
  background-color: rgba(76, 175, 80, 0.1);
}

.removed-row {
  background-color: rgba(244, 67, 54, 0.1);
}

.modified-row {
  background-color: rgba(255, 152, 0, 0.1);
}

.size-comparison {
  padding: 16px 0;
}

.size-bar-container {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.size-bar-label {
  width: 60px;
  font-weight: 500;
}

.size-bar-wrapper {
  flex: 1;
  height: 24px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 16px;
}

.size-bar {
  height: 100%;
  transition: width 0.5s ease;
}

.size-bar-value {
  width: 100px;
  text-align: right;
}
</style>
