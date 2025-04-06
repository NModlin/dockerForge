<template>
  <div class="build-args-editor">
    <v-card outlined>
      <v-card-title class="text-subtitle-1">
        <v-icon left>mdi-key-variant</v-icon>
        Build Arguments
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
            Build arguments are variables passed to the build process.<br>
            They can be used in the Dockerfile with the ARG instruction.
          </span>
        </v-tooltip>
        <v-spacer></v-spacer>
        <v-btn
          text
          small
          color="primary"
          @click="addArgument"
          :disabled="disabled"
        >
          <v-icon left small>mdi-plus</v-icon>
          Add Argument
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <div v-if="args.length === 0" class="text-center pa-4">
          <v-icon large color="grey lighten-1">mdi-key-variant</v-icon>
          <p class="text-body-2 mt-2 grey--text">No build arguments defined</p>
          <p class="text-caption grey--text">
            Build arguments are used with ARG instructions in your Dockerfile
          </p>
        </div>
        
        <v-row v-for="(arg, index) in args" :key="index" class="mt-2">
          <v-col cols="5">
            <v-text-field
              v-model="arg.key"
              label="Name"
              placeholder="ARG_NAME"
              dense
              outlined
              :rules="[v => !!v || 'Name is required', v => /^[a-zA-Z0-9_]+$/.test(v) || 'Only alphanumeric characters and underscore allowed']"
              :disabled="disabled"
              @input="validateAndUpdate"
            ></v-text-field>
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="arg.value"
              label="Value"
              placeholder="value"
              dense
              outlined
              :disabled="disabled"
              @input="validateAndUpdate"
            ></v-text-field>
          </v-col>
          <v-col cols="1" class="d-flex align-center">
            <v-btn
              icon
              small
              color="error"
              @click="removeArgument(index)"
              :disabled="disabled"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        
        <div v-if="args.length > 0" class="mt-4">
          <v-expansion-panels>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left>mdi-code-braces</v-icon>
                  Dockerfile Usage Example
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <pre class="dockerfile-example">{{ dockerfileExample }}</pre>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'BuildArgsEditor',
  
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
      args: []
    };
  },
  
  computed: {
    dockerfileExample() {
      if (this.args.length === 0) {
        return '';
      }
      
      let example = '# Example usage in Dockerfile:\n';
      
      this.args.forEach(arg => {
        if (arg.key) {
          example += `ARG ${arg.key}\n`;
        }
      });
      
      example += '\n# Using the arguments:\n';
      
      this.args.forEach(arg => {
        if (arg.key) {
          example += `# $${arg.key} will be replaced with "${arg.value || ''}"\n`;
        }
      });
      
      return example;
    }
  },
  
  watch: {
    value: {
      handler(newValue) {
        if (newValue && Object.keys(newValue).length > 0) {
          this.initializeArgs(newValue);
        }
      },
      immediate: true
    }
  },
  
  methods: {
    initializeArgs(argsObject) {
      this.args = Object.entries(argsObject).map(([key, value]) => ({
        key,
        value
      }));
    },
    
    addArgument() {
      this.args.push({
        key: '',
        value: ''
      });
    },
    
    removeArgument(index) {
      this.args.splice(index, 1);
      this.validateAndUpdate();
    },
    
    validateAndUpdate() {
      // Convert args array to object
      const argsObject = {};
      
      this.args.forEach(arg => {
        if (arg.key) {
          argsObject[arg.key] = arg.value;
        }
      });
      
      // Emit changes
      this.$emit('input', argsObject);
      this.$emit('update:modelValue', argsObject);
      this.$emit('change', argsObject);
    }
  }
};
</script>

<style scoped>
.build-args-editor {
  width: 100%;
}

.dockerfile-example {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
