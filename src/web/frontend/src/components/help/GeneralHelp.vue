<template>
  <div class="general-help">
    <h2 class="headline mb-3">Welcome to DockerForge</h2>
    
    <v-expansion-panels>
      <v-expansion-panel v-for="(item, i) in helpItems" :key="i">
        <v-expansion-panel-header>
          <div class="d-flex align-center">
            <v-icon left color="primary">{{ item.icon }}</v-icon>
            <span>{{ item.title }}</span>
          </div>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <div v-html="item.content"></div>
          <v-btn
            v-if="item.link"
            text
            color="primary"
            class="mt-2"
            @click="openDocumentation(item.link)"
          >
            <v-icon left>mdi-open-in-new</v-icon>
            Read More
          </v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-card outlined class="mt-5 pa-4">
      <div class="d-flex align-center mb-2">
        <v-icon color="info" large class="mr-2">mdi-lightbulb-on</v-icon>
        <h3 class="subtitle-1 font-weight-bold">Pro Tip</h3>
      </div>
      <p>You can access this help center anytime by clicking the help icon in the top navigation bar or by typing <code>/help</code> in the chat interface.</p>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'GeneralHelp',
  props: {
    category: {
      type: String,
      default: 'general'
    }
  },
  data() {
    return {
      helpItems: [
        {
          title: 'About DockerForge',
          icon: 'mdi-information-outline',
          content: `
            <p>DockerForge is a comprehensive Docker management platform designed to simplify container operations,
            enhance security, and optimize your Docker workflows.</p>
            <p>Key features include:</p>
            <ul>
              <li>Container and image management</li>
              <li>Security scanning and vulnerability remediation</li>
              <li>Resource monitoring and optimization</li>
              <li>AI-powered assistant and automation</li>
              <li>Backup and checkpoint management</li>
            </ul>
          `,
          link: '/documentation/overview'
        },
        {
          title: 'Getting Started',
          icon: 'mdi-rocket-launch',
          content: `
            <p>New to DockerForge? Here's how to get started:</p>
            <ol>
              <li>Explore the dashboard to view your containers and images</li>
              <li>Use the AI chat assistant to ask questions or get help</li>
              <li>Check the security dashboard to identify vulnerabilities</li>
              <li>Set up monitoring to track resource usage</li>
              <li>Create a checkpoint before making significant changes</li>
            </ol>
            <p>The guided tour will walk you through these features step by step.</p>
          `,
          link: '/documentation/getting-started'
        },
        {
          title: 'Interface Overview',
          icon: 'mdi-view-dashboard',
          content: `
            <p>The DockerForge interface is organized into several key areas:</p>
            <ul>
              <li><strong>Dashboard:</strong> Overview of your Docker environment</li>
              <li><strong>Containers:</strong> Manage and monitor containers</li>
              <li><strong>Images:</strong> Browse and manage Docker images</li>
              <li><strong>Security:</strong> Scan and remediate vulnerabilities</li>
              <li><strong>Resources:</strong> Monitor and optimize system resources</li>
              <li><strong>Settings:</strong> Configure DockerForge preferences</li>
              <li><strong>Chat Assistant:</strong> Get AI-powered help and automation</li>
            </ul>
            <p>Navigate between these sections using the main menu on the left.</p>
          `,
          link: '/documentation/interface'
        },
        {
          title: 'Where to Find Help',
          icon: 'mdi-help-circle',
          content: `
            <p>If you need assistance, DockerForge offers several resources:</p>
            <ul>
              <li><strong>AI Chat Assistant:</strong> Ask questions in natural language</li>
              <li><strong>Contextual Help:</strong> Click the help icon in any section</li>
              <li><strong>Documentation:</strong> Access comprehensive guides</li>
              <li><strong>Tooltips:</strong> Hover over elements for quick information</li>
              <li><strong>Command Reference:</strong> View available chat commands</li>
            </ul>
            <p>You can also start the guided tour anytime from the help menu.</p>
          `,
          link: '/documentation/support'
        }
      ]
    };
  },
  methods: {
    openDocumentation(link) {
      // This would normally navigate to the documentation page
      // For now, we'll just emit an event that could be handled by a parent
      this.$emit('open-documentation', link);
      
      // Alternatively, this could use the router if these are internal routes
      // this.$router.push(link);
    }
  }
};
</script>

<style scoped>
.general-help {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: var(--v-primary-base);
  margin-bottom: 1rem;
}

.v-expansion-panels {
  margin-bottom: 1rem;
}

code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}
</style>
