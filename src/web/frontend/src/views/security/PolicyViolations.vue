<template>
  <div class="policy-violations">
    <div class="d-flex align-center mb-4">
      <h1 class="text-h4">Policy Violations</h1>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :to="{ name: 'SecurityPolicies' }"
      >
        <v-icon left>mdi-shield-lock</v-icon>
        Manage Policies
      </v-btn>
    </div>

    <!-- Loading State -->
    <div v-if="policyLoading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <!-- Error State -->
    <v-alert v-else-if="policyError" type="error" class="mb-4">
      {{ policyError }}
    </v-alert>

    <!-- Violations Dashboard -->
    <template v-else>
      <!-- Violations Summary -->
      <v-row>
        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="error">mdi-alert-circle</v-icon>
              Critical
            </v-card-title>
            <v-card-text class="text-center">
              <div class="text-h3 red--text">{{ criticalViolations.length }}</div>
              <div class="text-subtitle-1">Violations</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="warning">mdi-alert</v-icon>
              High
            </v-card-title>
            <v-card-text class="text-center">
              <div class="text-h3 orange--text">{{ highViolations.length }}</div>
              <div class="text-subtitle-1">Violations</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="info">mdi-information</v-icon>
              Medium/Low
            </v-card-title>
            <v-card-text class="text-center">
              <div class="text-h3 blue--text">{{ mediumViolations.length + lowViolations.length }}</div>
              <div class="text-subtitle-1">Violations</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card class="mb-4">
            <v-card-title class="headline">
              <v-icon left color="success">mdi-check-circle</v-icon>
              Resolved
            </v-card-title>
            <v-card-text class="text-center">
              <div class="text-h3 green--text">{{ resolvedViolations.length }}</div>
              <div class="text-subtitle-1">Violations</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Violations List -->
      <h2 class="text-h5 mb-3">Active Violations</h2>
      <v-card v-if="unresolvedViolations.length > 0" class="mb-4">
        <v-data-table
          :headers="violationHeaders"
          :items="unresolvedViolations"
          :items-per-page="10"
          class="elevation-1"
        >
          <!-- Resource Column -->
          <template v-slot:item.resource="{ item }">
            <router-link
              :to="getResourceLink(item)"
              class="text-decoration-none"
            >
              {{ item.resource_name }}
            </router-link>
            <v-chip
              x-small
              class="ml-2"
              :color="getResourceTypeColor(item.resource_type)"
            >
              {{ item.resource_type }}
            </v-chip>
          </template>

          <!-- Policy Column -->
          <template v-slot:item.policy="{ item }">
            <router-link
              :to="{ name: 'PolicyDetail', params: { id: item.policy_id } }"
              class="text-decoration-none"
            >
              {{ item.policy_name }}
            </router-link>
          </template>

          <!-- Severity Column -->
          <template v-slot:item.severity="{ item }">
            <v-chip
              :color="getSeverityColor(item.severity)"
              text-color="white"
              small
            >
              {{ item.severity }}
            </v-chip>
          </template>

          <!-- Date Column -->
          <template v-slot:item.created_at="{ item }">
            {{ formatDate(item.created_at) }}
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              @click="openViolationDetails(item)"
              title="View Details"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="openResolveDialog(item)"
              title="Resolve Violation"
              color="success"
            >
              <v-icon small>mdi-check</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="resolveWithAI(item)"
              title="Resolve with AI"
              color="primary"
            >
              <v-icon small>mdi-robot</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
      <v-card v-else class="pa-4 text-center mb-4">
        <v-icon color="success" large class="mb-2">mdi-check-circle</v-icon>
        <p class="text-h6">No active policy violations</p>
        <p class="text-subtitle-1">All policy checks are passing</p>
      </v-card>

      <!-- Resolved Violations -->
      <h2 class="text-h5 mb-3">Resolved Violations</h2>
      <v-card v-if="resolvedViolations.length > 0">
        <v-data-table
          :headers="resolvedHeaders"
          :items="resolvedViolations"
          :items-per-page="10"
          class="elevation-1"
        >
          <!-- Resource Column -->
          <template v-slot:item.resource="{ item }">
            <router-link
              :to="getResourceLink(item)"
              class="text-decoration-none"
            >
              {{ item.resource_name }}
            </router-link>
            <v-chip
              x-small
              class="ml-2"
              :color="getResourceTypeColor(item.resource_type)"
            >
              {{ item.resource_type }}
            </v-chip>
          </template>

          <!-- Policy Column -->
          <template v-slot:item.policy="{ item }">
            <router-link
              :to="{ name: 'PolicyDetail', params: { id: item.policy_id } }"
              class="text-decoration-none"
            >
              {{ item.policy_name }}
            </router-link>
          </template>

          <!-- Severity Column -->
          <template v-slot:item.severity="{ item }">
            <v-chip
              :color="getSeverityColor(item.severity)"
              text-color="white"
              small
            >
              {{ item.severity }}
            </v-chip>
          </template>

          <!-- Resolved Date Column -->
          <template v-slot:item.resolved_at="{ item }">
            {{ formatDate(item.resolved_at) }}
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              @click="openViolationDetails(item)"
              title="View Details"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
      <v-card v-else class="pa-4 text-center">
        <p class="text-subtitle-1">No resolved violations</p>
      </v-card>
    </template>

    <!-- Violation Details Dialog -->
    <v-dialog
      v-model="detailsDialog"
      max-width="700px"
    >
      <v-card v-if="selectedViolation">
        <v-card-title class="headline d-flex align-center">
          <div>
            Policy Violation
            <v-chip
              :color="getSeverityColor(selectedViolation.severity)"
              text-color="white"
              small
              class="ml-2"
            >
              {{ selectedViolation.severity }}
            </v-chip>
          </div>
          <v-spacer></v-spacer>
          <v-btn
            icon
            @click="detailsDialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <strong>Resource:</strong> {{ selectedViolation.resource_name }}
              <v-chip
                x-small
                class="ml-2"
                :color="getResourceTypeColor(selectedViolation.resource_type)"
              >
                {{ selectedViolation.resource_type }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="6">
              <strong>Policy:</strong> {{ selectedViolation.policy_name }}
            </v-col>
            <v-col cols="12">
              <strong>Description:</strong> {{ selectedViolation.description }}
            </v-col>
            <v-col cols="12" md="6">
              <strong>Created:</strong> {{ formatDate(selectedViolation.created_at) }}
            </v-col>
            <v-col cols="12" md="6" v-if="selectedViolation.resolved">
              <strong>Resolved:</strong> {{ formatDate(selectedViolation.resolved_at) }}
            </v-col>
            <v-col cols="12" v-if="selectedViolation.resolved && selectedViolation.resolution_notes">
              <strong>Resolution Notes:</strong> {{ selectedViolation.resolution_notes }}
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <h3 class="text-subtitle-1 mb-2">Rule Information</h3>
          <v-row>
            <v-col cols="12" md="6">
              <strong>Rule:</strong> {{ selectedViolation.rule_name }}
            </v-col>
            <v-col cols="12" md="6">
              <strong>Action Taken:</strong>
              <v-chip
                :color="getActionColor(selectedViolation.action_taken)"
                text-color="white"
                small
                class="ml-2"
              >
                {{ selectedViolation.action_taken }}
              </v-chip>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <div class="d-flex mt-2" v-if="!selectedViolation.resolved">
            <v-btn
              color="success"
              class="mr-2"
              @click="openResolveDialog(selectedViolation)"
            >
              <v-icon left>mdi-check</v-icon>
              Resolve Violation
            </v-btn>
            <v-btn
              color="primary"
              @click="resolveWithAI(selectedViolation)"
            >
              <v-icon left>mdi-robot</v-icon>
              Resolve with AI
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Resolve Violation Dialog -->
    <v-dialog
      v-model="resolveDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Resolve Violation
        </v-card-title>
        <v-card-text>
          <p>Please provide resolution notes for this violation:</p>
          <v-textarea
            v-model="resolutionNotes"
            label="Resolution Notes"
            rows="4"
            counter
            hint="Describe how this violation was resolved"
            persistent-hint
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="resolveDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success"
            :disabled="!resolutionNotes || resolveSubmitting"
            @click="resolveViolation"
          >
            <v-progress-circular
              v-if="resolveSubmitting"
              indeterminate
              size="20"
              width="2"
              class="mr-2"
            ></v-progress-circular>
            Resolve
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import axios from 'axios';

export default {
  name: 'PolicyViolations',
  data() {
    return {
      detailsDialog: false,
      resolveDialog: false,
      selectedViolation: null,
      resolutionNotes: '',
      resolveSubmitting: false,
      violationHeaders: [
        { text: 'Resource', value: 'resource', sortable: true },
        { text: 'Policy', value: 'policy', sortable: true },
        { text: 'Description', value: 'description', sortable: false },
        { text: 'Severity', value: 'severity', sortable: true },
        { text: 'Date', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      resolvedHeaders: [
        { text: 'Resource', value: 'resource', sortable: true },
        { text: 'Policy', value: 'policy', sortable: true },
        { text: 'Description', value: 'description', sortable: false },
        { text: 'Severity', value: 'severity', sortable: true },
        { text: 'Resolved Date', value: 'resolved_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ]
    };
  },
  computed: {
    ...mapGetters({
      policyViolations: 'security/policyViolations',
      policyLoading: 'security/isPolicyLoading',
      policyError: 'security/policyErrorMessage',
      unresolvedViolations: 'security/unresolvedViolations',
      resolvedViolations: 'security/resolvedViolations',
      criticalViolations: 'security/criticalViolations',
      highViolations: 'security/highViolations',
      mediumViolations: 'security/mediumViolations',
      lowViolations: 'security/lowViolations'
    })
  },
  created() {
    this.fetchPolicyViolations();
  },
  methods: {
    ...mapActions({
      fetchPolicyViolations: 'security/fetchPolicyViolations',
      resolveViolationAction: 'security/resolveViolation',
      setActive: 'chat/SET_ACTIVE',
      updateContext: 'chat/updateContext'
    }),
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getSeverityColor(severity) {
      switch (severity) {
        case 'CRITICAL':
          return 'error';
        case 'HIGH':
          return 'deep-orange';
        case 'MEDIUM':
          return 'warning';
        case 'LOW':
          return 'info';
        default:
          return 'grey';
      }
    },
    getResourceTypeColor(type) {
      switch (type) {
        case 'image':
          return 'primary';
        case 'container':
          return 'success';
        case 'volume':
          return 'warning';
        case 'network':
          return 'info';
        default:
          return 'grey';
      }
    },
    getActionColor(action) {
      switch (action) {
        case 'BLOCK':
          return 'error';
        case 'WARN':
          return 'warning';
        case 'ALLOW':
          return 'success';
        case 'AUDIT':
          return 'info';
        default:
          return 'grey';
      }
    },
    getResourceLink(violation) {
      switch (violation.resource_type) {
        case 'image':
          return `/images/${violation.resource_id}`;
        case 'container':
          return `/containers/${violation.resource_id}`;
        case 'volume':
          return `/volumes/${violation.resource_id}`;
        case 'network':
          return `/networks/${violation.resource_id}`;
        default:
          return '#';
      }
    },
    openViolationDetails(violation) {
      this.selectedViolation = violation;
      this.detailsDialog = true;
    },
    openResolveDialog(violation) {
      this.selectedViolation = violation;
      this.resolutionNotes = '';
      this.resolveDialog = true;
    },
    async resolveViolation() {
      if (!this.selectedViolation || !this.resolutionNotes) {
        return;
      }

      this.resolveSubmitting = true;

      try {
        await this.resolveViolationAction({
          violationId: this.selectedViolation.id,
          resolutionNotes: this.resolutionNotes
        });
        this.$emit('show-notification', {
          type: 'success',
          message: 'Violation resolved successfully'
        });
        this.resolveDialog = false;
        this.detailsDialog = false;
      } catch (error) {
        console.error('Error resolving violation:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to resolve violation: ' + (error.message || 'Unknown error')
        });
      } finally {
        this.resolveSubmitting = false;
      }
    },
    async resolveWithAI(violation) {
      try {
        // Start a security workflow for the violation
        const response = await axios.post(`/api/chat/security/start-workflow?violation_id=${violation.id}`);

        // Set context data for chat
        this.updateContext({
          currentPage: 'security',
          currentResourceType: violation.resource_type,
          currentResourceId: violation.resource_id,
          violation_id: violation.id,
          workflow_id: response.data.message.context?.workflow_id
        });

        // Open chat sidebar
        this.setActive(true);

        // Show notification
        this.$emit('show-notification', {
          type: 'info',
          message: 'AI-assisted resolution workflow started. Check the chat sidebar.'
        });

        // Close dialogs if open
        this.resolveDialog = false;
        this.detailsDialog = false;
      } catch (error) {
        console.error('Error starting violation resolution workflow:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to start AI resolution workflow.'
        });
      }
    }
  }
};
</script>

<style scoped>
.policy-violations {
  padding: 16px;
}
</style>
