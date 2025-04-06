<template>
  <div class="tag-list">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-tag-multiple</v-icon>
        Image Tags
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          dense
          class="ml-2"
          style="max-width: 200px"
        ></v-text-field>
        <v-btn
          text
          small
          color="primary"
          class="ml-2"
          @click="openAddTagDialog"
          :disabled="!canManageTags"
        >
          <v-icon left small>mdi-tag-plus</v-icon>
          Add Tag
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text class="pa-0">
        <div v-if="loading" class="text-center pa-6">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="text-body-2 mt-2">Loading tags...</p>
        </div>
        
        <div v-else-if="!filteredTags.length" class="text-center pa-6">
          <v-icon large color="grey lighten-1">mdi-tag-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No tags found</p>
          <p v-if="search" class="text-caption grey--text">
            Try adjusting your search query
          </p>
        </div>
        
        <div v-else>
          <v-data-table
            :headers="headers"
            :items="filteredTags"
            :search="search"
            :sort-by="['created_at']"
            :sort-desc="[true]"
            :items-per-page="10"
            :footer-props="{
              'items-per-page-options': [5, 10, 15, 20, -1],
              'items-per-page-text': 'Tags per page'
            }"
            class="tag-table"
          >
            <!-- Tag Name Column -->
            <template v-slot:item.name="{ item }">
              <div class="d-flex align-center">
                <v-chip
                  small
                  :color="getTagColor(item)"
                  text-color="white"
                  class="mr-2"
                >
                  {{ item.name }}
                </v-chip>
                <v-icon
                  v-if="item.is_latest"
                  small
                  color="success"
                  title="Latest tag"
                >
                  mdi-star
                </v-icon>
              </div>
            </template>
            
            <!-- Created Column -->
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>
            
            <!-- Size Column -->
            <template v-slot:item.size="{ item }">
              {{ formatSize(item.size) }}
            </template>
            
            <!-- Actions Column -->
            <template v-slot:item.actions="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    icon
                    x-small
                    v-bind="attrs"
                    v-on="on"
                    @click="viewTagDetails(item)"
                  >
                    <v-icon x-small>mdi-eye</v-icon>
                  </v-btn>
                </template>
                <span>View Details</span>
              </v-tooltip>
              
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    icon
                    x-small
                    v-bind="attrs"
                    v-on="on"
                    @click="copyTagName(item)"
                  >
                    <v-icon x-small>mdi-content-copy</v-icon>
                  </v-btn>
                </template>
                <span>Copy Tag</span>
              </v-tooltip>
              
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    icon
                    x-small
                    color="error"
                    v-bind="attrs"
                    v-on="on"
                    @click="confirmDeleteTag(item)"
                    :disabled="!canManageTags || item.is_latest"
                  >
                    <v-icon x-small>mdi-delete</v-icon>
                  </v-btn>
                </template>
                <span>{{ item.is_latest ? 'Cannot delete latest tag' : 'Delete Tag' }}</span>
              </v-tooltip>
            </template>
          </v-data-table>
        </div>
      </v-card-text>
    </v-card>
    
    <!-- Add Tag Dialog -->
    <v-dialog v-model="addTagDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <v-icon left>mdi-tag-plus</v-icon>
          Add New Tag
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form ref="addTagForm" v-model="addTagFormValid" @submit.prevent="addTag">
            <v-text-field
              v-model="newTag.name"
              label="Tag Name"
              :rules="[v => !!v || 'Tag name is required', v => /^[a-zA-Z0-9._-]+$/.test(v) || 'Tag name can only contain alphanumeric characters, dots, hyphens, and underscores']"
              required
              outlined
              dense
              autofocus
            ></v-text-field>
            
            <v-checkbox
              v-model="newTag.is_latest"
              label="Set as latest tag"
              hint="This will update the 'latest' tag to point to this image"
              persistent-hint
            ></v-checkbox>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey darken-1" @click="addTagDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!addTagFormValid || addingTag"
            :loading="addingTag"
            @click="addTag"
          >
            Add Tag
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Tag Confirmation Dialog -->
    <v-dialog v-model="deleteTagDialog" max-width="500px">
      <v-card>
        <v-card-title class="headline">
          <v-icon left color="error">mdi-alert</v-icon>
          Confirm Delete
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="py-4">
          <p>Are you sure you want to delete the tag <strong>{{ tagToDelete ? tagToDelete.name : '' }}</strong>?</p>
          <p class="text-caption mt-2">This action cannot be undone. The tag will be removed, but the image content will remain if other tags reference it.</p>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="grey darken-1" @click="deleteTagDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            :loading="deletingTag"
            @click="deleteTag"
          >
            Delete Tag
          </v-btn>
        </v-card-actions>
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
  name: 'TagList',
  
  props: {
    tags: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    canManageTags: {
      type: Boolean,
      default: true
    },
    imageId: {
      type: String,
      default: null
    }
  },
  
  data() {
    return {
      search: '',
      headers: [
        { text: 'Tag', value: 'name', sortable: true },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Size', value: 'size', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      addTagDialog: false,
      deleteTagDialog: false,
      addTagFormValid: false,
      newTag: {
        name: '',
        is_latest: false
      },
      tagToDelete: null,
      addingTag: false,
      deletingTag: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success'
    };
  },
  
  computed: {
    filteredTags() {
      if (!this.tags) return [];
      
      // Apply search filter
      let filtered = [...this.tags];
      
      if (this.search) {
        const searchLower = this.search.toLowerCase();
        filtered = filtered.filter(tag => 
          tag.name.toLowerCase().includes(searchLower)
        );
      }
      
      return filtered;
    }
  },
  
  methods: {
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
    
    viewTagDetails(tag) {
      this.$emit('view-tag', tag);
    },
    
    copyTagName(tag) {
      navigator.clipboard.writeText(tag.name)
        .then(() => {
          this.showSnackbar(`Tag "${tag.name}" copied to clipboard`, 'success');
        })
        .catch(err => {
          console.error('Failed to copy tag name: ', err);
          this.showSnackbar('Failed to copy tag name', 'error');
        });
    },
    
    openAddTagDialog() {
      this.newTag = {
        name: '',
        is_latest: false
      };
      this.addTagDialog = true;
      
      // Focus the tag name input after dialog is shown
      this.$nextTick(() => {
        if (this.$refs.addTagForm) {
          const input = this.$refs.addTagForm.$el.querySelector('input');
          if (input) input.focus();
        }
      });
    },
    
    async addTag() {
      if (!this.addTagFormValid) return;
      
      this.addingTag = true;
      
      try {
        // Emit event to parent component to handle the actual API call
        await this.$emit('add-tag', {
          imageId: this.imageId,
          tagName: this.newTag.name,
          isLatest: this.newTag.is_latest
        });
        
        this.showSnackbar(`Tag "${this.newTag.name}" added successfully`, 'success');
        this.addTagDialog = false;
      } catch (error) {
        console.error('Error adding tag:', error);
        this.showSnackbar(`Failed to add tag: ${error.message || 'Unknown error'}`, 'error');
      } finally {
        this.addingTag = false;
      }
    },
    
    confirmDeleteTag(tag) {
      this.tagToDelete = tag;
      this.deleteTagDialog = true;
    },
    
    async deleteTag() {
      if (!this.tagToDelete) return;
      
      this.deletingTag = true;
      
      try {
        // Emit event to parent component to handle the actual API call
        await this.$emit('delete-tag', {
          imageId: this.imageId,
          tagName: this.tagToDelete.name
        });
        
        this.showSnackbar(`Tag "${this.tagToDelete.name}" deleted successfully`, 'success');
        this.deleteTagDialog = false;
        this.tagToDelete = null;
      } catch (error) {
        console.error('Error deleting tag:', error);
        this.showSnackbar(`Failed to delete tag: ${error.message || 'Unknown error'}`, 'error');
      } finally {
        this.deletingTag = false;
      }
    },
    
    showSnackbar(text, color = 'success') {
      this.snackbarText = text;
      this.snackbarColor = color;
      this.snackbar = true;
    }
  }
};
</script>

<style scoped>
.tag-list {
  width: 100%;
}

.tag-table {
  width: 100%;
}
</style>
