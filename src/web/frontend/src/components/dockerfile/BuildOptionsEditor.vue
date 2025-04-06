<template>
  <div class="build-options-editor">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-cog</v-icon>
        Build Options
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
            Configure additional options for the Docker build process.
          </span>
        </v-tooltip>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-switch
              v-model="options.noCache"
              label="No Cache"
              hint="Do not use cache when building the image"
              persistent-hint
              :disabled="disabled"
              @change="updateOptions"
            ></v-switch>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-switch
              v-model="options.pull"
              label="Always Pull"
              hint="Always pull the newer version of the base image"
              persistent-hint
              :disabled="disabled"
              @change="updateOptions"
            ></v-switch>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12" md="6">
            <v-switch
              v-model="options.rm"
              label="Remove Intermediate Containers"
              hint="Remove intermediate containers after a successful build"
              persistent-hint
              :disabled="disabled"
              @change="updateOptions"
            ></v-switch>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-switch
              v-model="options.forcerm"
              label="Force Remove Intermediate Containers"
              hint="Always remove intermediate containers, even upon failure"
              persistent-hint
              :disabled="disabled"
              @change="updateOptions"
            ></v-switch>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12" md="6">
            <v-switch
              v-model="options.squash"
              label="Squash Layers"
              hint="Squash newly built layers into a single new layer"
              persistent-hint
              :disabled="disabled"
              @change="updateOptions"
            ></v-switch>
          </v-col>
          
          <v-col cols="12" md="6">
            <v-select
              v-model="options.platform"
              :items="platformOptions"
              label="Platform"
              hint="Set platform if server is multi-platform capable"
              persistent-hint
              outlined
              dense
              :disabled="disabled"
              @change="updateOptions"
            ></v-select>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="options.target"
              label="Target Stage"
              hint="Name of the target build stage in a multi-stage build"
              persistent-hint
              outlined
              dense
              :disabled="disabled"
              @input="updateOptions"
            ></v-text-field>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            <v-slider
              v-model="options.memory"
              label="Memory Limit"
              hint="Memory limit for the build container (in MB)"
              persistent-hint
              :min="0"
              :max="8192"
              :step="256"
              thumb-label="always"
              :disabled="disabled"
              @change="updateOptions"
            >
              <template v-slot:append>
                <v-text-field
                  v-model="options.memory"
                  type="number"
                  style="width: 100px"
                  outlined
                  dense
                  hide-details
                  :disabled="disabled"
                  @input="updateOptions"
                ></v-text-field>
                <span class="ml-2">MB</span>
              </template>
            </v-slider>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'BuildOptionsEditor',
  
  props: {
    value: {
      type: Object,
      default: () => ({})
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      options: {
        noCache: false,
        pull: false,
        rm: true,
        forcerm: false,
        squash: false,
        platform: '',
        target: '',
        memory: 0
      },
      platformOptions: [
        { text: 'Default', value: '' },
        { text: 'linux/amd64', value: 'linux/amd64' },
        { text: 'linux/arm64', value: 'linux/arm64' },
        { text: 'linux/arm/v7', value: 'linux/arm/v7' },
        { text: 'linux/arm/v6', value: 'linux/arm/v6' },
        { text: 'linux/386', value: 'linux/386' },
        { text: 'linux/ppc64le', value: 'linux/ppc64le' },
        { text: 'linux/s390x', value: 'linux/s390x' },
        { text: 'windows/amd64', value: 'windows/amd64' }
      ]
    };
  },
  
  watch: {
    value: {
      handler(newValue) {
        if (newValue) {
          // Merge new values with defaults
          this.options = {
            ...this.options,
            ...newValue
          };
        }
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    updateOptions() {
      // Create a clean options object (remove empty values)
      const cleanOptions = {};
      
      Object.entries(this.options).forEach(([key, value]) => {
        // Only include non-empty values
        if (value !== '' && value !== 0 && value !== false) {
          cleanOptions[key] = value;
        }
      });
      
      // Emit changes
      this.$emit('input', cleanOptions);
      this.$emit('update:modelValue', cleanOptions);
      this.$emit('change', cleanOptions);
    }
  }
};
</script>

<style scoped>
.build-options-editor {
  width: 100%;
}
</style>
