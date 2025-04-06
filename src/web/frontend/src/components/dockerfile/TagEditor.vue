<template>
  <div class="tag-editor">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-tag-multiple</v-icon>
        Image Tags
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              icon
              x-small
              class="ml-2"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon x-small>mdi-help-circle</v-icon>
            </v-btn>
          </template>
          <span>
            Tags are used to identify different versions of the same image.<br>
            You can add multiple tags to the same image.
          </span>
        </v-tooltip>
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="addTag"
          :disabled="disabled"
        >
          <v-icon left small>mdi-plus</v-icon>
          Add Tag
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="imageName"
              label="Image Name"
              placeholder="e.g., myapp"
              outlined
              dense
              :rules="[v => !!v || 'Image name is required', v => /^[a-z0-9._-]+$/.test(v) || 'Only lowercase letters, numbers, dots, hyphens, and underscores allowed']"
              :disabled="disabled"
              @input="validateAndUpdate"
            ></v-text-field>
          </v-col>
        </v-row>
        
        <div v-if="tags.length === 0" class="text-center pa-4">
          <v-icon large color="grey lighten-1">mdi-tag-outline</v-icon>
          <p class="text-body-2 mt-2 grey--text">No tags defined</p>
          <p class="text-caption grey--text">
            Add at least one tag to identify your image
          </p>
        </div>
        
        <v-row v-for="(tag, index) in tags" :key="index" class="mt-2">
          <v-col cols="11">
            <v-text-field
              v-model="tags[index]"
              :label="index === 0 ? 'Primary Tag' : `Additional Tag ${index}`"
              placeholder="e.g., latest, v1.0.0"
              dense
              outlined
              :rules="[v => !!v || 'Tag is required', v => /^[a-zA-Z0-9._-]+$/.test(v) || 'Only alphanumeric characters, dots, hyphens, and underscores allowed']"
              :disabled="disabled"
              @input="validateAndUpdate"
            ></v-text-field>
          </v-col>
          <v-col cols="1" class="d-flex align-center">
            <v-btn
              v-if="index > 0"
              icon
              small
              color="error"
              @click="removeTag(index)"
              :disabled="disabled"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        
        <v-row v-if="tags.length > 0" class="mt-4">
          <v-col cols="12">
            <v-card outlined class="pa-3 tag-preview">
              <div class="text-subtitle-2 mb-2">Tag Preview:</div>
              <div v-for="(tag, index) in tags" :key="`preview-${index}`" class="mb-1">
                <v-chip
                  small
                  color="primary"
                  text-color="white"
                  class="mr-2"
                >
                  {{ imageName }}:{{ tag }}
                </v-chip>
                <span class="text-caption grey--text">
                  {{ index === 0 ? '(primary)' : '' }}
                </span>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'TagEditor',
  
  props: {
    value: {
      type: Object,
      default: () => ({ name: '', tags: ['latest'] })
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      imageName: '',
      tags: ['latest']
    };
  },
  
  watch: {
    value: {
      handler(newValue) {
        if (newValue) {
          this.imageName = newValue.name || '';
          this.tags = newValue.tags && newValue.tags.length > 0 ? [...newValue.tags] : ['latest'];
        }
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    addTag() {
      this.tags.push('');
      this.validateAndUpdate();
    },
    
    removeTag(index) {
      if (index > 0) {
        this.tags.splice(index, 1);
        this.validateAndUpdate();
      }
    },
    
    validateAndUpdate() {
      // Filter out empty tags
      const filteredTags = this.tags.filter(tag => tag.trim() !== '');
      
      // Ensure there's at least one tag
      if (filteredTags.length === 0) {
        filteredTags.push('latest');
      }
      
      // Update tags array
      this.tags = filteredTags;
      
      // Emit changes
      this.$emit('input', {
        name: this.imageName,
        tags: this.tags
      });
      this.$emit('update:modelValue', {
        name: this.imageName,
        tags: this.tags
      });
      this.$emit('change', {
        name: this.imageName,
        tags: this.tags
      });
    }
  }
};
</script>

<style scoped>
.tag-editor {
  width: 100%;
}

.tag-preview {
  background-color: #f5f5f5;
}
</style>
