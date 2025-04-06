<template>
  <div class="image-history-timeline">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-timeline</v-icon>
        Image History Timeline
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
        <div v-if="!history || history.length === 0" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-timeline-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No history information available</p>
        </div>
        
        <div v-else>
          <div class="timeline-container pa-4">
            <div class="timeline">
              <div
                v-for="(item, index) in reversedHistory"
                :key="`timeline-${index}`"
                class="timeline-item"
                :class="{ 'last-item': index === reversedHistory.length - 1 }"
              >
                <div class="timeline-marker">
                  <v-avatar
                    size="36"
                    :color="getCommandColor(item)"
                    class="timeline-avatar"
                    @click="selectHistoryItem(item)"
                    :class="{ 'selected': selectedItem === item }"
                  >
                    <v-icon dark>{{ getCommandIcon(item) }}</v-icon>
                  </v-avatar>
                </div>
                
                <div class="timeline-content">
                  <div class="timeline-header">
                    <div class="d-flex align-center">
                      <div class="text-subtitle-2">{{ getCommandType(item) }}</div>
                      <v-spacer></v-spacer>
                      <div class="text-caption">{{ formatDate(item.Created) }}</div>
                    </div>
                  </div>
                  
                  <div class="timeline-body">
                    <div class="command-preview">{{ getCommandPreview(item) }}</div>
                    
                    <div class="mt-2 d-flex align-center">
                      <v-chip
                        x-small
                        :color="item.Size > 0 ? 'primary' : 'grey'"
                        text-color="white"
                        class="mr-2"
                      >
                        {{ formatSize(item.Size) }}
                      </v-chip>
                      
                      <v-btn
                        x-small
                        text
                        color="primary"
                        @click="toggleDetails(index)"
                      >
                        {{ expandedItems.includes(index) ? 'Hide Details' : 'Show Details' }}
                      </v-btn>
                    </div>
                    
                    <v-expand-transition>
                      <div v-if="expandedItems.includes(index)" class="mt-2">
                        <v-card flat outlined class="command-details">
                          <v-card-text>
                            <div class="text-subtitle-2 mb-2">Command</div>
                            <pre class="command-pre">{{ getFullCommand(item) }}</pre>
                            
                            <div class="text-subtitle-2 mb-2 mt-4">Details</div>
                            <v-simple-table dense>
                              <template v-slot:default>
                                <tbody>
                                  <tr>
                                    <td class="font-weight-medium">Size</td>
                                    <td>{{ formatSize(item.Size) }}</td>
                                  </tr>
                                  <tr>
                                    <td class="font-weight-medium">Created</td>
                                    <td>{{ formatDate(item.Created) }}</td>
                                  </tr>
                                  <tr v-if="item.Comment">
                                    <td class="font-weight-medium">Comment</td>
                                    <td>{{ item.Comment }}</td>
                                  </tr>
                                  <tr>
                                    <td class="font-weight-medium">Empty Layer</td>
                                    <td>{{ item.Size === 0 ? 'Yes' : 'No' }}</td>
                                  </tr>
                                </tbody>
                              </template>
                            </v-simple-table>
                          </v-card-text>
                        </v-card>
                      </div>
                    </v-expand-transition>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { format, parseISO } from 'date-fns';

export default {
  name: 'ImageHistoryTimeline',
  
  props: {
    history: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      expandedItems: [],
      selectedItem: null,
      allExpanded: false
    };
  },
  
  computed: {
    reversedHistory() {
      // Display history in reverse order (newest first)
      return [...this.history].reverse();
    }
  },
  
  methods: {
    expandAll() {
      this.expandedItems = this.history.map((_, index) => index);
      this.allExpanded = true;
    },
    
    collapseAll() {
      this.expandedItems = [];
      this.allExpanded = false;
    },
    
    toggleDetails(index) {
      const position = this.expandedItems.indexOf(index);
      if (position === -1) {
        this.expandedItems.push(index);
      } else {
        this.expandedItems.splice(position, 1);
      }
      
      // Update allExpanded state
      this.allExpanded = this.expandedItems.length === this.history.length;
    },
    
    selectHistoryItem(item) {
      this.selectedItem = this.selectedItem === item ? null : item;
      this.$emit('select-item', this.selectedItem);
    },
    
    getCommandType(item) {
      if (!item || !item.CreatedBy) return 'Unknown';
      
      const command = item.CreatedBy;
      
      if (command.includes('#(nop)')) {
        // Non-operation commands (metadata)
        if (command.includes('FROM')) return 'FROM';
        if (command.includes('LABEL')) return 'LABEL';
        if (command.includes('MAINTAINER')) return 'MAINTAINER';
        if (command.includes('EXPOSE')) return 'EXPOSE';
        if (command.includes('ENV')) return 'ENV';
        if (command.includes('ENTRYPOINT')) return 'ENTRYPOINT';
        if (command.includes('CMD')) return 'CMD';
        if (command.includes('VOLUME')) return 'VOLUME';
        if (command.includes('USER')) return 'USER';
        if (command.includes('WORKDIR')) return 'WORKDIR';
        if (command.includes('ARG')) return 'ARG';
        if (command.includes('ONBUILD')) return 'ONBUILD';
        if (command.includes('STOPSIGNAL')) return 'STOPSIGNAL';
        if (command.includes('HEALTHCHECK')) return 'HEALTHCHECK';
        if (command.includes('SHELL')) return 'SHELL';
        return 'Metadata';
      } else {
        // Operation commands
        if (command.includes('RUN')) return 'RUN';
        if (command.includes('COPY')) return 'COPY';
        if (command.includes('ADD')) return 'ADD';
        return 'Operation';
      }
    },
    
    getCommandIcon(item) {
      const type = this.getCommandType(item);
      
      switch (type) {
        case 'FROM':
          return 'mdi-package-variant';
        case 'RUN':
          return 'mdi-console';
        case 'COPY':
        case 'ADD':
          return 'mdi-file-multiple';
        case 'ENV':
          return 'mdi-variable';
        case 'WORKDIR':
          return 'mdi-folder';
        case 'EXPOSE':
          return 'mdi-network';
        case 'VOLUME':
          return 'mdi-database';
        case 'ENTRYPOINT':
        case 'CMD':
          return 'mdi-play';
        case 'USER':
          return 'mdi-account';
        case 'LABEL':
          return 'mdi-tag';
        case 'ARG':
          return 'mdi-key-variant';
        case 'HEALTHCHECK':
          return 'mdi-heart-pulse';
        default:
          return 'mdi-docker';
      }
    },
    
    getCommandColor(item) {
      const type = this.getCommandType(item);
      
      switch (type) {
        case 'FROM':
          return '#4CAF50'; // Green
        case 'RUN':
          return '#FF5722'; // Deep Orange
        case 'COPY':
        case 'ADD':
          return '#2196F3'; // Blue
        case 'ENV':
          return '#9C27B0'; // Purple
        case 'WORKDIR':
          return '#795548'; // Brown
        case 'EXPOSE':
          return '#00BCD4'; // Cyan
        case 'VOLUME':
          return '#3F51B5'; // Indigo
        case 'ENTRYPOINT':
        case 'CMD':
          return '#FFC107'; // Amber
        case 'USER':
          return '#E91E63'; // Pink
        case 'LABEL':
          return '#607D8B'; // Blue Grey
        case 'ARG':
          return '#8BC34A'; // Light Green
        case 'HEALTHCHECK':
          return '#F44336'; // Red
        default:
          return '#9E9E9E'; // Grey
      }
    },
    
    getCommandPreview(item) {
      if (!item || !item.CreatedBy) return 'Unknown';
      
      // Extract command from CreatedBy field
      let command = item.CreatedBy;
      
      // Remove "/bin/sh -c " prefix if present
      if (command.startsWith('/bin/sh -c ')) {
        command = command.substring('/bin/sh -c '.length);
      }
      
      // Remove "#(nop) " prefix if present
      if (command.startsWith('#(nop) ')) {
        command = command.substring('#(nop) '.length);
      }
      
      // Truncate if too long
      if (command.length > 100) {
        return command.substring(0, 100) + '...';
      }
      
      return command;
    },
    
    getFullCommand(item) {
      if (!item || !item.CreatedBy) return 'Unknown';
      
      // Extract command from CreatedBy field
      let command = item.CreatedBy;
      
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
.image-history-timeline {
  width: 100%;
}

.timeline-container {
  position: relative;
}

.timeline {
  position: relative;
  padding: 0;
  margin: 0;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  display: flex;
}

.timeline-item.last-item {
  margin-bottom: 0;
}

.timeline-marker {
  position: relative;
  flex: 0 0 40px;
  margin-right: 16px;
}

.timeline-marker::after {
  content: '';
  position: absolute;
  top: 36px;
  left: 18px;
  width: 2px;
  height: calc(100% + 24px);
  background-color: #e0e0e0;
  z-index: 0;
}

.timeline-item.last-item .timeline-marker::after {
  display: none;
}

.timeline-avatar {
  z-index: 1;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.timeline-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.timeline-avatar.selected {
  transform: scale(1.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.timeline-content {
  flex: 1;
  padding: 0 0 0 8px;
}

.timeline-header {
  margin-bottom: 8px;
}

.timeline-body {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 12px;
}

.command-preview {
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.command-details {
  background-color: #fafafa;
}

.command-pre {
  white-space: pre-wrap;
  word-break: break-word;
  background-color: #f0f0f0;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9rem;
}
</style>
