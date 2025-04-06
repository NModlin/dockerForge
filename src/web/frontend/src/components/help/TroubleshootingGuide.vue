<template>
  <div class="troubleshooting-guide">
    <h2 class="headline mb-3">Troubleshooting Guide</h2>
    
    <v-text-field
      v-model="searchQuery"
      label="Search troubleshooting topics"
      prepend-icon="mdi-magnify"
      clearable
      outlined
      dense
      class="mb-4"
      @input="filterIssues"
    ></v-text-field>
    
    <v-expansion-panels>
      <v-expansion-panel
        v-for="(issue, i) in filteredIssues"
        :key="i"
      >
        <v-expansion-panel-header>
          <div class="d-flex align-center">
            <v-icon
              :color="getIssueSeverityColor(issue.severity)"
              class="mr-2"
            >
              {{ getIssueSeverityIcon(issue.severity) }}
            </v-icon>
            <span>{{ issue.title }}</span>
          </div>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <div class="mb-3">
            <v-chip
              small
              :color="getIssueSeverityColor(issue.severity)"
              text-color="white"
              class="mr-1"
            >
              {{ issue.severity }}
            </v-chip>
            <v-chip
              small
              outlined
              class="mr-1"
            >
              {{ issue.category }}
            </v-chip>
          </div>
          
          <p class="font-weight-bold">Symptoms:</p>
          <ul>
            <li v-for="(symptom, j) in issue.symptoms" :key="j">
              {{ symptom }}
            </li>
          </ul>
          
          <p class="font-weight-bold mt-3">Possible Causes:</p>
          <ul>
            <li v-for="(cause, j) in issue.causes" :key="j">
              {{ cause }}
            </li>
          </ul>
          
          <p class="font-weight-bold mt-3">Solutions:</p>
          <v-timeline dense>
            <v-timeline-item
              v-for="(step, j) in issue.solutions"
              :key="j"
              small
            >
              <div v-html="step"></div>
            </v-timeline-item>
          </v-timeline>
          
          <div v-if="issue.notes" class="mt-3 pa-3 grey lighten-4 rounded">
            <p class="font-weight-bold">Notes:</p>
            <p v-html="issue.notes"></p>
          </div>
          
          <div v-if="issue.relatedDocs && issue.relatedDocs.length" class="mt-3">
            <p class="font-weight-bold">Related Documentation:</p>
            <ul>
              <li v-for="(doc, j) in issue.relatedDocs" :key="j">
                <a :href="doc.url" target="_blank">{{ doc.title }}</a>
              </li>
            </ul>
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
    
    <div v-if="filteredIssues.length === 0" class="text-center my-4">
      <v-icon size="64" color="grey lighten-1">mdi-help-circle-outline</v-icon>
      <p class="mt-2">No troubleshooting topics found for "{{ searchQuery }}"</p>
      <p class="subtitle-2 grey--text">Try different keywords or ask the AI Assistant for help</p>
      <v-btn
        color="primary"
        class="mt-3"
        @click="askAiAssistant"
      >
        <v-icon left>mdi-robot</v-icon>
        Ask AI Assistant
      </v-btn>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TroubleshootingGuide',
  data() {
    return {
      searchQuery: '',
      issues: [
        {
          title: 'Container fails to start',
          severity: 'Critical',
          category: 'Containers',
          symptoms: [
            'Container shows "Error" status',
            'Container exits immediately after starting',
            'Error message in container logs'
          ],
          causes: [
            'Incorrect container configuration',
            'Missing environment variables',
            'Port conflicts',
            'Resource constraints',
            'Application error inside container'
          ],
          solutions: [
            'Check container logs using <code>docker logs [container_name]</code> or the Logs tab in DockerForge',
            'Verify that all required environment variables are set correctly',
            'Check for port conflicts by running <code>docker port [container_name]</code> or using the Network tab',
            'Ensure the container has sufficient CPU and memory resources',
            'Try running the container with an interactive shell to debug: <code>docker run -it --entrypoint /bin/sh [image_name]</code>'
          ],
          notes: 'If the container is part of a Docker Compose setup, check the logs of other related containers as they might provide additional context.',
          relatedDocs: [
            { title: 'Container Lifecycle Management', url: '/help/user-guide/containers' },
            { title: 'Debugging Container Issues', url: '/help/user-guide/troubleshooting/containers' }
          ]
        },
        {
          title: 'Image pull fails',
          severity: 'High',
          category: 'Images',
          symptoms: [
            'Error message when pulling an image',
            '"Error response from daemon" message',
            'Authentication failure message'
          ],
          causes: [
            'Network connectivity issues',
            'Registry authentication problems',
            'Image does not exist or tag is incorrect',
            'Insufficient disk space'
          ],
          solutions: [
            'Verify your internet connection and ensure you can reach the Docker registry',
            'Check your registry credentials using <code>docker login</code>',
            'Verify that the image name and tag are correct',
            'Check available disk space with <code>df -h</code> and free up space if needed',
            'Try pulling a different tag or from a different registry'
          ],
          notes: 'For private registries, ensure that your credentials are correctly configured in DockerForge settings.',
          relatedDocs: [
            { title: 'Working with Docker Registries', url: '/help/user-guide/registries' },
            { title: 'Image Management', url: '/help/user-guide/images' }
          ]
        },
        {
          title: 'Volume mount issues',
          severity: 'Medium',
          category: 'Volumes',
          symptoms: [
            'Container cannot access files in mounted volume',
            'Permission denied errors in container logs',
            'Changes to files not persisting after container restart'
          ],
          causes: [
            'Incorrect volume path specification',
            'Permission issues on host directory',
            'SELinux or AppArmor restrictions',
            'Bind mount instead of volume being used unintentionally'
          ],
          solutions: [
            'Verify the volume mount path in the container configuration',
            'Check permissions on the host directory: <code>ls -la /path/to/volume</code>',
            'For SELinux systems, try adding <code>:z</code> or <code>:Z</code> to the volume mount',
            'Use Docker volumes instead of bind mounts for better portability',
            'Inspect the volume using <code>docker volume inspect [volume_name]</code>'
          ],
          notes: 'Remember that Docker volumes are the preferred mechanism for persisting data generated by and used by Docker containers.',
          relatedDocs: [
            { title: 'Managing Docker Volumes', url: '/help/user-guide/volumes' },
            { title: 'Data Persistence in Docker', url: '/help/user-guide/data-management' }
          ]
        },
        {
          title: 'Network connectivity issues',
          severity: 'High',
          category: 'Networks',
          symptoms: [
            'Containers cannot communicate with each other',
            'Container cannot access external network',
            'DNS resolution fails inside container'
          ],
          causes: [
            'Containers on different networks',
            'Firewall blocking container traffic',
            'Docker network driver issues',
            'DNS configuration problems'
          ],
          solutions: [
            'Verify that containers are on the same network using <code>docker network inspect [network_name]</code>',
            'Check firewall rules that might be blocking container traffic',
            'Try using the host network mode for troubleshooting: <code>--network=host</code>',
            'Check DNS settings in the Docker daemon configuration',
            'Use <code>docker exec [container_name] ping [target]</code> to test connectivity'
          ],
          notes: 'Docker creates three networks automatically: bridge, host, and none. Make sure you understand the differences between these network types.',
          relatedDocs: [
            { title: 'Docker Networking Guide', url: '/help/user-guide/networks' },
            { title: 'Container Communication', url: '/help/user-guide/container-communication' }
          ]
        },
        {
          title: 'Docker daemon not responding',
          severity: 'Critical',
          category: 'System',
          symptoms: [
            'DockerForge cannot connect to Docker daemon',
            'Error message: "Cannot connect to the Docker daemon"',
            'All Docker commands fail'
          ],
          causes: [
            'Docker service not running',
            'Permission issues with Docker socket',
            'Docker daemon crashed due to resource exhaustion',
            'Socket path configuration incorrect'
          ],
          solutions: [
            'Check if Docker service is running: <code>systemctl status docker</code>',
            'Restart Docker service: <code>systemctl restart docker</code>',
            'Verify permissions on Docker socket: <code>ls -la /var/run/docker.sock</code>',
            'Check Docker daemon logs: <code>journalctl -u docker</code>',
            'Ensure your user is in the docker group: <code>usermod -aG docker $USER</code>'
          ],
          notes: 'If Docker daemon crashes frequently, it might indicate underlying system issues like insufficient resources or disk space.',
          relatedDocs: [
            { title: 'Docker Daemon Configuration', url: '/help/user-guide/daemon-configuration' },
            { title: 'System Requirements', url: '/help/user-guide/system-requirements' }
          ]
        },
        {
          title: 'High CPU or memory usage',
          severity: 'Medium',
          category: 'Performance',
          symptoms: [
            'System becomes slow or unresponsive',
            'Docker containers using excessive CPU or memory',
            'Container performance degradation over time'
          ],
          causes: [
            'No resource limits set on containers',
            'Memory leaks in containerized applications',
            'Too many containers running simultaneously',
            'Inefficient container configuration'
          ],
          solutions: [
            'Set resource limits for containers using <code>--memory</code> and <code>--cpu</code> flags',
            'Monitor container resource usage with <code>docker stats</code> or the Monitoring dashboard',
            'Identify and fix memory leaks in containerized applications',
            'Consider using Docker Compose to manage resource allocation across services',
            'Optimize container images to reduce resource usage'
          ],
          notes: 'Regular monitoring of container resource usage can help identify potential issues before they become critical.',
          relatedDocs: [
            { title: 'Container Resource Management', url: '/help/user-guide/resource-management' },
            { title: 'Performance Optimization', url: '/help/user-guide/performance' }
          ]
        },
        {
          title: 'Docker Compose service dependencies issues',
          severity: 'Medium',
          category: 'Compose',
          symptoms: [
            'Services start in wrong order',
            'Services fail because dependent services are not ready',
            'Timeout errors when starting compose stack'
          ],
          causes: [
            'Missing or incorrect depends_on configuration',
            'No health checks defined for services',
            'Services take too long to initialize'
          ],
          solutions: [
            'Use <code>depends_on</code> to specify service dependencies',
            'Implement health checks for services to ensure they are fully initialized',
            'Consider using wait scripts or tools like wait-for-it.sh in your entrypoint',
            'Increase timeout values in Docker Compose configuration',
            'Use the <code>restart: on-failure</code> policy for services that might fail initially'
          ],
          notes: 'Remember that <code>depends_on</code> only waits for services to start, not for them to be "ready". Health checks can help ensure services are fully initialized.',
          relatedDocs: [
            { title: 'Docker Compose Dependencies', url: '/help/user-guide/compose-dependencies' },
            { title: 'Service Health Checks', url: '/help/user-guide/health-checks' }
          ]
        },
        {
          title: 'Security scanning shows vulnerabilities',
          severity: 'High',
          category: 'Security',
          symptoms: [
            'Security scan reports vulnerabilities',
            'Critical or high severity CVEs detected',
            'Compliance checks failing'
          ],
          causes: [
            'Outdated base images',
            'Vulnerable packages installed in container',
            'Insecure container configuration',
            'Using deprecated or unsupported software'
          ],
          solutions: [
            'Update base images to latest versions with <code>docker pull</code>',
            'Rebuild images with updated packages',
            'Use minimal base images like Alpine to reduce attack surface',
            'Implement security best practices in Dockerfiles',
            'Use DockerForge\'s remediation recommendations to fix vulnerabilities'
          ],
          notes: 'Regular security scanning and updates are essential for maintaining a secure container environment. Consider implementing automated scanning in your CI/CD pipeline.',
          relatedDocs: [
            { title: 'Container Security Best Practices', url: '/help/user-guide/security-best-practices' },
            { title: 'Vulnerability Management', url: '/help/user-guide/vulnerability-management' }
          ]
        }
      ],
      filteredIssues: []
    };
  },
  created() {
    // Initialize filtered issues with all issues
    this.filteredIssues = [...this.issues];
  },
  methods: {
    filterIssues() {
      if (!this.searchQuery.trim()) {
        this.filteredIssues = [...this.issues];
        return;
      }
      
      const query = this.searchQuery.toLowerCase();
      this.filteredIssues = this.issues.filter(issue => {
        return (
          issue.title.toLowerCase().includes(query) ||
          issue.category.toLowerCase().includes(query) ||
          issue.symptoms.some(s => s.toLowerCase().includes(query)) ||
          issue.causes.some(c => c.toLowerCase().includes(query)) ||
          issue.solutions.some(s => s.toLowerCase().includes(query))
        );
      });
    },
    
    getIssueSeverityColor(severity) {
      switch (severity.toLowerCase()) {
        case 'critical': return 'error';
        case 'high': return 'deep-orange';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'grey';
      }
    },
    
    getIssueSeverityIcon(severity) {
      switch (severity.toLowerCase()) {
        case 'critical': return 'mdi-alert-circle';
        case 'high': return 'mdi-alert';
        case 'medium': return 'mdi-alert-outline';
        case 'low': return 'mdi-information';
        default: return 'mdi-help-circle';
      }
    },
    
    askAiAssistant() {
      // Emit event to open AI Assistant with the current search query
      this.$root.$emit('open-ai-assistant', {
        query: `I'm having trouble with ${this.searchQuery}. Can you help me troubleshoot?`
      });
      
      // Alternatively, navigate to chat with pre-filled query
      this.$router.push({
        path: '/chat',
        query: { q: `Troubleshooting: ${this.searchQuery}` }
      });
    }
  }
};
</script>

<style scoped>
.troubleshooting-guide {
  max-width: 800px;
  margin: 0 auto;
}

:deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
