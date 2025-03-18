<template>
  <div class="command-reference">
    <h2 class="headline mb-3">Command Reference</h2>
    
    <v-text-field
      v-model="search"
      label="Search Commands"
      prepend-icon="mdi-magnify"
      clearable
      outlined
      dense
      class="mb-4"
    ></v-text-field>
    
    <v-row>
      <v-col cols="12" md="3">
        <v-list dense nav>
          <v-list-item
            v-for="category in categories"
            :key="category.id"
            @click="currentCategory = category.id"
            :class="{ 'primary--text': currentCategory === category.id }"
          >
            <v-list-item-icon>
              <v-icon :color="currentCategory === category.id ? 'primary' : ''">
                {{ category.icon }}
              </v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ category.name }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
      
      <v-col cols="12" md="9">
        <v-card outlined class="command-list">
          <v-list two-line>
            <template v-for="(command, index) in filteredCommands" :key="command.name">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title class="d-flex align-center">
                    <code class="command-code">{{ command.syntax }}</code>
                    <v-chip
                      x-small
                      :color="getPermissionColor(command.permissionLevel)"
                      class="ml-2"
                      label
                    >
                      {{ command.permissionLevel }}
                    </v-chip>
                  </v-list-item-title>
                  <v-list-item-subtitle class="mt-1">
                    {{ command.description }}
                  </v-list-item-subtitle>
                  
                  <div v-if="command.options && command.options.length" class="mt-2 options-list">
                    <div class="caption grey--text mb-1">Options:</div>
                    <ul class="pl-4 mb-0">
                      <li v-for="(option, i) in command.options" :key="i" class="caption">
                        <code>{{ option.name }}</code> - {{ option.description }}
                      </li>
                    </ul>
                  </div>
                  
                  <div v-if="command.example" class="mt-2">
                    <div class="caption grey--text">Example:</div>
                    <code class="example-code">{{ command.example }}</code>
                  </div>
                </v-list-item-content>
                
                <v-list-item-action>
                  <v-btn
                    icon
                    small
                    @click="copyToClipboard(command.syntax)"
                    title="Copy command"
                  >
                    <v-icon small>mdi-content-copy</v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
              
              <v-divider
                v-if="index < filteredCommands.length - 1"
                :key="`divider-${index}`"
              ></v-divider>
            </template>
            
            <v-list-item v-if="filteredCommands.length === 0">
              <v-list-item-content>
                <v-list-item-title class="text-center">
                  No commands match your search
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
    
    <v-alert
      color="info"
      text
      class="mt-4"
      icon="mdi-information"
    >
      <p class="mb-1">Commands can be used in the chat input by typing <code>/</code> followed by the command name.</p>
      <p class="mb-0">Type <code>/</code> in the chat input to see a list of available commands with autocomplete suggestions.</p>
    </v-alert>
  </div>
</template>

<script>
export default {
  name: 'CommandReference',
  props: {
    category: {
      type: String,
      default: 'commands'
    }
  },
  data() {
    return {
      search: '',
      currentCategory: 'all',
      categories: [
        { id: 'all', name: 'All Commands', icon: 'mdi-view-list' },
        { id: 'general', name: 'General', icon: 'mdi-home' },
        { id: 'container', name: 'Containers', icon: 'mdi-docker' },
        { id: 'security', name: 'Security', icon: 'mdi-shield-check' },
        { id: 'agent', name: 'Agents', icon: 'mdi-robot' },
        { id: 'system', name: 'System', icon: 'mdi-cog' }
      ],
      commands: [
        {
          name: 'help',
          syntax: '/help [topic]',
          description: 'Display help information about DockerForge or a specific topic',
          example: '/help security',
          category: 'general',
          permissionLevel: 'Read-Only',
          options: [
            { name: 'topic', description: 'Optional topic to get help on (e.g., containers, security, agents)' }
          ]
        },
        {
          name: 'logs',
          syntax: '/logs <container> [options]',
          description: 'Display logs for a specified container',
          example: '/logs web-server --tail 50',
          category: 'container',
          permissionLevel: 'Read-Only',
          options: [
            { name: '--tail <n>', description: 'Show only the last n lines' },
            { name: '--since <time>', description: 'Show logs since timestamp (e.g., 2h, 10m)' },
            { name: '--follow', description: 'Follow log output in real-time' }
          ]
        },
        {
          name: 'scan',
          syntax: '/scan <target> [type]',
          description: 'Run a security scan on a container, image, or the entire environment',
          example: '/scan nginx vulnerability',
          category: 'security',
          permissionLevel: 'Read-Only',
          options: [
            { name: 'target', description: 'Container name, image name, or "all"' },
            { name: 'type', description: 'Scan type: vulnerability, configuration, or compliance' }
          ]
        },
        {
          name: 'fix',
          syntax: '/fix <vulnerability-id>',
          description: 'Apply recommended fix for a specific vulnerability',
          example: '/fix CVE-2022-27664',
          category: 'security',
          permissionLevel: 'High Impact',
          options: []
        },
        {
          name: 'restart',
          syntax: '/restart <container>',
          description: 'Restart a specific container',
          example: '/restart postgres',
          category: 'container',
          permissionLevel: 'Medium Impact',
          options: []
        },
        {
          name: 'checkpoint',
          syntax: '/checkpoint [name]',
          description: 'Create a system checkpoint with an optional name',
          example: '/checkpoint before-upgrade',
          category: 'system',
          permissionLevel: 'Low Impact',
          options: [
            { name: 'name', description: 'Optional checkpoint name (defaults to timestamp)' }
          ]
        },
        {
          name: 'restore',
          syntax: '/restore <checkpoint-id>',
          description: 'Restore system to a previous checkpoint state',
          example: '/restore checkpoint-20250315-143022',
          category: 'system',
          permissionLevel: 'Critical',
          options: []
        },
        {
          name: 'agent',
          syntax: '/agent <agent-type> <task>',
          description: 'Explicitly assign a task to a specific agent',
          example: '/agent container diagnose web-server high-cpu',
          category: 'agent',
          permissionLevel: 'Medium Impact',
          options: [
            { name: 'agent-type', description: 'Type of agent: container, security, optimization, documentation' },
            { name: 'task', description: 'Task description for the agent to perform' }
          ]
        },
        {
          name: 'agents',
          syntax: '/agents [status]',
          description: 'List all available agents and their status',
          example: '/agents',
          category: 'agent',
          permissionLevel: 'Read-Only',
          options: [
            { name: 'status', description: 'Optional filter: active, idle, or all' }
          ]
        },
        {
          name: 'exec',
          syntax: '/exec <container> <command>',
          description: 'Execute a command in a running container',
          example: '/exec web-server ls -la /app',
          category: 'container',
          permissionLevel: 'High Impact',
          options: []
        },
        {
          name: 'stats',
          syntax: '/stats [container]',
          description: 'Display resource usage statistics for containers',
          example: '/stats web-server',
          category: 'container',
          permissionLevel: 'Read-Only',
          options: [
            { name: 'container', description: 'Optional container name (defaults to all containers)' }
          ]
        },
        {
          name: 'inspect',
          syntax: '/inspect <resource-type> <name>',
          description: 'Show detailed information about a Docker resource',
          example: '/inspect container web-server',
          category: 'general',
          permissionLevel: 'Read-Only',
          options: [
            { name: 'resource-type', description: 'Type of resource: container, image, volume, network' },
            { name: 'name', description: 'Name or ID of the resource to inspect' }
          ]
        },
        {
          name: 'audit',
          syntax: '/audit [options]',
          description: 'Show system audit log of actions and changes',
          example: '/audit --since 2d --type agent',
          category: 'system',
          permissionLevel: 'Read-Only',
          options: [
            { name: '--since <time>', description: 'Show entries since timestamp (e.g., 2h, 10m, 3d)' },
            { name: '--type <type>', description: 'Filter by entry type: agent, user, system' },
            { name: '--limit <n>', description: 'Limit to n entries (default: 50)' }
          ]
        },
        {
          name: 'optimize',
          syntax: '/optimize <container>',
          description: 'Analyze and suggest optimizations for container resource usage',
          example: '/optimize web-server',
          category: 'agent',
          permissionLevel: 'Medium Impact',
          options: []
        }
      ]
    };
  },
  computed: {
    filteredCommands() {
      let commands = this.commands;
      
      // Filter by category
      if (this.currentCategory !== 'all') {
        commands = commands.filter(cmd => cmd.category === this.currentCategory);
      }
      
      // Filter by search term
      if (this.search.trim() !== '') {
        const searchTerm = this.search.toLowerCase();
        commands = commands.filter(cmd => 
          cmd.name.toLowerCase().includes(searchTerm) || 
          cmd.description.toLowerCase().includes(searchTerm) ||
          cmd.syntax.toLowerCase().includes(searchTerm)
        );
      }
      
      return commands;
    }
  },
  methods: {
    getPermissionColor(level) {
      const colors = {
        'Read-Only': 'green',
        'Low Impact': 'blue',
        'Medium Impact': 'amber',
        'High Impact': 'deep-orange',
        'Critical': 'red'
      };
      
      return colors[level] || 'grey';
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        // We could show a success message here
        this.$emit('copied', text);
      });
    }
  }
};
</script>

<style scoped>
.command-reference {
  max-width: 900px;
  margin: 0 auto;
}

h2 {
  color: var(--v-primary-base);
}

.command-list {
  max-height: 600px;
  overflow-y: auto;
}

.command-code {
  font-family: monospace;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 3px 6px;
  border-radius: 3px;
  font-weight: bold;
}

.example-code {
  background-color: rgba(0, 0, 0, 0.03);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.85rem;
  display: block;
  margin-top: 4px;
}

code {
  font-family: monospace;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}

.options-list ul {
  margin-top: 4px;
}
</style>
