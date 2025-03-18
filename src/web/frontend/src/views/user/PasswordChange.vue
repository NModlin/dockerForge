<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Change Password</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-alert
              v-if="error"
              type="error"
              dismissible
              @click="error = null"
            >
              {{ error }}
            </v-alert>
            <v-alert
              v-if="success"
              type="success"
              dismissible
              @click="success = null"
            >
              {{ success }}
            </v-alert>
            <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="changePassword">
              <v-text-field
                v-model="currentPassword"
                :rules="currentPasswordRules"
                label="Current Password"
                prepend-icon="mdi-lock-outline"
                type="password"
                required
                :disabled="loading"
              ></v-text-field>

              <v-text-field
                v-model="newPassword"
                :rules="newPasswordRules"
                label="New Password"
                prepend-icon="mdi-lock"
                type="password"
                required
                :disabled="loading"
              ></v-text-field>

              <v-text-field
                v-model="confirmPassword"
                :rules="confirmPasswordRules"
                label="Confirm New Password"
                prepend-icon="mdi-lock-check"
                type="password"
                required
                :disabled="loading"
                @keyup.enter="changePassword"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="secondary"
              :disabled="loading"
              @click="$router.push('/')"
              v-if="!forced"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              :disabled="!valid || loading"
              :loading="loading"
              @click="changePassword"
            >
              Change Password
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PasswordChange',
  data() {
    return {
      valid: true,
      currentPassword: '',
      currentPasswordRules: [
        v => !!v || 'Current password is required',
      ],
      newPassword: '',
      newPasswordRules: [
        v => !!v || 'New password is required',
        v => (v && v.length >= 8) || 'Password must be at least 8 characters',
        v => (v && v !== this.currentPassword) || 'New password must be different from current password',
      ],
      confirmPassword: '',
      confirmPasswordRules: [
        v => !!v || 'Please confirm your password',
        v => v === this.newPassword || 'Passwords do not match',
      ],
      error: null,
      success: null,
      loading: false,
      forced: false,
    };
  },
  created() {
    // Check if this is a forced password change
    this.forced = this.$route.query.forced === 'true';
  },
  methods: {
    async changePassword() {
      if (this.$refs.form.validate()) {
        try {
          this.loading = true;
          this.error = null;
          this.success = null;
          
          // Call the API password change endpoint
          await axios.post('/api/auth/change-password', {
            current_password: this.currentPassword,
            new_password: this.newPassword,
          }, {
            headers: {
              'Authorization': `Bearer ${this.$store.state.auth.token}`
            }
          });
          
          // Update the user info to indicate password has been changed
          this.$store.commit('auth/SET_PASSWORD_CHANGED');
          
          this.success = 'Password successfully changed!';
          
          // After a brief delay, redirect to the dashboard
          setTimeout(() => {
            this.$router.push('/');
          }, 2000);
        } catch (error) {
          console.error('Password change error:', error);
          this.error = error.response?.data?.detail || 'Failed to change password. Please try again.';
        } finally {
          this.loading = false;
        }
      }
    },
  },
};
</script>
