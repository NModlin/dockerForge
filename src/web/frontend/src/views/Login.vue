<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>DockerForge Login</v-toolbar-title>
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
            <v-form ref="form" v-model="valid" lazy-validation @submit.prevent="login">
              <v-text-field
                v-model="username"
                :rules="usernameRules"
                label="Username"
                prepend-icon="mdi-account"
                required
                :disabled="loading"
              ></v-text-field>

              <v-text-field
                v-model="password"
                :rules="passwordRules"
                label="Password"
                prepend-icon="mdi-lock"
                type="password"
                required
                :disabled="loading"
                @keyup.enter="login"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              :disabled="!valid || loading"
              :loading="loading"
              @click="login"
            >
              Login
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
  name: 'Login',
  data() {
    return {
      valid: true,
      username: '',
      usernameRules: [
        v => !!v || 'Username is required',
      ],
      password: '',
      passwordRules: [
        v => !!v || 'Password is required',
      ],
      error: null,
      loading: false,
    };
  },
  methods: {
    async login() {
      if (this.$refs.form.validate()) {
        try {
          this.loading = true;
          this.error = null;
          
          // Create form data for OAuth2 password flow
          const formData = new FormData();
          formData.append('username', this.username);
          formData.append('password', this.password);
          
          // Call the API login endpoint
          const response = await axios.post('/api/auth/token', formData);
          
          // Store the token and user info
          this.$store.dispatch('auth/login', {
            token: response.data.access_token,
            user: {
              username: this.username,
              password_change_required: response.data.password_change_required
            },
          });
          
          // Check if password change is required
          if (response.data.password_change_required) {
            // Redirect to password change page with the forced parameter
            this.$router.push({ path: '/change-password', query: { forced: 'true' } });
          } else {
            // Redirect to dashboard
            this.$router.push('/');
          }
        } catch (error) {
          console.error('Login error:', error);
          this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.';
        } finally {
          this.loading = false;
        }
      }
    },
  },
};
</script>
