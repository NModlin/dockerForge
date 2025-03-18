<template>
  <div class="chat-preferences">
    <v-card outlined class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon left small>mdi-cog</v-icon>
        AI Assistant Preferences
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <v-form ref="form">
          <!-- Response Style -->
          <div class="mb-3">
            <div class="text-subtitle-2 mb-1">Response Style</div>
            <v-radio-group
              v-model="preferences.response_style"
              hide-details
              dense
              row
              @change="savePreferences"
            >
              <v-radio
                label="Technical"
                value="technical"
                dense
              ></v-radio>
              <v-radio
                label="Balanced"
                value="balanced"
                dense
              ></v-radio>
              <v-radio
                label="Simple"
                value="simple"
                dense
              ></v-radio>
            </v-radio-group>
          </div>
          
          <!-- Auto Suggestions -->
          <div class="mb-3">
            <v-switch
              v-model="preferences.auto_suggestions"
              label="Show automatic suggestions"
              hide-details
              dense
              @change="savePreferences"
            ></v-switch>
          </div>
          
          <!-- Preferred Topics -->
          <div class="mb-3">
            <div class="text-subtitle-2 mb-1">Preferred Topics</div>
            <v-combobox
              v-model="preferences.preferred_topics"
              :items="availableTopics"
              chips
              multiple
              small-chips
              dense
              hide-details
              placeholder="Select or type topics you're interested in"
              @change="savePreferences"
            ></v-combobox>
          </div>
          
          <!-- Avoided Topics -->
          <div class="mb-3">
            <div class="text-subtitle-2 mb-1">Avoided Topics</div>
            <v-combobox
              v-model="preferences.avoided_topics"
              :items="availableTopics"
              chips
              multiple
              small-chips
              dense
              hide-details
              placeholder="Select or type topics you want to avoid"
              @change="savePreferences"
            ></v-combobox>
          </div>
        </v-form>
      </v-card-text>
      
      <!-- Feedback Statistics (Read-only) -->
      <v-divider></v-divider>
      
      <v-card-title class="text-subtitle-1 pt-3">
        <v-icon left small>mdi-chart-bar</v-icon>
        Feedback Summary
      </v-card-title>
      
      <v-card-text>
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2">Positive Feedback:</span>
          <span class="text-body-2">{{ positiveFeedbackCount }}</span>
        </div>
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2">Negative Feedback:</span>
          <span class="text-body-2">{{ negativeFeedbackCount }}</span>
        </div>
        <div class="d-flex justify-space-between mb-2">
          <span class="text-body-2">Last Feedback:</span>
          <span class="text-body-2">{{ formattedLastFeedbackTime }}</span>
        </div>
        
        <!-- Top Rated Topics -->
        <div class="mt-4" v-if="topRatedTopics.length > 0">
          <div class="text-subtitle-2 mb-2">Top Rated Topics</div>
          <v-chip
            v-for="topic in topRatedTopics"
            :key="topic.name"
            class="mr-2 mb-2"
            x-small
            :color="getTopicColor(topic.avgRating)"
            text-color="white"
          >
            {{ topic.name }} ({{ topic.avgRating.toFixed(1) }})
          </v-chip>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'ChatPreferences',
  
  data() {
    return {
      // Default topics
      availableTopics: [
        'containers', 
        'images', 
        'volumes', 
        'networks', 
        'security', 
        'troubleshooting',
        'backup',
        'configuration'
      ],
      // Local copy of preferences for editing
      preferences: {
        response_style: 'balanced',
        auto_suggestions: true,
        preferred_topics: [],
        avoided_topics: []
      },
      saving: false
    };
  },
  
  computed: {
    ...mapState('chat', ['userPreferences']),
    
    // Feedback statistics
    positiveFeedbackCount() {
      return this.userPreferences?.feedback_preferences?.positively_rated_responses || 0;
    },
    
    negativeFeedbackCount() {
      return this.userPreferences?.feedback_preferences?.negatively_rated_responses || 0;
    },
    
    formattedLastFeedbackTime() {
      const lastTime = this.userPreferences?.feedback_preferences?.last_feedback_time;
      if (!lastTime) return 'None';
      
      try {
        const date = new Date(lastTime);
        return date.toLocaleString();
      } catch (e) {
        return 'Invalid date';
      }
    },
    
    // Extract top rated topics
    topRatedTopics() {
      const topicRatings = this.userPreferences?.feedback_preferences?.topic_ratings || {};
      
      // Convert to array and sort by average rating
      return Object.entries(topicRatings)
        .map(([name, data]) => ({
          name,
          count: data.count,
          avgRating: data.avg_rating
        }))
        .filter(topic => topic.count >= 2) // Only include topics with multiple ratings
        .sort((a, b) => b.avgRating - a.avgRating)
        .slice(0, 5); // Top 5
    }
  },
  
  methods: {
    ...mapActions('chat', ['updateUserPreferences']),
    
    // Save preferences to store and API
    async savePreferences() {
      if (this.saving) return;
      
      this.saving = true;
      
      try {
        await this.updateUserPreferences(this.preferences);
        
        // Show success notification
        this.$emit('notification', {
          type: 'success',
          message: 'Preferences saved successfully'
        });
      } catch (error) {
        console.error('Error saving preferences:', error);
        
        // Show error notification
        this.$emit('notification', {
          type: 'error',
          message: 'Failed to save preferences'
        });
        
        // Reset to stored preferences
        this.preferences = { ...this.userPreferences };
      } finally {
        this.saving = false;
      }
    },
    
    // Get color for topic chip based on rating
    getTopicColor(rating) {
      if (rating >= 4.5) return 'green darken-1';
      if (rating >= 4.0) return 'green';
      if (rating >= 3.5) return 'lime darken-2';
      if (rating >= 3.0) return 'orange';
      if (rating >= 2.5) return 'amber darken-2';
      return 'red';
    }
  },
  
  watch: {
    // Update local preferences when store changes
    userPreferences: {
      handler(newVal) {
        if (newVal) {
          this.preferences = {
            response_style: newVal.response_style || 'balanced',
            auto_suggestions: newVal.auto_suggestions !== undefined ? newVal.auto_suggestions : true,
            preferred_topics: [...(newVal.preferred_topics || [])],
            avoided_topics: [...(newVal.avoided_topics || [])]
          };
        }
      },
      immediate: true,
      deep: true
    }
  }
};
</script>

<style scoped>
.chat-preferences {
  margin-bottom: 16px;
}
</style>
