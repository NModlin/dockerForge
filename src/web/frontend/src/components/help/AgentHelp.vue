<template>
  <div class="agent-help">
    <h2 class="headline mb-3">Agent System Guide</h2>
    
    <p class="mb-4">
      The DockerForge Agent System enables autonomous task execution and intelligent automation. 
      Agents are specialized AI components that can perform complex tasks, solve problems, and assist you with Docker management.
    </p>
    
    <v-tabs v-model="activeTab" background-color="primary" dark grow>
      <v-tab>Agent Types</v-tab>
      <v-tab>Using Agents</v-tab>
      <v-tab>Permissions</v-tab>
    </v-tabs>
    
    <v-tabs-items v-model="activeTab" class="mt-4">
      <!-- Agent Types Tab -->
      <v-tab-item>
        <v-card flat>
          <v-card-text>
            <v-row>
              <v-col v-for="agent in agents" :key="agent.id" cols="12" md="6">
                <v-card outlined class="mb-3" :class="`${agent.color} lighten-5`">
                  <v-card-title>
                    <v-avatar :color="agent.color" size="40" class="mr-3">
                      <v-icon dark>{{ agent.icon }}</v-icon>
                    </v-avatar>
                    {{ agent.name }}
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <p>{{ agent.description }}</p>
                    <h4 class="subtitle-1 font-weight-bold mt-3">Capabilities:</h4>
                    <ul class="pl-4">
                      <li v-for="(capability, i) in agent.capabilities" :key="i">
                        {{ capability }}
                      </li>
                    </ul>
                    <h4 class="subtitle-1 font-weight-bold mt-3">Example Task:</h4>
                    <v-card outlined class="pa-2 grey lighten-4 mt-1">
                      <code>{{ agent.example }}</code>
                    </v-card>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-tab-item>
      
      <!-- Using Agents Tab -->
      <v-tab-item>
        <v-card flat>
          <v-card-text>
            <h3 class="subtitle-1 font-weight-bold mb-3">How to Work with Agents</h3>
            
            <v-stepper vertical>
              <v-stepper-step step="1" complete>
                Request Agent Assistance
              </v-stepper-step>
              <v-stepper-content step="1">
                <p>There are multiple ways to engage agents:</p>
                <ul class="pl-4 mb-3">
                  <li>Ask the chat assistant a question or request a task</li>
                  <li>Use the <code>/agent</code> command followed by a task description</li>
                  <li>Click an "Agent Action" button in the interface</li>
                </ul>
                <p class="caption">The system will automatically route your request to the appropriate agent.</p>
              </v-stepper-content>
              
              <v-stepper-step step="2" complete>
                Task Planning
              </v-stepper-step>
              <v-stepper-content step="2">
                <p>When an agent receives a task, it will:</p>
                <ol class="pl-4 mb-3">
                  <li>Analyze the request and break it down into steps</li>
                  <li>Create a task plan with required actions</li>
                  <li>Display the proposed plan for your review</li>
                </ol>
                <v-alert
                  color="info"
                  text
                  dense
                  class="mb-3"
                >
                  You can modify the plan before execution if needed.
                </v-alert>
              </v-stepper-content>
              
              <v-stepper-step step="3" complete>
                Approval and Execution
              </v-stepper-step>
              <v-stepper-content step="3">
                <p>Actions that impact your system require approval:</p>
                <ul class="pl-4 mb-3">
                  <li>Review the proposed actions</li>
                  <li>Approve or reject each action</li>
                  <li>Monitor execution progress in real-time</li>
                </ul>
                <p>Some low-risk actions may be executed automatically based on your preference settings.</p>
              </v-stepper-content>
              
              <v-stepper-step step="4" complete>
                Results and Follow-up
              </v-stepper-step>
              <v-stepper-content step="4">
                <p>After execution:</p>
                <ul class="pl-4 mb-3">
                  <li>View a detailed report of completed actions</li>
                  <li>See results and any changes made</li>
                  <li>Get recommendations for next steps</li>
                  <li>Review logs for troubleshooting if needed</li>
                </ul>
              </v-stepper-content>
            </v-stepper>
            
            <v-card outlined class="mt-4 pa-3">
              <div class="d-flex align-center mb-2">
                <v-icon color="warning" class="mr-2">mdi-lightbulb-on</v-icon>
                <h3 class="subtitle-1 font-weight-bold">Pro Tip</h3>
              </div>
              <p>For complex tasks, try chaining agent capabilities. For example: "Scan my web container for vulnerabilities, then optimize its resource usage."</p>
            </v-card>
          </v-card-text>
        </v-card>
      </v-tab-item>
      
      <!-- Permissions Tab -->
      <v-tab-item>
        <v-card flat>
          <v-card-text>
            <h3 class="subtitle-1 font-weight-bold mb-3">Agent Permissions</h3>
            
            <p class="mb-4">Agent actions are categorized by their impact level. You can configure permissions for each level:</p>
            
            <v-simple-table>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th>Permission Level</th>
                    <th>Description</th>
                    <th>Examples</th>
                    <th>Default Setting</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="perm in permissions" :key="perm.level">
                    <td>
                      <v-chip :color="perm.color" small label>
                        {{ perm.level }}
                      </v-chip>
                    </td>
                    <td>{{ perm.description }}</td>
                    <td><span v-html="perm.examples"></span></td>
                    <td>{{ perm.default }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
            
            <v-alert
              color="info"
              text
              class="mt-4"
            >
              <p class="mb-0">You can configure agent permissions in the <strong>Settings</strong> page under the <strong>Agents & Automation</strong> tab.</p>
            </v-alert>
            
            <h3 class="subtitle-1 font-weight-bold mt-5 mb-3">Action History and Audit Log</h3>
            
            <p>All agent actions are recorded in an audit log for transparency and accountability. You can:</p>
            <ul class="pl-4">
              <li>View complete history of agent actions</li>
              <li>Filter by agent type, action type, or date range</li>
              <li>See detailed information about each action</li>
              <li>Roll back certain actions if needed</li>
            </ul>
            
            <p class="mt-3">Access the audit log from the settings page or by using the <code>/audit</code> command in chat.</p>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
export default {
  name: 'AgentHelp',
  props: {
    category: {
      type: String,
      default: 'agents'
    }
  },
  data() {
    return {
      activeTab: 0,
      agents: [
        {
          id: 'container',
          name: 'Container Agent',
          icon: 'mdi-docker',
          color: 'blue',
          description: 'Manages container operations and troubleshooting for your Docker environment.',
          capabilities: [
            'Container lifecycle management (start, stop, restart)',
            'Log analysis and error diagnosis',
            'Performance monitoring and optimization',
            'Configuration troubleshooting',
            'Automated issue resolution'
          ],
          example: 'Can you check why my web-app container is using high CPU and fix it?'
        },
        {
          id: 'security',
          name: 'Security Agent',
          icon: 'mdi-shield-check',
          color: 'deep-purple',
          description: 'Handles vulnerability scanning, security analysis, and remediation tasks.',
          capabilities: [
            'Container and image vulnerability scanning',
            'Security configuration analysis',
            'Automated vulnerability remediation',
            'CVE tracking and alerting',
            'Security best practices enforcement'
          ],
          example: 'Scan my postgres container for vulnerabilities and apply fixes'
        },
        {
          id: 'optimization',
          name: 'Optimization Agent',
          icon: 'mdi-speedometer',
          color: 'green',
          description: 'Monitors and improves resource utilization and performance of your Docker environment.',
          capabilities: [
            'Resource usage analysis and visualization',
            'Performance bottleneck identification',
            'Resource limit optimization',
            'Container placement recommendations',
            'Efficiency improvements for Docker configurations'
          ],
          example: 'Analyze my Docker environment and optimize resource allocation'
        },
        {
          id: 'documentation',
          name: 'Documentation Agent',
          icon: 'mdi-book-open-variant',
          color: 'amber',
          description: 'Provides contextual help, documentation, and learning resources.',
          capabilities: [
            'Context-aware documentation lookup',
            'Command explanation and examples',
            'Tutorial generation for common tasks',
            'Best practices recommendations',
            'DockerForge feature guides'
          ],
          example: 'Show me how to set up volume mounting for persistent data'
        }
      ],
      permissions: [
        {
          level: 'Read-Only',
          color: 'green',
          description: 'Actions that only read information without making any changes',
          examples: 'Viewing logs, running scans, generating reports',
          default: 'Auto-approve'
        },
        {
          level: 'Low Impact',
          color: 'blue',
          description: 'Actions with minimal risk that don\'t affect running containers',
          examples: 'Pulling images, creating volumes, updating labels',
          default: 'Ask for approval'
        },
        {
          level: 'Medium Impact',
          color: 'amber',
          description: 'Actions that affect container state but don\'t modify data',
          examples: 'Starting/stopping containers, changing resource limits',
          default: 'Ask for approval'
        },
        {
          level: 'High Impact',
          color: 'deep-orange',
          description: 'Actions that could affect data or critical services',
          examples: 'Removing containers, applying security patches, modifying volumes',
          default: 'Always ask for detailed approval'
        },
        {
          level: 'Critical',
          color: 'red',
          description: 'Actions with potential for significant impact',
          examples: 'Removing volumes with data, system-wide configuration changes',
          default: 'Always ask for detailed approval with warnings'
        }
      ]
    };
  }
};
</script>

<style scoped>
.agent-help {
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
