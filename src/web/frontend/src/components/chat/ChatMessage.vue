<template>
  <div :class="['chat-message', `chat-message--${message.type}`]">
    <div class="chat-message__avatar" v-if="message.type === 'ai'">
      <v-avatar color="primary" size="36">
        <v-icon dark>mdi-robot</v-icon>
      </v-avatar>
    </div>
    <div class="chat-message__avatar" v-else-if="message.type === 'user'">
      <v-avatar color="grey lighten-1" size="36">
        <v-icon dark>mdi-account</v-icon>
      </v-avatar>
    </div>
    <div class="chat-message__content">
      <div class="chat-message__name" v-if="message.type === 'ai'">DockerForge AI</div>
      <div class="chat-message__name" v-else-if="message.type === 'user'">You</div>
      <div class="chat-message__text">{{ message.text }}</div>
      <div class="chat-message__time">{{ formattedTime }}</div>
      
      <!-- Phase 7: Message feedback UI (only for AI messages) -->
      <div class="chat-message__feedback" v-if="message.type === 'ai' && !feedbackSubmitted">
        <v-divider class="my-2"></v-divider>
        <div class="text-caption text-center mb-1">Was this response helpful?</div>
        <div class="d-flex justify-center">
          <v-rating
            v-model="feedbackRating"
            color="amber"
            hover
            dense
            half-increments
            size="small"
            length="5"
            @input="onRatingChange"
          ></v-rating>
        </div>
        <div v-if="feedbackRating && feedbackRating <= 3" class="mt-2">
          <v-textarea
            v-model="feedbackText"
            rows="2"
            dense
            hide-details
            placeholder="Please tell us how we can improve"
            class="text-caption"
          ></v-textarea>
          <div class="d-flex justify-end mt-1">
            <v-btn
              x-small
              text
              color="primary"
              @click="submitFeedback"
              :disabled="submittingFeedback"
            >
              Submit Feedback
              <v-progress-circular
                v-if="submittingFeedback"
                indeterminate
                size="16"
                class="ml-2"
              ></v-progress-circular>
            </v-btn>
          </div>
        </div>
      </div>
      <div class="chat-message__feedback-submitted" v-else-if="message.type === 'ai' && feedbackSubmitted">
        <v-divider class="my-2"></v-divider>
        <div class="text-caption text-center">
          <v-icon small color="success">mdi-check-circle</v-icon>
          Thank you for your feedback!
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ChatMessage',
  props: {
    message: {
      type: Object,
      required: true,
      validator: (prop) => {
        return prop.type && prop.text && prop.timestamp;
      }
    },
    // Phase 7: Pass existing feedback to avoid duplicates
    existingFeedback: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      // Phase 7: Feedback data
      feedbackRating: 0,
      feedbackText: '',
      feedbackSubmitted: !!this.existingFeedback,
      submittingFeedback: false
    }
  },
  computed: {
    formattedTime() {
      const date = new Date(this.message.timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  },
  methods: {
    // Phase 7: Handle rating change
    onRatingChange(value) {
      if (value >= 4) {
        // For high ratings, automatically submit without text
        this.submitFeedback();
      }
    },
    
    // Phase 7: Submit feedback
    async submitFeedback() {
      if (!this.feedbackRating) return;
      
      this.submittingFeedback = true;
      
      try {
        // Submit feedback to API
        const response = await axios.post('/api/chat/feedback', {
          message_id: this.message.id,
          rating: this.feedbackRating,
          feedback_text: this.feedbackText
        });
        
        // Update state
        this.feedbackSubmitted = true;
        
        // Emit event for parent components
        this.$emit('feedback-submitted', {
          messageId: this.message.id,
          rating: this.feedbackRating,
          feedbackText: this.feedbackText,
          feedbackId: response.data.id
        });
        
        // Update store if needed (you may need to add this action to your store)
        if (this.$store && this.$store.dispatch) {
          this.$store.dispatch('chat/updateMessageFeedback', {
            messageId: this.message.id,
            feedback: {
              rating: this.feedbackRating,
              feedbackText: this.feedbackText,
              feedbackId: response.data.id
            }
          });
        }
      } catch (error) {
        console.error('Error submitting feedback:', error);
        // Show error notification
        if (this.$store && this.$store.dispatch) {
          this.$store.dispatch('showNotification', {
            type: 'error',
            message: 'Failed to submit feedback. Please try again.'
          });
        }
      } finally {
        this.submittingFeedback = false;
      }
    }
  },
  // Phase 7: Set feedback from props if exists
  created() {
    if (this.existingFeedback) {
      this.feedbackRating = this.existingFeedback.rating;
      this.feedbackText = this.existingFeedback.feedback_text;
      this.feedbackSubmitted = true;
    }
  }
}
</script>

<style scoped>
.chat-message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.chat-message__avatar {
  margin-right: 12px;
  flex-shrink: 0;
}

.chat-message__content {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 10px 12px;
  max-width: 80%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.chat-message--user .chat-message__content {
  background-color: #e3f2fd;
}

.chat-message__name {
  font-weight: 500;
  font-size: 0.8rem;
  margin-bottom: 4px;
  color: rgba(0, 0, 0, 0.6);
}

.chat-message__text {
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-message__time {
  font-size: 0.7rem;
  color: rgba(0, 0, 0, 0.4);
  text-align: right;
  margin-top: 4px;
}

/* Phase 7: Feedback styles */
.chat-message__feedback {
  margin-top: 4px;
}

.chat-message__feedback-submitted {
  margin-top: 4px;
}

/* Dark theme adjustments */
.theme--dark .chat-message__content {
  background-color: #424242;
}

.theme--dark .chat-message--user .chat-message__content {
  background-color: #1976d2;
}

.theme--dark .chat-message__name {
  color: rgba(255, 255, 255, 0.7);
}

.theme--dark .chat-message__time {
  color: rgba(255, 255, 255, 0.5);
}
</style>
