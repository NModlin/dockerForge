<template>
  <div class="image-layer-visualization">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-layers</v-icon>
        Image Layers
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="expandAll"
          v-if="!allExpanded"
        >
          <v-icon left small>mdi-arrow-expand-all</v-icon>
          Expand All
        </v-btn>
        <v-btn
          text
          small
          color="primary"
          @click="collapseAll"
          v-else
        >
          <v-icon left small>mdi-arrow-collapse-all</v-icon>
          Collapse All
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <div v-if="!layers || layers.length === 0" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-layers-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No layer information available</p>
        </div>
        
        <div v-else>
          <!-- Layer Size Visualization -->
          <div class="layer-size-visualization pa-4">
            <h3 class="text-subtitle-2 mb-2">Layer Size Distribution</h3>
            <div class="layer-bars">
              <div
                v-for="(layer, index) in layersWithSizes"
                :key="`size-${index}`"
                class="layer-bar"
                :style="{
                  width: `${layer.sizePercentage}%`,
                  backgroundColor: getLayerColor(index)
                }"
                @mouseover="hoveredLayer = index"
                @mouseleave="hoveredLayer = null"
              >
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <div class="layer-bar-content" v-bind="attrs" v-on="on">
                      {{ index + 1 }}
                    </div>
                  </template>
                  <span>
                    Layer {{ index + 1 }}: {{ formatSize(layer.size) }}<br>
                    {{ layer.sizePercentage.toFixed(1) }}% of total size
                  </span>
                </v-tooltip>
              </div>
            </div>
            <div class="text-caption text-right mt-1">
              Total Size: {{ formatSize(totalSize) }}
            </div>
          </div>
          
          <v-divider></v-divider>
          
          <!-- Layer Details -->
          <div class="layer-details">
            <v-expansion-panels
              v-model="expandedPanels"
              multiple
            >
              <v-expansion-panel
                v-for="(layer, index) in layers"
                :key="`layer-${index}`"
                :class="{ 'highlighted': hoveredLayer === index }"
              >
                <v-expansion-panel-header>
                  <div class="d-flex align-center">
                    <div
                      class="layer-indicator mr-2"
                      :style="{ backgroundColor: getLayerColor(index) }"
                    ></div>
                    <div>
                      <div class="text-subtitle-2">
                        Layer {{ index + 1 }}
                        <span class="text-caption ml-2">
                          {{ formatSize(layer.Size) }}
                        </span>
                      </div>
                      <div class="text-caption layer-command">
                        {{ getLayerCommand(layer) }}
                      </div>
                    </div>
                  </div>
                </v-expansion-panel-header>
                
                <v-expansion-panel-content>
                  <v-card flat outlined class="layer-details-card">
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <div class="text-subtitle-2 mb-2">Command</div>
                          <pre class="layer-command-pre">{{ getLayerCommand(layer) }}</pre>
                        </v-col>
                        
                        <v-col cols="12" md="6">
                          <div class="text-subtitle-2 mb-2">Details</div>
                          <v-list dense>
                            <v-list-item>
                              <v-list-item-content>
                                <v-list-item-title>Size</v-list-item-title>
                                <v-list-item-subtitle>{{ formatSize(layer.Size) }}</v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                            
                            <v-list-item v-if="layer.Created">
                              <v-list-item-content>
                                <v-list-item-title>Created</v-list-item-title>
                                <v-list-item-subtitle>{{ formatDate(layer.Created) }}</v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                            
                            <v-list-item v-if="layer.CreatedBy">
                              <v-list-item-content>
                                <v-list-item-title>Created By</v-list-item-title>
                                <v-list-item-subtitle>{{ layer.CreatedBy }}</v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                            
                            <v-list-item v-if="layer.Comment">
                              <v-list-item-content>
                                <v-list-item-title>Comment</v-list-item-title>
                                <v-list-item-subtitle>{{ layer.Comment }}</v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                            
                            <v-list-item>
                              <v-list-item-content>
                                <v-list-item-title>Empty Layer</v-list-item-title>
                                <v-list-item-subtitle>{{ layer.Size === 0 ? 'Yes' : 'No' }}</v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                          </v-list>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { format, parseISO } from 'date-fns';

export default {
  name: 'ImageLayerVisualization',
  
  props: {
    layers: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      expandedPanels: [],
      hoveredLayer: null,
      allExpanded: false
    };
  },
  
  computed: {
    totalSize() {
      return this.layers.reduce((total, layer) => total + (layer.Size || 0), 0);
    },
    
    layersWithSizes() {
      if (!this.layers || this.layers.length === 0 || this.totalSize === 0) {
        return [];
      }
      
      return this.layers.map(layer => {
        const size = layer.Size || 0;
        const sizePercentage = (size / this.totalSize) * 100;
        return {
          ...layer,
          size,
          sizePercentage
        };
      });
    }
  },
  
  methods: {
    expandAll() {
      this.expandedPanels = this.layers.map((_, index) => index);
      this.allExpanded = true;
    },
    
    collapseAll() {
      this.expandedPanels = [];
      this.allExpanded = false;
    },
    
    getLayerCommand(layer) {
      if (!layer) return 'Unknown';
      
      // Extract command from CreatedBy field
      if (layer.CreatedBy) {
        // Remove "/bin/sh -c " prefix if present
        let command = layer.CreatedBy;
        if (command.startsWith('/bin/sh -c ')) {
          command = command.substring('/bin/sh -c '.length);
        }
        
        // Remove "#(nop) " prefix if present
        if (command.startsWith('#(nop) ')) {
          command = command.substring('#(nop) '.length);
        }
        
        return command;
      }
      
      // Fallback to comment if available
      if (layer.Comment) {
        return layer.Comment;
      }
      
      return 'Unknown';
    },
    
    getLayerColor(index) {
      // Generate colors based on index
      const colors = [
        '#4CAF50', // Green
        '#2196F3', // Blue
        '#FFC107', // Amber
        '#FF5722', // Deep Orange
        '#9C27B0', // Purple
        '#00BCD4', // Cyan
        '#795548', // Brown
        '#607D8B', // Blue Grey
        '#E91E63', // Pink
        '#3F51B5'  // Indigo
      ];
      
      return colors[index % colors.length];
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
    
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      
      try {
        // Check if dateString is a timestamp
        if (typeof dateString === 'number') {
          return format(new Date(dateString * 1000), 'MMM d, yyyy HH:mm');
        }
        
        // Otherwise, parse as ISO string
        return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
      } catch (error) {
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.image-layer-visualization {
  width: 100%;
}

.layer-size-visualization {
  background-color: #f5f5f5;
}

.layer-bars {
  display: flex;
  height: 30px;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}

.layer-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  transition: opacity 0.2s;
  min-width: 20px;
}

.layer-bar:hover {
  opacity: 0.8;
}

.layer-bar-content {
  width: 100%;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layer-indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.layer-command {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 500px;
}

.layer-command-pre {
  white-space: pre-wrap;
  word-break: break-word;
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9rem;
}

.layer-details-card {
  background-color: #fafafa;
}

.highlighted {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
