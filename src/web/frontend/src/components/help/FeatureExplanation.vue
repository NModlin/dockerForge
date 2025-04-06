<template>
  <v-card class="feature-explanation" outlined>
    <v-card-title class="primary white--text">
      <v-icon left color="white">{{ icon }}</v-icon>
      {{ title }}
      <v-spacer></v-spacer>
      <v-btn icon @click="$emit('close')" class="white--text">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    
    <v-card-text class="pa-4">
      <div v-html="content"></div>
      
      <div v-if="steps && steps.length" class="mt-4">
        <v-subheader>How to use this feature</v-subheader>
        <v-timeline dense>
          <v-timeline-item
            v-for="(step, i) in steps"
            :key="i"
            small
            :color="step.color || 'primary'"
          >
            <div class="font-weight-bold mb-1">{{ step.title }}</div>
            <div v-html="step.content"></div>
          </v-timeline-item>
        </v-timeline>
      </div>
      
      <div v-if="tips && tips.length" class="mt-4">
        <v-subheader>Tips & Tricks</v-subheader>
        <v-list dense>
          <v-list-item v-for="(tip, i) in tips" :key="i">
            <v-list-item-icon>
              <v-icon color="info">mdi-lightbulb-on</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-subtitle v-html="tip"></v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </div>
      
      <div v-if="relatedFeatures && relatedFeatures.length" class="mt-4">
        <v-subheader>Related Features</v-subheader>
        <v-chip-group>
          <v-chip
            v-for="(feature, i) in relatedFeatures"
            :key="i"
            outlined
            color="primary"
            @click="showRelatedFeature(feature)"
          >
            <v-icon left small>{{ feature.icon || 'mdi-link-variant' }}</v-icon>
            {{ feature.title }}
          </v-chip>
        </v-chip-group>
      </div>
    </v-card-text>
    
    <v-card-actions>
      <v-btn text color="primary" @click="openDocumentation">
        <v-icon left>mdi-book-open-variant</v-icon>
        Read Documentation
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn text @click="askInChat">
        <v-icon left>mdi-message-question</v-icon>
        Ask in Chat
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'FeatureExplanation',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: 'mdi-information-outline'
    },
    content: {
      type: String,
      required: true
    },
    steps: {
      type: Array,
      default: () => []
    },
    tips: {
      type: Array,
      default: () => []
    },
    relatedFeatures: {
      type: Array,
      default: () => []
    },
    documentationLink: {
      type: String,
      default: null
    }
  },
  methods: {
    openDocumentation() {
      if (this.documentationLink) {
        if (this.documentationLink.startsWith('http')) {
          window.open(this.documentationLink, '_blank');
        } else {
          this.$router.push(this.documentationLink);
        }
      } else {
        this.$router.push('/help');
      }
    },
    askInChat() {
      const topic = this.title;
      this.$emit('ask-in-chat', `Can you help me with ${topic}?`);
    },
    showRelatedFeature(feature) {
      if (feature.route) {
        this.$router.push(feature.route);
      } else if (feature.action) {
        this.$emit('feature-action', feature.action);
      } else {
        this.$emit('show-related-feature', feature);
      }
    }
  }
};
</script>

<style scoped>
.feature-explanation {
  max-width: 600px;
  margin: 0 auto;
}

:deep(ul) {
  padding-left: 1.5rem;
}
</style>
