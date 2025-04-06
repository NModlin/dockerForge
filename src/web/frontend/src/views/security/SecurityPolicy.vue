<template>
  <div class="security-policy">
    <div class="d-flex align-center mb-4">
      <h1 class="text-h4">Security Policies</h1>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        @click="openCreateDialog"
      >
        <v-icon left>mdi-plus</v-icon>
        New Policy
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

    <!-- Policy List -->
    <template v-else>
      <v-card v-if="!policyId">
        <v-data-table
          :headers="policyHeaders"
          :items="policies"
          :items-per-page="10"
          class="elevation-1"
        >
          <!-- Name Column -->
          <template v-slot:item.name="{ item }">
            <router-link
              :to="{ name: 'PolicyDetail', params: { id: item.id } }"
              class="text-decoration-none"
            >
              {{ item.name }}
            </router-link>
          </template>

          <!-- Status Column -->
          <template v-slot:item.enabled="{ item }">
            <v-chip
              :color="item.enabled ? 'success' : 'grey'"
              text-color="white"
              small
            >
              {{ item.enabled ? 'Enabled' : 'Disabled' }}
            </v-chip>
          </template>

          <!-- Rules Column -->
          <template v-slot:item.rules="{ item }">
            {{ item.rules.length }} rule{{ item.rules.length !== 1 ? 's' : '' }}
          </template>

          <!-- Created Column -->
          <template v-slot:item.created_at="{ item }">
            {{ formatDate(item.created_at) }}
          </template>

          <!-- Actions Column -->
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              small
              :to="{ name: 'PolicyDetail', params: { id: item.id } }"
              title="View Details"
            >
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="openEditDialog(item)"
              title="Edit Policy"
            >
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="togglePolicyStatus(item)"
              :title="item.enabled ? 'Disable Policy' : 'Enable Policy'"
              :color="item.enabled ? 'warning' : 'success'"
            >
              <v-icon small>{{ item.enabled ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off' }}</v-icon>
            </v-btn>
            <v-btn
              icon
              small
              @click="confirmDelete(item)"
              title="Delete Policy"
              color="error"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- Policy Detail View -->
      <div v-else>
        <v-btn
          text
          color="primary"
          class="mb-4"
          :to="{ name: 'SecurityPolicies' }"
        >
          <v-icon left>mdi-arrow-left</v-icon>
          Back to Policies
        </v-btn>

        <v-card v-if="currentPolicy" class="mb-4">
          <v-card-title class="headline d-flex align-center">
            <div>
              {{ currentPolicy.name }}
              <v-chip
                :color="currentPolicy.enabled ? 'success' : 'grey'"
                text-color="white"
                small
                class="ml-2"
              >
                {{ currentPolicy.enabled ? 'Enabled' : 'Disabled' }}
              </v-chip>
            </div>
            <v-spacer></v-spacer>
            <v-btn
              icon
              @click="openEditDialog(currentPolicy)"
              title="Edit Policy"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn
              icon
              @click="togglePolicyStatus(currentPolicy)"
              :title="currentPolicy.enabled ? 'Disable Policy' : 'Enable Policy'"
              :color="currentPolicy.enabled ? 'warning' : 'success'"
            >
              <v-icon>{{ currentPolicy.enabled ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off' }}</v-icon>
            </v-btn>
            <v-btn
              icon
              @click="confirmDelete(currentPolicy)"
              title="Delete Policy"
              color="error"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text>
            <p v-if="currentPolicy.description">{{ currentPolicy.description }}</p>
            <div class="mt-4">
              <strong>Created:</strong> {{ formatDate(currentPolicy.created_at) }}
            </div>
            <div v-if="currentPolicy.updated_at">
              <strong>Last Updated:</strong> {{ formatDate(currentPolicy.updated_at) }}
            </div>
            <div v-if="currentPolicy.applied_to && currentPolicy.applied_to.length > 0" class="mt-2">
              <strong>Applied To:</strong>
              <v-chip
                v-for="(pattern, index) in currentPolicy.applied_to"
                :key="index"
                small
                class="mr-1 mt-1"
              >
                {{ pattern }}
              </v-chip>
            </div>
          </v-card-text>
        </v-card>

        <!-- Rules List -->
        <h2 class="text-h5 mb-3">Policy Rules</h2>
        <v-card v-if="currentPolicy && currentPolicy.rules.length > 0">
          <v-data-table
            :headers="ruleHeaders"
            :items="currentPolicy.rules"
            :items-per-page="10"
            class="elevation-1"
          >
            <!-- Status Column -->
            <template v-slot:item.enabled="{ item }">
              <v-chip
                :color="item.enabled ? 'success' : 'grey'"
                text-color="white"
                small
              >
                {{ item.enabled ? 'Enabled' : 'Disabled' }}
              </v-chip>
            </template>

            <!-- Rule Type Column -->
            <template v-slot:item.rule_type="{ item }">
              <v-chip
                :color="getRuleTypeColor(item.rule_type)"
                text-color="white"
                small
              >
                {{ item.rule_type }}
              </v-chip>
            </template>

            <!-- Action Column -->
            <template v-slot:item.action="{ item }">
              <v-chip
                :color="getActionColor(item.action)"
                text-color="white"
                small
              >
                {{ item.action }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
        <v-card v-else class="pa-4 text-center">
          <p>No rules defined for this policy.</p>
          <v-btn
            color="primary"
            @click="openEditDialog(currentPolicy)"
          >
            Add Rules
          </v-btn>
        </v-card>
      </div>
    </template>

    <!-- Policy Form Dialog -->
    <v-dialog
      v-model="dialog"
      max-width="800px"
    >
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ isEditMode ? 'Edit Policy' : 'Create Policy' }}</span>
        </v-card-title>

        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="formData.name"
                    label="Policy Name"
                    required
                    :rules="[v => !!v || 'Name is required']"
                  ></v-text-field>
                </v-col>

                <v-col cols="12">
                  <v-textarea
                    v-model="formData.description"
                    label="Description"
                    rows="3"
                  ></v-textarea>
                </v-col>

                <v-col cols="12">
                  <v-switch
                    v-model="formData.enabled"
                    label="Enabled"
                    color="success"
                  ></v-switch>
                </v-col>

                <v-col cols="12">
                  <v-combobox
                    v-model="formData.applied_to"
                    label="Applied To (Resource Patterns)"
                    multiple
                    chips
                    small-chips
                    hint="Enter patterns like 'nginx:*' or 'web-*' to apply policy to specific resources"
                    persistent-hint
                  ></v-combobox>
                </v-col>

                <v-col cols="12">
                  <h3 class="text-h6 mb-2">Rules</h3>
                  <v-btn
                    color="primary"
                    text
                    @click="addRule"
                    class="mb-3"
                  >
                    <v-icon left>mdi-plus</v-icon>
                    Add Rule
                  </v-btn>

                  <div
                    v-for="(rule, index) in formData.rules"
                    :key="index"
                    class="rule-item pa-3 mb-3"
                  >
                    <div class="d-flex align-center mb-2">
                      <h4 class="text-subtitle-1">Rule {{ index + 1 }}</h4>
                      <v-spacer></v-spacer>
                      <v-btn
                        icon
                        small
                        color="error"
                        @click="removeRule(index)"
                      >
                        <v-icon small>mdi-delete</v-icon>
                      </v-btn>
                    </div>

                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="rule.name"
                          label="Rule Name"
                          required
                          :rules="[v => !!v || 'Rule name is required']"
                        ></v-text-field>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-select
                          v-model="rule.rule_type"
                          label="Rule Type"
                          :items="ruleTypes"
                          required
                          :rules="[v => !!v || 'Rule type is required']"
                        ></v-select>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="rule.pattern"
                          label="Pattern"
                          required
                          :rules="[v => !!v || 'Pattern is required']"
                          :hint="getPatternHint(rule.rule_type)"
                          persistent-hint
                        ></v-text-field>
                      </v-col>

                      <v-col cols="12" md="6">
                        <v-select
                          v-model="rule.action"
                          label="Action"
                          :items="actionTypes"
                          required
                          :rules="[v => !!v || 'Action is required']"
                        ></v-select>
                      </v-col>

                      <v-col cols="12">
                        <v-textarea
                          v-model="rule.description"
                          label="Description"
                          rows="2"
                        ></v-textarea>
                      </v-col>

                      <v-col cols="12">
                        <v-switch
                          v-model="rule.enabled"
                          label="Enabled"
                          color="success"
                        ></v-switch>
                      </v-col>
                    </v-row>
                  </div>

                  <v-alert
                    v-if="formData.rules.length === 0"
                    type="info"
                    text
                  >
                    No rules defined. Add at least one rule to create an effective policy.
                  </v-alert>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="closeDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!valid || formSubmitting"
            @click="savePolicy"
          >
            <v-progress-circular
              v-if="formSubmitting"
              indeterminate
              size="20"
              width="2"
              class="mr-2"
            ></v-progress-circular>
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="deleteDialog"
      max-width="400px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Delete Policy
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete the policy "{{ policyToDelete?.name }}"? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="deleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            :disabled="deleteSubmitting"
            @click="deletePolicy"
          >
            <v-progress-circular
              v-if="deleteSubmitting"
              indeterminate
              size="20"
              width="2"
              class="mr-2"
            ></v-progress-circular>
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import { v4 as uuidv4 } from 'uuid';

export default {
  name: 'SecurityPolicy',
  props: {
    policyId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      valid: false,
      dialog: false,
      deleteDialog: false,
      isEditMode: false,
      formSubmitting: false,
      deleteSubmitting: false,
      policyToDelete: null,
      formData: {
        name: '',
        description: '',
        enabled: true,
        rules: [],
        applied_to: []
      },
      policyHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Status', value: 'enabled', sortable: true },
        { text: 'Rules', value: 'rules', sortable: false },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      ruleHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Type', value: 'rule_type', sortable: true },
        { text: 'Pattern', value: 'pattern', sortable: true },
        { text: 'Action', value: 'action', sortable: true },
        { text: 'Status', value: 'enabled', sortable: true }
      ],
      ruleTypes: [
        'SEVERITY',
        'CVE',
        'PACKAGE',
        'IMAGE',
        'CONTAINER',
        'PRIVILEGED',
        'CAPABILITY',
        'VOLUME',
        'PORT',
        'NETWORK'
      ],
      actionTypes: [
        'BLOCK',
        'WARN',
        'ALLOW',
        'AUDIT'
      ]
    };
  },
  computed: {
    ...mapGetters({
      policies: 'security/policies',
      currentPolicy: 'security/currentPolicy',
      policyLoading: 'security/isPolicyLoading',
      policyError: 'security/policyErrorMessage'
    })
  },
  watch: {
    policyId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchPolicy(newVal);
        }
      }
    }
  },
  created() {
    this.fetchPolicies();
  },
  methods: {
    ...mapActions({
      fetchPolicies: 'security/fetchPolicies',
      fetchPolicy: 'security/fetchPolicy',
      createPolicy: 'security/createPolicy',
      updatePolicy: 'security/updatePolicy',
      deletePolicy: 'security/deletePolicy'
    }),
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    getRuleTypeColor(type) {
      switch (type) {
        case 'SEVERITY':
          return 'error';
        case 'CVE':
          return 'deep-orange';
        case 'PACKAGE':
          return 'orange';
        case 'IMAGE':
          return 'primary';
        case 'CONTAINER':
          return 'success';
        case 'PRIVILEGED':
          return 'purple';
        case 'CAPABILITY':
          return 'indigo';
        case 'VOLUME':
          return 'teal';
        case 'PORT':
          return 'blue';
        case 'NETWORK':
          return 'cyan';
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
    getPatternHint(ruleType) {
      switch (ruleType) {
        case 'SEVERITY':
          return 'E.g., "CRITICAL" or "HIGH"';
        case 'CVE':
          return 'E.g., "CVE-2021-*" or specific CVE ID';
        case 'PACKAGE':
          return 'E.g., "log4j:*" or "openssl:1.1.*"';
        case 'IMAGE':
          return 'E.g., "nginx:*" or "*/debian:*"';
        case 'CONTAINER':
          return 'E.g., "web-*" or specific container name';
        case 'PRIVILEGED':
          return 'E.g., "true" to detect privileged containers';
        case 'CAPABILITY':
          return 'E.g., "SYS_ADMIN" or "NET_ADMIN"';
        case 'VOLUME':
          return 'E.g., "/etc/*" or "/var/run/docker.sock"';
        case 'PORT':
          return 'E.g., "22" or "3306"';
        case 'NETWORK':
          return 'E.g., "host" or "bridge"';
        default:
          return 'Enter a pattern to match';
      }
    },
    openCreateDialog() {
      this.isEditMode = false;
      this.formData = {
        name: '',
        description: '',
        enabled: true,
        rules: [],
        applied_to: []
      };
      this.dialog = true;
    },
    openEditDialog(policy) {
      this.isEditMode = true;
      // Deep clone the policy to avoid modifying the original
      this.formData = JSON.parse(JSON.stringify({
        name: policy.name,
        description: policy.description || '',
        enabled: policy.enabled,
        rules: policy.rules || [],
        applied_to: policy.applied_to || []
      }));
      this.dialog = true;
    },
    closeDialog() {
      this.dialog = false;
      this.$nextTick(() => {
        this.$refs.form.reset();
      });
    },
    addRule() {
      this.formData.rules.push({
        id: uuidv4(),
        name: '',
        description: '',
        rule_type: 'SEVERITY',
        pattern: '',
        action: 'WARN',
        enabled: true
      });
    },
    removeRule(index) {
      this.formData.rules.splice(index, 1);
    },
    async savePolicy() {
      if (!this.$refs.form.validate()) {
        return;
      }

      this.formSubmitting = true;

      try {
        if (this.isEditMode) {
          await this.updatePolicy({
            policyId: this.currentPolicy.id,
            policyData: this.formData
          });
          this.$emit('show-notification', {
            type: 'success',
            message: 'Policy updated successfully'
          });
        } else {
          await this.createPolicy(this.formData);
          this.$emit('show-notification', {
            type: 'success',
            message: 'Policy created successfully'
          });
        }
        this.closeDialog();
      } catch (error) {
        console.error('Error saving policy:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to save policy: ' + (error.message || 'Unknown error')
        });
      } finally {
        this.formSubmitting = false;
      }
    },
    confirmDelete(policy) {
      this.policyToDelete = policy;
      this.deleteDialog = true;
    },
    async deletePolicy() {
      if (!this.policyToDelete) {
        return;
      }

      this.deleteSubmitting = true;

      try {
        await this.deletePolicy(this.policyToDelete.id);
        this.$emit('show-notification', {
          type: 'success',
          message: 'Policy deleted successfully'
        });
        this.deleteDialog = false;

        // If we're on the detail page, redirect back to the list
        if (this.policyId) {
          this.$router.push({ name: 'SecurityPolicies' });
        }
      } catch (error) {
        console.error('Error deleting policy:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to delete policy: ' + (error.message || 'Unknown error')
        });
      } finally {
        this.deleteSubmitting = false;
      }
    },
    async togglePolicyStatus(policy) {
      try {
        await this.updatePolicy({
          policyId: policy.id,
          policyData: {
            enabled: !policy.enabled
          }
        });
        this.$emit('show-notification', {
          type: 'success',
          message: `Policy ${policy.enabled ? 'disabled' : 'enabled'} successfully`
        });
      } catch (error) {
        console.error('Error toggling policy status:', error);
        this.$emit('show-notification', {
          type: 'error',
          message: 'Failed to update policy status: ' + (error.message || 'Unknown error')
        });
      }
    }
  }
};
</script>

<style scoped>
.security-policy {
  padding: 16px;
}

.rule-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f5f5f5;
}
</style>
