<template>
  <div class="api-keys">
    <v-card flat>
      <v-card-text>
        <div class="d-flex align-center mb-4">
          <h2 class="text-h5">API Key Management</h2>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="showCreateDialog"
            :disabled="loading"
          >
            <v-icon left>mdi-plus</v-icon>
            Create API Key
          </v-btn>
        </div>

        <v-alert
          v-if="error"
          type="error"
          dismissible
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-alert
          v-if="success"
          type="success"
          dismissible
          class="mb-4"
        >
          {{ success }}
        </v-alert>

        <v-alert
          type="info"
          outlined
          class="mb-4"
        >
          <p>API keys allow external applications to access DockerForge on your behalf. Each key can have specific permissions to limit what actions it can perform.</p>
          <p class="mb-0"><strong>Security Note:</strong> API keys are sensitive credentials. Never share them publicly or commit them to source code repositories.</p>
        </v-alert>

        <!-- Loading State -->
        <div v-if="loading" class="d-flex justify-center my-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <!-- API Keys List -->
        <template v-else>
          <v-data-table
            :headers="headers"
            :items="apiKeys"
            :items-per-page="10"
            :footer-props="{
              'items-per-page-options': [5, 10, 15, 20],
              'items-per-page-text': 'Keys per page'
            }"
            class="elevation-1"
            :no-data-text="apiKeys.length === 0 ? 'No API keys found. Create one to get started.' : 'No results found.'"
          >
            <!-- Name Column -->
            <template v-slot:item.name="{ item }">
              <div class="font-weight-medium">{{ item.name }}</div>
            </template>

            <!-- Key Preview Column -->
            <template v-slot:item.key_preview="{ item }">
              <div class="d-flex align-center">
                <code>{{ item.key_preview }}</code>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      x-small
                      v-bind="attrs"
                      v-on="on"
                      @click="copyApiKey(item)"
                      class="ml-2"
                    >
                      <v-icon small>mdi-content-copy</v-icon>
                    </v-btn>
                  </template>
                  <span>Copy to clipboard</span>
                </v-tooltip>
              </div>
            </template>

            <!-- Created Date Column -->
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>

            <!-- Last Used Column -->
            <template v-slot:item.last_used="{ item }">
              {{ item.last_used ? formatDate(item.last_used) : 'Never' }}
            </template>

            <!-- Permissions Column -->
            <template v-slot:item.permissions="{ item }">
              <v-chip
                v-if="item.read_only"
                x-small
                color="blue-grey"
                text-color="white"
                class="mr-1"
              >
                Read-only
              </v-chip>
              <v-chip
                v-else
                x-small
                color="deep-purple"
                text-color="white"
                class="mr-1"
              >
                Full Access
              </v-chip>
              <v-chip
                v-for="scope in item.scopes || []"
                :key="scope"
                x-small
                color="primary"
                text-color="white"
                class="mr-1 mt-1"
              >
                {{ scope }}
              </v-chip>
            </template>

            <!-- Actions Column -->
            <template v-slot:item.actions="{ item }">
              <div class="d-flex">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      small
                      v-bind="attrs"
                      v-on="on"
                      @click="showUsageDialog(item)"
                      color="primary"
                      class="mr-2"
                    >
                      <v-icon small>mdi-chart-bar</v-icon>
                    </v-btn>
                  </template>
                  <span>View Usage Statistics</span>
                </v-tooltip>

                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      small
                      v-bind="attrs"
                      v-on="on"
                      @click="showRevokeDialog(item)"
                      color="error"
                    >
                      <v-icon small>mdi-delete</v-icon>
                    </v-btn>
                  </template>
                  <span>Revoke API Key</span>
                </v-tooltip>
              </div>
            </template>
          </v-data-table>
        </template>
      </v-card-text>
    </v-card>

    <!-- Create API Key Dialog -->
    <v-dialog v-model="createDialog" max-width="600">
      <v-card>
        <v-card-title>Create New API Key</v-card-title>
        <v-card-text>
          <v-form ref="createForm" v-model="createFormValid">
            <v-text-field
              v-model="apiKeyForm.name"
              label="Key Name"
              hint="A descriptive name to identify this key"
              persistent-hint
              :rules="[v => !!v || 'Name is required']"
              required
            ></v-text-field>

            <v-select
              v-model="apiKeyForm.expiration"
              :items="expirationOptions"
              label="Expiration"
              hint="When this key should expire"
              persistent-hint
              class="mt-4"
            ></v-select>

            <v-switch
              v-model="apiKeyForm.read_only"
              label="Read-only Access"
              hint="Limit this key to read-only operations"
              persistent-hint
              class="mt-4"
            ></v-switch>

            <v-expansion-panels v-if="!apiKeyForm.read_only" class="mt-4">
              <v-expansion-panel>
                <v-expansion-panel-header>
                  Advanced Permissions
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <p class="text-caption mb-2">Select specific permissions for this API key:</p>

                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Containers - View"
                    value="containers:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Containers - Manage"
                    value="containers:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Images - View"
                    value="images:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Images - Manage"
                    value="images:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Volumes - View"
                    value="volumes:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Volumes - Manage"
                    value="volumes:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Networks - View"
                    value="networks:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Networks - Manage"
                    value="networks:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Compose - View"
                    value="compose:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Compose - Manage"
                    value="compose:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Security - View"
                    value="security:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Security - Manage"
                    value="security:write"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="Monitoring - View"
                    value="monitoring:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                  <v-checkbox
                    v-model="apiKeyForm.scopes"
                    label="System - View"
                    value="system:read"
                    hide-details
                    class="my-0 py-0"
                  ></v-checkbox>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="createDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="createApiKey"
            :disabled="!createFormValid || creatingKey"
            :loading="creatingKey"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New API Key Dialog -->
    <v-dialog v-model="newKeyDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="headline">API Key Created</v-card-title>
        <v-card-text>
          <v-alert
            type="warning"
            outlined
            class="mb-4"
          >
            <p><strong>Important:</strong> This is the only time your API key will be shown in full. Please copy it now and store it securely.</p>
          </v-alert>

          <div class="d-flex align-center">
            <v-text-field
              v-model="newApiKey"
              label="API Key"
              readonly
              outlined
              class="font-weight-medium"
            ></v-text-field>

            <v-btn
              icon
              class="ml-2"
              @click="copyNewApiKey"
            >
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>
          </div>

          <p class="mt-4">You can use this key to authenticate API requests to DockerForge:</p>

          <v-card outlined class="pa-3 mt-2">
            <code>curl -H "Authorization: Bearer {{ newApiKey }}" https://your-dockerforge-instance/api/containers</code>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="newKeyDialog = false"
          >
            I've Saved My Key
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Revoke API Key Dialog -->
    <v-dialog v-model="revokeDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Revoke API Key</v-card-title>
        <v-card-text>
          Are you sure you want to revoke the API key "{{ selectedKey ? selectedKey.name : '' }}"?
          This action cannot be undone, and any applications using this key will no longer be able to access the API.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            @click="revokeDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="revokeApiKey"
            :loading="revokingKey"
          >
            Revoke
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- API Key Usage Dialog -->
    <v-dialog v-model="usageDialog" max-width="1000" persistent>
      <v-card>
        <v-card-title class="headline">
          API Key Usage: {{ selectedKey ? selectedKey.name : '' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="closeUsageDialog">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <api-key-usage v-if="selectedKey" :api-key-id="selectedKey.id" />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="closeUsageDialog"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { format } from 'date-fns';
import { mapState, mapGetters, mapActions } from 'vuex';
import ApiKeyUsage from '@/components/settings/ApiKeyUsage.vue';

export default {
  name: 'ApiKeys',
  components: {
    ApiKeyUsage
  },
  data() {
    return {
      success: null,
      createDialog: false,
      newKeyDialog: false,
      revokeDialog: false,
      usageDialog: false,
      creatingKey: false,
      revokingKey: false,
      createFormValid: false,
      selectedKey: null,

      // Form data
      apiKeyForm: {
        name: '',
        expiration: 'never',
        read_only: false,
        scopes: []
      },

      // Table headers
      headers: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Key', value: 'key_preview', sortable: false },
        { text: 'Created', value: 'created_at', sortable: true },
        { text: 'Last Used', value: 'last_used', sortable: true },
        { text: 'Permissions', value: 'permissions', sortable: false },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],

      // Options
      expirationOptions: [
        { text: 'Never expires', value: 'never' },
        { text: '30 days', value: '30d' },
        { text: '90 days', value: '90d' },
        { text: '1 year', value: '1y' }
      ]
    };
  },
  computed: {
    ...mapState('apiKeys', ['loading', 'error']),
    ...mapGetters('apiKeys', ['getApiKeys', 'getCurrentKey']),

    apiKeys() {
      return this.getApiKeys;
    },

    newApiKey() {
      return this.getCurrentKey ? this.getCurrentKey.key : '';
    }
  },
  created() {
    this.fetchApiKeys();
  },
  methods: {
    ...mapActions('apiKeys', [
      'fetchApiKeys',
      'createApiKey',
      'updateApiKey',
      'deleteApiKey',
      'clearCurrentKey'
    ]),

    showCreateDialog() {
      // Reset form
      this.apiKeyForm = {
        name: '',
        expiration: 'never',
        read_only: false,
        scopes: []
      };

      // Show dialog
      this.createDialog = true;
    },

    async createApiKey() {
      if (!this.$refs.createForm.validate()) return;

      this.creatingKey = true;
      this.error = null;
      this.success = null;

      try {
        // Convert form data to API format
        const keyData = {
          name: this.apiKeyForm.name,
          expiration: this.apiKeyForm.expiration,
          is_read_only: this.apiKeyForm.read_only,
          scopes: this.apiKeyForm.read_only ? [] : this.apiKeyForm.scopes
        };

        // Create the API key using the store action
        await this.$store.dispatch('apiKeys/createApiKey', keyData);

        // Close create dialog and open new key dialog
        this.createDialog = false;
        this.newKeyDialog = true;

        this.success = 'API key created successfully';
      } catch (error) {
        this.error = 'Failed to create API key';
        console.error('Error creating API key:', error);
      } finally {
        this.creatingKey = false;
      }
    },

    showRevokeDialog(key) {
      this.selectedKey = key;
      this.revokeDialog = true;
    },

    async revokeApiKey() {
      if (!this.selectedKey) return;

      this.revokingKey = true;
      this.error = null;
      this.success = null;

      try {
        // Delete the API key using the store action
        await this.$store.dispatch('apiKeys/deleteApiKey', this.selectedKey.id);

        // Close dialog
        this.revokeDialog = false;
        this.selectedKey = null;

        this.success = 'API key revoked successfully';
      } catch (error) {
        this.error = 'Failed to revoke API key';
        console.error('Error revoking API key:', error);
      } finally {
        this.revokingKey = false;
      }
    },

    copyApiKey(key) {
      // In a real implementation, this would copy the actual key
      // For security reasons, we don't store the full key in the UI
      // This is just a mock implementation
      navigator.clipboard.writeText(key.key_preview)
        .then(() => {
          this.$store.dispatch('showSnackbar', {
            text: 'Only the key preview was copied. Full keys are only shown once at creation time.',
            color: 'info'
          });
        })
        .catch(err => {
          console.error('Could not copy text: ', err);
        });
    },

    copyNewApiKey() {
      navigator.clipboard.writeText(this.newApiKey)
        .then(() => {
          this.$store.dispatch('showSnackbar', {
            text: 'API key copied to clipboard',
            color: 'success'
          });
        })
        .catch(err => {
          console.error('Could not copy text: ', err);
        });
    },

    closeNewKeyDialog() {
      this.newKeyDialog = false;
      this.$store.dispatch('apiKeys/clearCurrentKey');
    },

    showUsageDialog(key) {
      this.selectedKey = key;
      this.usageDialog = true;
    },

    closeUsageDialog() {
      this.usageDialog = false;
      this.selectedKey = null;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      try {
        return format(new Date(dateString), 'MMM d, yyyy h:mm a');
      } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.api-keys {
  max-width: 100%;
}
</style>
