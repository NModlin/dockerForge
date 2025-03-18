<template>
  <div class="chat-help">
    <h2 class="headline mb-3">Chat Interface Guide</h2>
    
    <v-tabs v-model="activeTab" background-color="secondary" dark grow>
      <v-tab>Overview</v-tab>
      <v-tab>Features</v-tab>
      <v-tab>Tips & Tricks</v-tab>
    </v-tabs>
    
    <v-tabs-items v-model="activeTab" class="mt-4">
      <!-- Overview Tab -->
      <v-tab-item>
        <div class="pa-2">
          <v-img
            src="/img/help/chat-interface.png"
            alt="Chat Interface"
            contain
            height="250"
            class="mb-4 grey lighten-4"
          ></v-img>
          
          <h3 class="subtitle-1 font-weight-bold mb-2">About the Chat Interface</h3>
          <p>The DockerForge AI Chat Assistant provides intelligent, context-aware assistance for managing your Docker environment. It helps you:</p>
          
          <v-list dense>
            <v-list-item v-for="(item, i) in overviewItems" :key="i">
              <v-list-item-icon>
                <v-icon color="primary">{{ item.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ item.text }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          
          <v-alert
            color="info"
            text
            icon="mdi-information"
            class="mt-4"
          >
            The chat assistant is context-aware and adapts to the current page you're viewing, providing relevant information and actions.
          </v-alert>
        </div>
      </v-tab-item>
      
      <!-- Features Tab -->
      <v-tab-item>
        <div class="pa-2">
          <v-expansion-panels>
            <v-expansion-panel v-for="(feature, i) in features" :key="i">
              <v-expansion-panel-header>
                <div class="d-flex align-center">
                  <v-icon left color="primary">{{ feature.icon }}</v-icon>
                  <span>{{ feature.title }}</span>
                </div>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div v-html="feature.description"></div>
                <div v-if="feature.example" class="mt-2">
                  <v-card outlined class="pa-2 grey lighten-4">
                    <strong>Example:</strong> <code>{{ feature.example }}</code>
                  </v-card>
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-tab-item>
      
      <!-- Tips & Tricks Tab -->
      <v-tab-item>
        <div class="pa-2">
          <v-card
            v-for="(tip, i) in tips"
            :key="i"
            outlined
            class="mb-4"
          >
            <v-card-title class="subtitle-1">
              <v-icon left color="info">mdi-lightbulb-on</v-icon>
              {{ tip.title }}
            </v-card-title>
            <v-card-text>
              <div v-html="tip.content"></div>
              <div v-if="tip.example" class="mt-2 grey lighten-4 pa-2 rounded">
                <code>{{ tip.example }}</code>
              </div>
            </v-card-text>
          </v-card>
          
          <v-alert
            color="success"
            text
            dense
            icon="mdi-thumb-up"
            class="mt-4"
          >
            Remember to provide feedback to help improve the chat assistant's responses. Click the thumbs up/down icons on chat messages to let us know how we're doing!
          </v-alert>
        </div>
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
export default {
  name: 'ChatHelp',
  props: {
    category: {
      type: String,
      default: 'chat'
    }
  },
  data() {
    return {
      activeTab: 0,
      overviewItems: [
        { icon: 'mdi-docker', text: 'Troubleshoot container and image issues' },
        { icon: 'mdi-shield-check', text: 'Analyze and fix security vulnerabilities' },
        { icon: 'mdi-chart-bar', text: 'Optimize resource usage and performance' },
        { icon: 'mdi-code-json', text: 'Edit Docker configuration files' },
        { icon: 'mdi-robot', text: 'Perform automated tasks via the agent system' }
      ],
      features: [
        {
          icon: 'mdi-context-menu',
          title: 'Context-Aware Assistance',
          description: `
            <p>The chat assistant automatically detects your current context (e.g., viewing a container, security scan, etc.) 
            and provides relevant information and actions.</p>
            <p>You can also explicitly set context by using the "Chat about this" button in various sections of the application.</p>
          `
        },
        {
          icon: 'mdi-slash-forward',
          title: 'Chat Commands',
          description: `
            <p>Start a message with <code>/</code> to access special commands that trigger specific actions:</p>
            <ul>
              <li><code>/help</code> - Open this help center</li>
              <li><code>/scan [container name]</code> - Run a security scan</li>
              <li><code>/logs [container name]</code> - Show container logs</li>
              <li><code>/checkpoint</code> - Create a system checkpoint</li>
              <li><code>/agents</code> - List available automated agents</li>
            </ul>
            <p>Type <code>/</code> in the chat input to see all available commands.</p>
          `,
          example: '/scan web-server'
        },
        {
          icon: 'mdi-robot',
          title: 'Agent System',
          description: `
            <p>The agent system allows the chat assistant to perform complex tasks automatically by delegating to specialized agents:</p>
            <ul>
              <li><strong>Container Agent:</strong> Manages container operations and troubleshooting</li>
              <li><strong>Security Agent:</strong> Handles vulnerability scanning and remediation</li>
              <li><strong>Optimization Agent:</strong> Monitors and improves resource utilization</li>
              <li><strong>Documentation Agent:</strong> Provides contextual help and documentation</li>
            </ul>
            <p>Agents can work together to solve complex problems and can execute tasks with your approval.</p>
          `,
          example: 'Can you optimize the resources for my web-server container?'
        },
        {
          icon: 'mdi-history',
          title: 'Conversation Memory',
          description: `
            <p>The chat assistant remembers your previous conversations and uses this context to provide more relevant responses.</p>
            <p>Conversation history is preserved between sessions and across different pages of the application. You can:</p>
            <ul>
              <li>View past conversations in the chat sidebar</li>
              <li>Search through conversation history</li>
              <li>Continue previous conversations where you left off</li>
            </ul>
            <p>Your conversation data is stored securely and can be cleared at any time from the settings page.</p>
          `
        },
        {
          icon: 'mdi-tune',
          title: 'Customization',
          description: `
            <p>The chat assistant can be customized to match your preferences and workflow:</p>
            <ul>
              <li>Adjust verbosity level of responses</li>
              <li>Set default agent permissions</li>
              <li>Configure notification preferences</li>
              <li>Customize the chat sidebar appearance</li>
            </ul>
            <p>Access these settings by clicking the gear icon in the chat sidebar or in the main settings page.</p>
          `
        }
      ],
      tips: [
        {
          title: 'Be Specific in Your Questions',
          content: `
            <p>The more specific your questions, the more accurate the responses will be. Include relevant details like container names, image versions, or error messages.</p>
          `,
          example: 'Why is my nginx-proxy container exiting with code 137?'
        },
        {
          title: 'Use Natural Language',
          content: `
            <p>You can interact with the chat assistant using natural, conversational language. No need for specific syntax or commands (unless you want to use them).</p>
          `,
          example: 'Can you help me figure out why my PostgreSQL container keeps crashing?'
        },
        {
          title: 'Combine with Direct Actions',
          content: `
            <p>For the best experience, combine chat assistance with direct actions. For example, have the assistant diagnose an issue, then use the action buttons it provides to fix the problem.</p>
          `
        },
        {
          title: 'Multi-Turn Conversations',
          content: `
            <p>The assistant can handle complex, multi-turn conversations. Feel free to ask follow-up questions or provide additional context as needed.</p>
          `
        },
        {
          title: 'Keyboard Shortcuts',
          content: `
            <p>Use keyboard shortcuts to interact with the chat interface more efficiently:</p>
            <ul>
              <li><code>Ctrl+Space</code> - Toggle chat sidebar</li>
              <li><code>Ctrl+Enter</code> - Send message</li>
              <li><code>Esc</code> - Cancel current message</li>
              <li><code>↑</code> (Up Arrow) - Edit last message</li>
            </ul>
          `
        }
      ]
    };
  }
};
</script>

<style scoped>
.chat-help {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: var(--v-primary-base);
}

code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}
</style>
