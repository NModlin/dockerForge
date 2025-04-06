<template>
  <div class="guided-tour">
    <v-card v-if="!tourStarted && !tourComplete" outlined class="welcome-card">
      <v-card-title primary-title>
        <v-icon left large color="primary">mdi-compass</v-icon>
        Welcome to DockerForge!
      </v-card-title>
      <v-card-text>
        <p>Would you like to take a guided tour to explore key features and get started quickly?</p>
        <p class="caption">You can always restart the tour later from the help menu.</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="skipTour">Skip for now</v-btn>
        <v-btn color="primary" @click="startTour">Start Tour</v-btn>
      </v-card-actions>
    </v-card>

    <v-dialog v-model="tourStarted" persistent max-width="500">
      <v-card>
        <v-card-title class="primary white--text">
          <v-avatar size="36" color="primary darken-2" class="mr-3">
            <span class="white--text">{{ currentStep + 1 }}</span>
          </v-avatar>
          {{ currentStepData.title }}
          <v-spacer></v-spacer>
          <v-btn icon @click="endTour" class="white--text">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-img
          v-if="currentStepData.image"
          :src="currentStepData.image"
          height="180"
          class="grey lighten-4"
          contain
        ></v-img>

        <v-card-text>
          <p v-html="currentStepData.content"></p>

          <div v-if="currentStepData.hint" class="hint mt-2">
            <v-alert
              text
              dense
              color="info"
              icon="mdi-lightbulb-on"
            >
              {{ currentStepData.hint }}
            </v-alert>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-btn
            text
            @click="prevStep"
            :disabled="currentStep === 0"
          >
            <v-icon left>mdi-arrow-left</v-icon>
            Back
          </v-btn>

          <v-spacer></v-spacer>

          <div class="tour-progress">
            <v-progress-linear
              :value="(currentStep / (tourSteps.length - 1)) * 100"
              height="6"
              color="primary"
              class="mt-1"
            ></v-progress-linear>
            <span class="caption">{{ currentStep + 1 }} / {{ tourSteps.length }}</span>
          </div>

          <v-spacer></v-spacer>

          <v-btn
            v-if="currentStep < tourSteps.length - 1"
            color="primary"
            @click="nextStep"
          >
            Next
            <v-icon right>mdi-arrow-right</v-icon>
          </v-btn>

          <v-btn
            v-else
            color="success"
            @click="completeTour"
          >
            Finish
            <v-icon right>mdi-check</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="tourCompleteSnackbar"
      timeout="5000"
      color="success"
    >
      <span>Tour completed! You can restart it anytime from the help menu.</span>
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="tourCompleteSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
export default {
  name: 'GuidedTour',
  props: {
    autoStart: {
      type: Boolean,
      default: false
    },
    targetRoute: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      tourStarted: false,
      tourComplete: false,
      tourCompleteSnackbar: false,
      currentStep: 0,
      tourSteps: [
        {
          title: 'Welcome to DockerForge',
          content: `
            <p>DockerForge makes Docker container management simple and efficient with AI-powered assistance.</p>
            <p>This tour will guide you through the key features of the application.</p>
          `,
          image: '/img/help/tour/dashboard.png',
          targetElement: null
        },
        {
          title: 'Navigation Menu',
          content: `
            <p>The left sidebar provides access to all major sections of DockerForge:</p>
            <ul>
              <li><strong>Dashboard</strong>: Overview of your Docker environment</li>
              <li><strong>Containers</strong>: Manage and monitor containers</li>
              <li><strong>Images</strong>: Browse and manage Docker images</li>
              <li><strong>Security</strong>: Scan and remediate vulnerabilities</li>
              <li><strong>Resources</strong>: Monitor and optimize system resources</li>
            </ul>
          `,
          image: '/img/help/tour/navigation.png',
          targetElement: '.v-navigation-drawer',
          hint: 'Click on different menu items to navigate between sections.'
        },
        {
          title: 'AI Chat Assistant',
          content: `
            <p>The AI Chat Assistant is your intelligent companion for Docker management.</p>
            <p>Use it to:</p>
            <ul>
              <li>Ask questions about Docker in natural language</li>
              <li>Troubleshoot container issues automatically</li>
              <li>Get help with security vulnerabilities</li>
              <li>Perform complex tasks with simple commands</li>
            </ul>
          `,
          image: '/img/help/tour/chat.png',
          targetElement: '.chat-toggle-button',
          hint: 'Toggle the chat panel by clicking the chat icon in the top-right corner.'
        },
        {
          title: 'Container Management',
          content: `
            <p>The Containers section provides a comprehensive view of all your Docker containers.</p>
            <p>From here you can:</p>
            <ul>
              <li>Start, stop, and restart containers</li>
              <li>View container logs and stats</li>
              <li>Access container terminals</li>
              <li>Manage container configurations</li>
            </ul>
          `,
          image: '/img/help/tour/containers.png',
          route: '/containers',
          hint: 'Use quick action buttons to manage container state without navigating away.'
        },
        {
          title: 'Security Dashboard',
          content: `
            <p>The Security Dashboard helps you identify and fix vulnerabilities in your containers and images.</p>
            <p>Key features include:</p>
            <ul>
              <li>Automated vulnerability scanning</li>
              <li>Security risk assessment</li>
              <li>One-click vulnerability remediation</li>
              <li>Compliance checks and reports</li>
            </ul>
          `,
          image: '/img/help/tour/security.png',
          route: '/security',
          hint: 'Schedule regular scans to keep your environment secure.'
        },
        {
          title: 'Agent System',
          content: `
            <p>The Agent System enables intelligent automation of complex Docker tasks.</p>
            <p>Specialized agents can:</p>
            <ul>
              <li>Diagnose and fix container problems</li>
              <li>Optimize resource usage</li>
              <li>Remediate security vulnerabilities</li>
              <li>Provide contextual documentation</li>
            </ul>
            <p>Agents work autonomously but always under your control.</p>
          `,
          image: '/img/help/tour/agents.png',
          hint: 'Access agents through the chat interface or specialized agent panels.'
        },
        {
          title: 'Chat Commands',
          content: `
            <p>Power users can leverage chat commands for quick actions.</p>
            <p>Start a message with <code>/</code> followed by a command, for example:</p>
            <ul>
              <li><code>/logs container-name</code> - Show container logs</li>
              <li><code>/scan image-name</code> - Run a security scan</li>
              <li><code>/restart container-name</code> - Restart a container</li>
              <li><code>/help</code> - Access the help center</li>
            </ul>
          `,
          image: '/img/help/tour/commands.png',
          hint: 'Type / in the chat input to see available commands with autocomplete.'
        },
        {
          title: 'You\'re All Set!',
          content: `
            <p>Congratulations! You've completed the guided tour of DockerForge.</p>
            <p>Remember:</p>
            <ul>
              <li>The AI assistant is always available to help</li>
              <li>You can access documentation from the help menu</li>
              <li>Create checkpoints before making significant changes</li>
              <li>Run regular security scans to keep your environment safe</li>
            </ul>
            <p>Happy containerizing!</p>
          `,
          image: '/img/help/tour/complete.png'
        }
      ]
    };
  },
  computed: {
    currentStepData() {
      return this.tourSteps[this.currentStep] || this.tourSteps[0];
    }
  },
  mounted() {
    // If autoStart is true and user hasn't completed the tour before, start automatically
    if (this.autoStart && !this.hasCompletedTour()) {
      this.startTour();
    }

    // If there's a specific target route for this instance
    if (this.targetRoute && this.$route.path !== this.targetRoute) {
      this.tourStarted = false;
    }
  },
  methods: {
    startTour() {
      this.tourStarted = true;

      // Check if there's a saved tour progress
      const savedProgress = localStorage.getItem('guided-tour-progress');
      if (savedProgress) {
        try {
          const progress = JSON.parse(savedProgress);
          this.currentStep = progress.step || 0;
        } catch (e) {
          console.error('Failed to parse saved tour progress:', e);
          this.currentStep = 0;
        }
      } else {
        this.currentStep = 0;
      }

      this.highlightElement();
      this.$emit('tour-started');

      // Track tour start in analytics if available
      if (this.$analytics) {
        this.$analytics.trackEvent('tour', 'start');
      }
    },
    nextStep() {
      if (this.currentStep < this.tourSteps.length - 1) {
        this.currentStep++;
        this.handleRouteChange();
        this.highlightElement();
        this.saveTourProgress();

        // Track step progress in analytics if available
        if (this.$analytics) {
          this.$analytics.trackEvent('tour', 'next_step', {
            step: this.currentStep,
            stepTitle: this.currentStepData.title
          });
        }
      }
    },
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--;
        this.handleRouteChange();
        this.highlightElement();
        this.saveTourProgress();

        // Track step progress in analytics if available
        if (this.$analytics) {
          this.$analytics.trackEvent('tour', 'prev_step', {
            step: this.currentStep,
            stepTitle: this.currentStepData.title
          });
        }
      }
    },
    endTour() {
      this.tourStarted = false;
      this.removeHighlights();
      this.$emit('tour-ended');

      // Track tour end in analytics if available
      if (this.$analytics) {
        this.$analytics.trackEvent('tour', 'end', {
          step: this.currentStep,
          completed: false
        });
      }

      // Keep the progress in case user wants to resume later
    },
    completeTour() {
      this.tourStarted = false;
      this.tourComplete = true;
      this.tourCompleteSnackbar = true;
      this.removeHighlights();
      this.markTourCompleted();
      this.$emit('tour-completed');

      // Clear progress since tour is completed
      localStorage.removeItem('guided-tour-progress');

      // Track tour completion in analytics if available
      if (this.$analytics) {
        this.$analytics.trackEvent('tour', 'complete');
      }
    },
    skipTour() {
      this.tourComplete = true;
      this.$emit('tour-skipped');

      // Track tour skip in analytics if available
      if (this.$analytics) {
        this.$analytics.trackEvent('tour', 'skip');
      }
    },
    handleRouteChange() {
      // If the current step specifies a route, navigate to it
      const route = this.currentStepData.route;
      if (route && this.$route.path !== route) {
        this.$router.push(route);
      }
    },
    highlightElement() {
      this.removeHighlights();

      // If the current step targets an element, highlight it
      const targetSelector = this.currentStepData.targetElement;
      if (targetSelector) {
        setTimeout(() => {
          const element = document.querySelector(targetSelector);
          if (element) {
            element.classList.add('tour-highlight');
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 300); // Small delay to allow for route changes/renders
      }
    },
    removeHighlights() {
      const highlighted = document.querySelectorAll('.tour-highlight');
      highlighted.forEach(el => el.classList.remove('tour-highlight'));
    },
    hasCompletedTour() {
      return localStorage.getItem('guided-tour-completed') === 'true';
    },
    markTourCompleted() {
      localStorage.setItem('guided-tour-completed', 'true');
    },

    saveTourProgress() {
      // Save current tour progress to localStorage
      try {
        const progress = {
          step: this.currentStep,
          timestamp: new Date().toISOString()
        };
        localStorage.setItem('guided-tour-progress', JSON.stringify(progress));
      } catch (e) {
        console.error('Failed to save tour progress:', e);
      }
    },

    resumeTour() {
      // Resume tour from saved progress
      const savedProgress = localStorage.getItem('guided-tour-progress');
      if (savedProgress) {
        try {
          const progress = JSON.parse(savedProgress);
          this.currentStep = progress.step || 0;
          this.startTour();
          return true;
        } catch (e) {
          console.error('Failed to parse saved tour progress:', e);
        }
      }
      return false;
    }
  }
};
</script>

<style scoped>
.welcome-card {
  max-width: 500px;
  margin: 2rem auto;
}

.tour-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
  margin: 0 1rem;
}

:deep(.tour-highlight) {
  position: relative;
  z-index: 100;
  box-shadow: 0 0 0 4px var(--v-primary-base) !important;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--v-primary-base), 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(var(--v-primary-base), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--v-primary-base), 0);
  }
}

code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
