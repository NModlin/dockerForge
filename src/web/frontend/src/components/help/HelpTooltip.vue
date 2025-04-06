<template>
  <v-tooltip
    bottom
    :max-width="300"
    open-delay="500"
    :disabled="!showTooltips"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        icon
        x-small
        color="primary"
        class="help-tooltip-btn"
        v-bind="attrs"
        v-on="on"
        @click.stop="showHelp"
      >
        <v-icon x-small>mdi-help-circle</v-icon>
      </v-btn>
    </template>
    <span v-html="content"></span>
  </v-tooltip>
</template>

<script>
export default {
  name: 'HelpTooltip',
  props: {
    content: {
      type: String,
      required: true
    },
    context: {
      type: String,
      default: null
    },
    identifier: {
      type: String,
      default: null
    }
  },
  computed: {
    showTooltips() {
      // Check user preferences for showing tooltips
      if (this.$store.hasModule('help')) {
        return this.$store.getters['help/userHelpPreferences'].showHelpTips;
      }
      return true;
    }
  },
  methods: {
    showHelp() {
      // Emit event to show contextual help panel
      this.$emit('show-help', {
        context: this.context,
        identifier: this.identifier
      });
    }
  }
};
</script>

<style scoped>
.help-tooltip-btn {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.help-tooltip-btn:hover {
  opacity: 1;
}
</style>
