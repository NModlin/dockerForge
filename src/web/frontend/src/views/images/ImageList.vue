<template>
  <div class="image-list">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              Docker Images
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
                class="mx-4"
              ></v-text-field>
              <v-btn color="primary" @click="openPullDialog" class="mr-2">
                <v-icon left>mdi-cloud-download</v-icon>
                Pull Image
              </v-btn>
              <v-btn color="secondary" @click="navigateToBuildPage" class="mr-2">
                <v-icon left>mdi-hammer-wrench</v-icon>
                Build Image
              </v-btn>
              <v-btn color="info" @click="navigateToTagManagement">
                <v-icon left>mdi-tag-multiple</v-icon>
                Manage Tags
              </v-btn>
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="images"
              :search="search"
              :loading="loading"
              :items-per-page="10"
              :footer-props="{
                'items-per-page-options': [5, 10, 15, 20, 50],
              }"
              class="elevation-1"
            >
              <template v-slot:item.tags="{ item }">
                <v-chip
                  v-for="tag in item.tags"
                  :key="tag"
                  class="ma-1"
                  small
                  color="primary"
                  text-color="white"
                >
                  {{ tag }}
                </v-chip>
              </template>
              <template v-slot:item.size="{ item }">
                {{ formatSize(item.size) }}
              </template>
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon small @click="viewImageDetails(item)">
                  <v-icon small>mdi-eye</v-icon>
                </v-btn>
                <v-btn icon small @click="scanImage(item)">
                  <v-icon small>mdi-shield-search</v-icon>
                </v-btn>
                <v-btn icon small @click="confirmDeleteImage(item)">
                  <v-icon small color="error">mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Pull Image Dialog -->
    <v-dialog v-model="pullDialog" max-width="800px" persistent>
      <image-pull
        @close="closePullDialog"
        @pulled="fetchImages"
      />
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>Delete Image</v-card-title>
        <v-card-text>
          Are you sure you want to delete this image?
          <div class="mt-2">
            <strong>ID:</strong> {{ selectedImage?.id }}
          </div>
          <div v-if="selectedImage?.tags && selectedImage.tags.length > 0">
            <strong>Tags:</strong>
            <v-chip
              v-for="tag in selectedImage.tags"
              :key="tag"
              class="ma-1"
              small
              color="primary"
              text-color="white"
            >
              {{ tag }}
            </v-chip>
          </div>
          <v-checkbox
            v-model="forceDelete"
            label="Force delete (remove even if used by containers)"
            class="mt-4"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDeleteDialog">Cancel</v-btn>
          <v-btn
            color="red darken-1"
            text
            @click="deleteImage"
            :loading="deleting"
            :disabled="deleting"
          >
            Delete
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
import { mapState, mapActions } from 'vuex';
import { format, parseISO } from 'date-fns';
import ImagePull from './ImagePull.vue';

export default {
  name: 'ImageList',

  components: {
    ImagePull,
  },

  data() {
    return {
      search: '',
      headers: [
        { text: 'ID', value: 'short_id' },
        { text: 'Tags', value: 'tags' },
        { text: 'Size', value: 'size' },
        { text: 'Created', value: 'created_at' },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      loading: false,
      pullDialog: false,
      deleteDialog: false,

      selectedImage: null,
      pulling: false,
      deleting: false,
      forceDelete: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },

  computed: {
    ...mapState('images', ['images']),
  },

  created() {
    this.fetchImages();
  },

  methods: {
    ...mapActions('images', ['getImages', 'pullImage', 'removeImage', 'scanImageVulnerabilities']),

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

    openPullDialog() {
      this.pullDialog = true;
    },

    closePullDialog() {
      this.pullDialog = false;
    },

    confirmDeleteImage(image) {
      this.selectedImage = image;
      this.deleteDialog = true;
      this.forceDelete = false;
    },

    closeDeleteDialog() {
      this.deleteDialog = false;
      this.selectedImage = null;
    },

    async deleteImage() {
      if (!this.selectedImage) return;

      this.deleting = true;
      try {
        await this.removeImage({
          id: this.selectedImage.id,
          force: this.forceDelete,
        });
        this.closeDeleteDialog();
        this.showSuccess('Image deleted successfully');
        this.fetchImages();
      } catch (error) {
        this.showError('Failed to delete image: ' + error.message);
      } finally {
        this.deleting = false;
      }
    },

    viewImageDetails(image) {
      this.$router.push({ name: 'ImageDetail', params: { id: image.id } });
    },

    navigateToBuildPage() {
      this.$router.push({ name: 'ImageBuild' });
    },

    navigateToTagManagement() {
      this.$router.push({ name: 'TagManagement' });
    },

    async scanImage(image) {
      try {
        await this.scanImageVulnerabilities(image.id);
        this.showSuccess('Security scan initiated');
        this.$router.push({ name: 'ImageSecurity', params: { id: image.id } });
      } catch (error) {
        this.showError('Failed to scan image: ' + error.message);
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
    },
  },
};
</script>

<style scoped>
.image-list {
  height: 100%;
}
</style>
