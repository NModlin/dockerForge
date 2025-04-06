<template>
  <div class="profile">
    <h1 class="text-h4 mb-4">My Profile</h1>
    
    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-center align-center my-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>
    
    <!-- Profile Content -->
    <template v-else>
      <v-row>
        <!-- Profile Information -->
        <v-col cols="12" md="4">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-account</v-icon>
              Profile Information
            </v-card-title>
            <v-card-text class="text-center">
              <v-avatar size="100" color="primary" class="mb-4">
                <v-icon size="64" color="white">mdi-account</v-icon>
              </v-avatar>
              
              <h2 class="text-h5">{{ user.username }}</h2>
              <p class="text-body-1">{{ user.email }}</p>
              
              <v-chip
                class="mt-2"
                :color="user.is_admin ? 'error' : 'primary'"
                text-color="white"
              >
                {{ user.is_admin ? 'Administrator' : 'User' }}
              </v-chip>
              
              <v-divider class="my-4"></v-divider>
              
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-calendar</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Member since</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(user.created_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-clock-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Last login</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(user.last_login) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" text @click="editProfileDialog = true">
                <v-icon left>mdi-account-edit</v-icon>
                Edit Profile
              </v-btn>
            </v-card-actions>
          </v-card>
          
          <v-card>
            <v-card-title>
              <v-icon left>mdi-shield-account</v-icon>
              Security
            </v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-lock</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Password</v-list-item-title>
                    <v-list-item-subtitle>Last changed {{ formatDate(user.password_changed_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-btn small text color="primary" to="/change-password">
                      Change
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-two-factor-authentication</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Two-Factor Authentication</v-list-item-title>
                    <v-list-item-subtitle>{{ user.two_factor_enabled ? 'Enabled' : 'Disabled' }}</v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-btn small text color="primary" @click="setup2FADialog = true">
                      {{ user.two_factor_enabled ? 'Manage' : 'Enable' }}
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        
        <!-- Activity and API Keys -->
        <v-col cols="12" md="8">
          <v-card class="mb-4">
            <v-card-title>
              <v-icon left>mdi-key</v-icon>
              API Keys
              <v-spacer></v-spacer>
              <v-btn color="primary" small @click="createAPIKeyDialog = true">
                <v-icon left small>mdi-plus</v-icon>
                New API Key
              </v-btn>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="apiKeyHeaders"
                :items="apiKeys"
                :items-per-page="5"
                :loading="loadingAPIKeys"
                no-data-text="No API keys found"
              >
                <!-- Name Column -->
                <template v-slot:item.name="{ item }">
                  <div>{{ item.name }}</div>
                  <div class="text-caption">Created {{ formatDate(item.created_at) }}</div>
                </template>
                
                <!-- Key Column -->
                <template v-slot:item.key="{ item }">
                  <div class="d-flex align-center">
                    <span class="text-truncate" style="max-width: 200px">{{ item.key_preview }}</span>
                    <v-btn icon x-small class="ml-2" @click="copyAPIKey(item.key)" v-if="item.key">
                      <v-icon x-small>mdi-content-copy</v-icon>
                    </v-btn>
                  </div>
                </template>
                
                <!-- Last Used Column -->
                <template v-slot:item.last_used="{ item }">
                  {{ item.last_used ? formatDate(item.last_used) : 'Never' }}
                </template>
                
                <!-- Actions Column -->
                <template v-slot:item.actions="{ item }">
                  <v-btn icon small color="error" @click="confirmDeleteAPIKey(item)">
                    <v-icon small>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
          
          <v-card>
            <v-card-title>
              <v-icon left>mdi-history</v-icon>
              Recent Activity
            </v-card-title>
            <v-card-text>
              <v-timeline dense>
                <v-timeline-item
                  v-for="activity in recentActivity"
                  :key="activity.id"
                  :color="getActivityColor(activity.type)"
                  small
                >
                  <div class="d-flex justify-space-between">
                    <div>
                      <strong>{{ activity.action }}</strong>
                      <div class="text-caption">{{ activity.details }}</div>
                    </div>
                    <div class="text-caption">{{ formatDate(activity.timestamp) }}</div>
                  </div>
                </v-timeline-item>
              </v-timeline>
              
              <div class="text-center mt-4" v-if="recentActivity.length > 0">
                <v-btn text color="primary" @click="loadMoreActivity">
                  Load More
                </v-btn>
              </div>
              
              <div v-if="recentActivity.length === 0" class="text-center pa-4">
                <v-icon large color="grey lighten-1">mdi-history</v-icon>
                <p class="text-body-2 mt-2">No recent activity</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
    
    <!-- Edit Profile Dialog -->
    <v-dialog v-model="editProfileDialog" max-width="500">
      <v-card>
        <v-card-title>Edit Profile</v-card-title>
        <v-card-text>
          <v-form ref="profileForm" v-model="profileFormValid">
            <v-text-field
              v-model="profileForm.username"
              label="Username"
              :rules="[v => !!v || 'Username is required']"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="profileForm.email"
              label="Email"
              type="email"
              :rules="[
                v => !!v || 'Email is required',
                v => /.+@.+\..+/.test(v) || 'Email must be valid'
              ]"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="profileForm.full_name"
              label="Full Name"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="editProfileDialog = false">Cancel</v-btn>
          <v-btn color="primary" :disabled="!profileFormValid" @click="updateProfile">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Create API Key Dialog -->
    <v-dialog v-model="createAPIKeyDialog" max-width="500">
      <v-card>
        <v-card-title>Create API Key</v-card-title>
        <v-card-text>
          <v-form ref="apiKeyForm" v-model="apiKeyFormValid">
            <v-text-field
              v-model="apiKeyForm.name"
              label="Key Name"
              :rules="[v => !!v || 'Key name is required']"
              required
            ></v-text-field>
            
            <v-select
              v-model="apiKeyForm.expiration"
              :items="expirationOptions"
              label="Expiration"
              item-text="text"
              item-value="value"
            ></v-select>
            
            <v-checkbox
              v-model="apiKeyForm.read_only"
              label="Read-only access"
              hint="Limits this key to read-only operations"
              persistent-hint
            ></v-checkbox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="createAPIKeyDialog = false">Cancel</v-btn>
          <v-btn color="primary" :disabled="!apiKeyFormValid" @click="createAPIKey">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- New API Key Created Dialog -->
    <v-dialog v-model="newAPIKeyDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="headline">API Key Created</v-card-title>
        <v-card-text>
          <p>Your new API key has been created. Please copy it now as you won't be able to see it again.</p>
          
          <v-alert type="warning" outlined class="mb-4">
            Make sure to store this key securely. It will not be displayed again.
          </v-alert>
          
          <v-text-field
            v-model="newAPIKey"
            label="API Key"
            readonly
            outlined
            append-icon="mdi-content-copy"
            @click:append="copyAPIKey(newAPIKey)"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="newAPIKeyDialog = false">Done</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete API Key Confirmation Dialog -->
    <v-dialog v-model="deleteAPIKeyDialog" max-width="500">
      <v-card>
        <v-card-title class="headline">Delete API Key</v-card-title>
        <v-card-text>
          <p>Are you sure you want to delete the API key "{{ apiKeyToDelete?.name }}"?</p>
          <p>This action cannot be undone and any applications using this key will no longer be able to access the API.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteAPIKeyDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteAPIKey">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 2FA Setup Dialog -->
    <v-dialog v-model="setup2FADialog" max-width="500">
      <v-card>
        <v-card-title>Two-Factor Authentication</v-card-title>
        <v-card-text>
          <div v-if="user.two_factor_enabled">
            <p>Two-factor authentication is currently enabled for your account.</p>
            <v-btn color="error" block class="mt-4" @click="disable2FA">
              Disable Two-Factor Authentication
            </v-btn>
          </div>
          <div v-else>
            <p>Enhance your account security by enabling two-factor authentication.</p>
            <div class="text-center my-4">
              <img src="https://via.placeholder.com/200x200?text=QR+Code" alt="QR Code" class="qr-code" />
              <p class="text-caption mt-2">Scan this QR code with your authenticator app</p>
            </div>
            <v-text-field
              v-model="twoFactorCode"
              label="Verification Code"
              hint="Enter the code from your authenticator app"
              persistent-hint
              :rules="[v => !!v || 'Code is required', v => v.length === 6 || 'Code must be 6 digits']"
            ></v-text-field>
            <v-btn color="primary" block class="mt-4" :disabled="!twoFactorCode || twoFactorCode.length !== 6" @click="enable2FA">
              Verify and Enable
            </v-btn>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="setup2FADialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'Profile',
  data() {
    return {
      loading: true,
      loadingAPIKeys: true,
      error: null,
      
      // Profile data
      user: {
        username: '',
        email: '',
        full_name: '',
        is_admin: false,
        created_at: null,
        last_login: null,
        password_changed_at: null,
        two_factor_enabled: false
      },
      
      // API Keys
      apiKeys: [],
      apiKeyHeaders: [
        { text: 'Name', value: 'name', sortable: true },
        { text: 'Key', value: 'key', sortable: false },
        { text: 'Last Used', value: 'last_used', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
      ],
      
      // Activity
      recentActivity: [],
      activityPage: 1,
      
      // Dialogs
      editProfileDialog: false,
      createAPIKeyDialog: false,
      newAPIKeyDialog: false,
      deleteAPIKeyDialog: false,
      setup2FADialog: false,
      
      // Forms
      profileFormValid: false,
      profileForm: {
        username: '',
        email: '',
        full_name: ''
      },
      
      apiKeyFormValid: false,
      apiKeyForm: {
        name: '',
        expiration: 'never',
        read_only: false
      },
      
      expirationOptions: [
        { text: 'Never expires', value: 'never' },
        { text: '30 days', value: '30d' },
        { text: '60 days', value: '60d' },
        { text: '90 days', value: '90d' },
        { text: '1 year', value: '1y' }
      ],
      
      newAPIKey: '',
      apiKeyToDelete: null,
      
      // 2FA
      twoFactorCode: ''
    };
  },
  computed: {
    ...mapGetters('auth', ['currentUser'])
  },
  created() {
    this.loadProfile();
    this.loadAPIKeys();
    this.loadActivity();
  },
  methods: {
    ...mapActions('auth', ['updateUserProfile']),
    
    async loadProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        // In a real app, this would fetch from the API
        // For now, use the current user from the store
        this.user = {
          ...this.currentUser,
          created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago
          last_login: new Date().toISOString(),
          password_changed_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), // 60 days ago
          two_factor_enabled: false
        };
        
        // Initialize profile form
        this.profileForm = {
          username: this.user.username,
          email: this.user.email,
          full_name: this.user.full_name || ''
        };
      } catch (error) {
        this.error = `Failed to load profile: ${error.message}`;
        console.error('Error loading profile:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async loadAPIKeys() {
      this.loadingAPIKeys = true;
      
      try {
        // In a real app, this would fetch from the API
        // For now, use mock data
        this.apiKeys = [
          {
            id: 1,
            name: 'Development API Key',
            key_preview: 'df_1234...5678',
            created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
            last_used: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            read_only: false
          },
          {
            id: 2,
            name: 'CI/CD Pipeline',
            key_preview: 'df_abcd...efgh',
            created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
            last_used: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
            read_only: false
          }
        ];
      } catch (error) {
        console.error('Error loading API keys:', error);
      } finally {
        this.loadingAPIKeys = false;
      }
    },
    
    async loadActivity() {
      try {
        // In a real app, this would fetch from the API
        // For now, use mock data
        const activities = [
          {
            id: 1,
            type: 'login',
            action: 'Logged in',
            details: 'Successful login from 192.168.1.100',
            timestamp: new Date().toISOString()
          },
          {
            id: 2,
            type: 'container',
            action: 'Created container',
            details: 'Created container "web-server" from image nginx:latest',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 3,
            type: 'image',
            action: 'Pulled image',
            details: 'Pulled image "postgres:13"',
            timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 4,
            type: 'security',
            action: 'Changed password',
            details: 'Password changed successfully',
            timestamp: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString()
          }
        ];
        
        this.recentActivity = [...this.recentActivity, ...activities];
      } catch (error) {
        console.error('Error loading activity:', error);
      }
    },
    
    loadMoreActivity() {
      this.activityPage++;
      this.loadActivity();
    },
    
    async updateProfile() {
      try {
        // In a real app, this would update via the API
        await this.updateUserProfile({
          username: this.profileForm.username,
          email: this.profileForm.email,
          full_name: this.profileForm.full_name
        });
        
        // Update local user object
        this.user = {
          ...this.user,
          username: this.profileForm.username,
          email: this.profileForm.email,
          full_name: this.profileForm.full_name
        };
        
        // Close dialog
        this.editProfileDialog = false;
        
        // Show success message
        this.$store.dispatch('showSnackbar', {
          text: 'Profile updated successfully',
          color: 'success'
        });
      } catch (error) {
        console.error('Error updating profile:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to update profile: ${error.message}`,
          color: 'error'
        });
      }
    },
    
    async createAPIKey() {
      try {
        // In a real app, this would create via the API
        // For now, simulate API key creation
        this.newAPIKey = 'df_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        
        // Add to API keys list
        this.apiKeys.unshift({
          id: Date.now(),
          name: this.apiKeyForm.name,
          key_preview: this.newAPIKey.substring(0, 8) + '...' + this.newAPIKey.substring(this.newAPIKey.length - 4),
          created_at: new Date().toISOString(),
          last_used: null,
          read_only: this.apiKeyForm.read_only
        });
        
        // Close create dialog and open new key dialog
        this.createAPIKeyDialog = false;
        this.newAPIKeyDialog = true;
        
        // Reset form
        this.apiKeyForm = {
          name: '',
          expiration: 'never',
          read_only: false
        };
      } catch (error) {
        console.error('Error creating API key:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to create API key: ${error.message}`,
          color: 'error'
        });
      }
    },
    
    confirmDeleteAPIKey(apiKey) {
      this.apiKeyToDelete = apiKey;
      this.deleteAPIKeyDialog = true;
    },
    
    async deleteAPIKey() {
      try {
        // In a real app, this would delete via the API
        // For now, just remove from the local list
        const index = this.apiKeys.findIndex(key => key.id === this.apiKeyToDelete.id);
        if (index !== -1) {
          this.apiKeys.splice(index, 1);
        }
        
        // Close dialog
        this.deleteAPIKeyDialog = false;
        this.apiKeyToDelete = null;
        
        // Show success message
        this.$store.dispatch('showSnackbar', {
          text: 'API key deleted successfully',
          color: 'success'
        });
      } catch (error) {
        console.error('Error deleting API key:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to delete API key: ${error.message}`,
          color: 'error'
        });
      }
    },
    
    copyAPIKey(key) {
      navigator.clipboard.writeText(key).then(() => {
        this.$store.dispatch('showSnackbar', {
          text: 'API key copied to clipboard',
          color: 'success'
        });
      }).catch(err => {
        console.error('Could not copy text: ', err);
      });
    },
    
    async enable2FA() {
      try {
        // In a real app, this would enable 2FA via the API
        // For now, just update the local user object
        this.user.two_factor_enabled = true;
        
        // Close dialog
        this.setup2FADialog = false;
        this.twoFactorCode = '';
        
        // Show success message
        this.$store.dispatch('showSnackbar', {
          text: 'Two-factor authentication enabled successfully',
          color: 'success'
        });
      } catch (error) {
        console.error('Error enabling 2FA:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to enable two-factor authentication: ${error.message}`,
          color: 'error'
        });
      }
    },
    
    async disable2FA() {
      try {
        // In a real app, this would disable 2FA via the API
        // For now, just update the local user object
        this.user.two_factor_enabled = false;
        
        // Close dialog
        this.setup2FADialog = false;
        
        // Show success message
        this.$store.dispatch('showSnackbar', {
          text: 'Two-factor authentication disabled successfully',
          color: 'success'
        });
      } catch (error) {
        console.error('Error disabling 2FA:', error);
        this.$store.dispatch('showSnackbar', {
          text: `Failed to disable two-factor authentication: ${error.message}`,
          color: 'error'
        });
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
      
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      
      return date.toLocaleDateString();
    },
    
    getActivityColor(type) {
      switch (type) {
        case 'login': return 'primary';
        case 'container': return 'success';
        case 'image': return 'info';
        case 'volume': return 'warning';
        case 'network': return 'purple';
        case 'security': return 'error';
        default: return 'grey';
      }
    }
  }
};
</script>

<style scoped>
.profile {
  max-width: 1200px;
  margin: 0 auto;
}

.qr-code {
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
