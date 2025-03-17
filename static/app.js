const app = Vue.createApp({
  data() {
    return {
      message: 'Welcome to DockerForge Web UI',
      loading: false,
      error: null,
      darkMode: false,
      isAuthenticated: false,
      token: null,
      user: null,
      passwordChangeRequired: false,
      aiProviders: {},
      defaultProvider: '',
      aiUsage: null,
      activeForm: null,
      loginForm: {
        username: '',
        password: '',
        error: null,
        loading: false
      },
      passwordChangeForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        error: null,
        loading: false
      },
      passwordResetForm: {
        username: '',
        error: null,
        loading: false,
        step: 1, // 1: username, 2: local auth, 3: new password
        localUsername: '',
        localPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      containerAnalysis: {
        containerId: '',
        confirmCost: true,
        result: null,
        loading: false,
        error: null
      },
      logAnalysis: {
        logs: '',
        confirmCost: true,
        result: null,
        loading: false,
        error: null
      },
      composeAnalysis: {
        content: '',
        confirmCost: true,
        result: null,
        loading: false,
        error: null
      },
      dockerfileAnalysis: {
        content: '',
        confirmCost: true,
        result: null,
        loading: false,
        error: null
      }
    };
  },
  methods: {
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      document.body.classList.toggle('dark-mode', this.darkMode);
    },
    
    // Authentication Methods
    async login() {
      try {
        this.loginForm.loading = true;
        this.loginForm.error = null;
        
        const formData = new FormData();
        formData.append('username', this.loginForm.username);
        formData.append('password', this.loginForm.password);
        
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Login failed');
        }
        
        const data = await response.json();
        this.token = data.access_token;
        this.isAuthenticated = true;
        this.passwordChangeRequired = data.password_change_required;
        
        // Store token in localStorage
        localStorage.setItem('token', this.token);
        localStorage.setItem('passwordChangeRequired', this.passwordChangeRequired);
        
        // Close login modal
        this.closeModal();
        
        // If password change is required, show password change form
        if (this.passwordChangeRequired) {
          this.showPasswordChangeForm();
        } else {
          // Fetch user info
          await this.fetchUserInfo();
        }
      } catch (error) {
        console.error('Login error:', error);
        this.loginForm.error = error.message;
      } finally {
        this.loginForm.loading = false;
      }
    },
    
    async logout() {
      // Clear auth state
      this.isAuthenticated = false;
      this.token = null;
      this.user = null;
      
      // Remove from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('passwordChangeRequired');
      
      // Call logout endpoint (optional, since JWT is stateless)
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
      
      // Redirect to login
      this.showLoginForm();
    },
    
    async fetchUserInfo() {
      try {
        const response = await fetch('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch user info');
        }
        
        this.user = await response.json();
      } catch (error) {
        console.error('Error fetching user info:', error);
        // If we can't get user info, logout
        this.logout();
      }
    },
    
    async changePassword() {
      try {
        this.passwordChangeForm.loading = true;
        this.passwordChangeForm.error = null;
        
        // Validate passwords match
        if (this.passwordChangeForm.newPassword !== this.passwordChangeForm.confirmPassword) {
          throw new Error('New passwords do not match');
        }
        
        const response = await fetch('/api/auth/change-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
          },
          body: JSON.stringify({
            current_password: this.passwordChangeForm.currentPassword,
            new_password: this.passwordChangeForm.newPassword
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Password change failed');
        }
        
        // Update password change required flag
        this.passwordChangeRequired = false;
        localStorage.setItem('passwordChangeRequired', 'false');
        
        // Close modal
        this.closeModal();
        
        // Show success message
        alert('Password changed successfully');
        
        // Fetch user info
        await this.fetchUserInfo();
      } catch (error) {
        console.error('Password change error:', error);
        this.passwordChangeForm.error = error.message;
      } finally {
        this.passwordChangeForm.loading = false;
      }
    },
    
    async requestPasswordReset() {
      try {
        this.passwordResetForm.loading = true;
        this.passwordResetForm.error = null;
        
        const response = await fetch('/api/auth/reset-password-request', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.passwordResetForm.username
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Password reset request failed');
        }
        
        // Move to next step
        this.passwordResetForm.step = 2;
      } catch (error) {
        console.error('Password reset request error:', error);
        this.passwordResetForm.error = error.message;
      } finally {
        this.passwordResetForm.loading = false;
      }
    },
    
    async verifyAndResetPassword() {
      try {
        this.passwordResetForm.loading = true;
        this.passwordResetForm.error = null;
        
        // Validate passwords match
        if (this.passwordResetForm.newPassword !== this.passwordResetForm.confirmPassword) {
          throw new Error('New passwords do not match');
        }
        
        const response = await fetch('/api/auth/reset-password-verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.passwordResetForm.username,
            local_username: this.passwordResetForm.localUsername,
            local_password: this.passwordResetForm.localPassword,
            new_password: this.passwordResetForm.newPassword
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Password reset failed');
        }
        
        // Close modal
        this.closeModal();
        
        // Show success message
        alert('Password reset successfully. Please login with your new password.');
        
        // Show login form
        this.showLoginForm();
      } catch (error) {
        console.error('Password reset error:', error);
        this.passwordResetForm.error = error.message;
      } finally {
        this.passwordResetForm.loading = false;
      }
    },
    
    // Auth Form Methods
    showLoginForm() {
      this.activeForm = 'login';
      this.loginForm.username = '';
      this.loginForm.password = '';
      this.loginForm.error = null;
      
      this.showModal(`
        <h3>Login</h3>
        <form id="login-form" @submit.prevent="login">
          <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" v-model="loginForm.username" required>
          </div>
          <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" v-model="loginForm.password" required>
          </div>
          <div v-if="loginForm.error" class="error-message">
            <p>{{ loginForm.error }}</p>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-link" @click="showPasswordResetForm">Forgot Password?</button>
            <button type="submit" class="btn btn-primary" :disabled="loginForm.loading">
              {{ loginForm.loading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </form>
      `);
    },
    
    showPasswordChangeForm() {
      this.activeForm = 'passwordChange';
      this.passwordChangeForm.currentPassword = '';
      this.passwordChangeForm.newPassword = '';
      this.passwordChangeForm.confirmPassword = '';
      this.passwordChangeForm.error = null;
      
      this.showModal(`
        <h3>Change Password</h3>
        <p>You must change your password before continuing.</p>
        <form id="password-change-form" @submit.prevent="changePassword">
          <div class="form-group">
            <label for="current-password">Current Password:</label>
            <input type="password" id="current-password" v-model="passwordChangeForm.currentPassword" required>
          </div>
          <div class="form-group">
            <label for="new-password">New Password:</label>
            <input type="password" id="new-password" v-model="passwordChangeForm.newPassword" required>
          </div>
          <div class="form-group">
            <label for="confirm-password">Confirm New Password:</label>
            <input type="password" id="confirm-password" v-model="passwordChangeForm.confirmPassword" required>
          </div>
          <div v-if="passwordChangeForm.error" class="error-message">
            <p>{{ passwordChangeForm.error }}</p>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="passwordChangeForm.loading">
              {{ passwordChangeForm.loading ? 'Changing Password...' : 'Change Password' }}
            </button>
          </div>
        </form>
      `);
    },
    
    showPasswordResetForm() {
      this.activeForm = 'passwordReset';
      this.passwordResetForm.username = '';
      this.passwordResetForm.localUsername = '';
      this.passwordResetForm.localPassword = '';
      this.passwordResetForm.newPassword = '';
      this.passwordResetForm.confirmPassword = '';
      this.passwordResetForm.error = null;
      this.passwordResetForm.step = 1;
      
      this.showModal(`
        <h3>Reset Password</h3>
        <div v-if="passwordResetForm.step === 1">
          <p>Enter your username to begin the password reset process.</p>
          <form id="password-reset-form-step1" @submit.prevent="requestPasswordReset">
            <div class="form-group">
              <label for="reset-username">Username:</label>
              <input type="text" id="reset-username" v-model="passwordResetForm.username" required>
            </div>
            <div v-if="passwordResetForm.error" class="error-message">
              <p>{{ passwordResetForm.error }}</p>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="showLoginForm">Back to Login</button>
              <button type="submit" class="btn btn-primary" :disabled="passwordResetForm.loading">
                {{ passwordResetForm.loading ? 'Processing...' : 'Continue' }}
              </button>
            </div>
          </form>
        </div>
        
        <div v-if="passwordResetForm.step === 2">
          <p>Please verify your identity using your local system credentials.</p>
          <form id="password-reset-form-step2" @submit.prevent="passwordResetForm.step = 3">
            <div class="form-group">
              <label for="local-username">Local System Username:</label>
              <input type="text" id="local-username" v-model="passwordResetForm.localUsername" required>
            </div>
            <div class="form-group">
              <label for="local-password">Local System Password:</label>
              <input type="password" id="local-password" v-model="passwordResetForm.localPassword" required>
            </div>
            <div v-if="passwordResetForm.error" class="error-message">
              <p>{{ passwordResetForm.error }}</p>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="passwordResetForm.step = 1">Back</button>
              <button type="submit" class="btn btn-primary">Continue</button>
            </div>
          </form>
        </div>
        
        <div v-if="passwordResetForm.step === 3">
          <p>Enter your new password.</p>
          <form id="password-reset-form-step3" @submit.prevent="verifyAndResetPassword">
            <div class="form-group">
              <label for="reset-new-password">New Password:</label>
              <input type="password" id="reset-new-password" v-model="passwordResetForm.newPassword" required>
            </div>
            <div class="form-group">
              <label for="reset-confirm-password">Confirm New Password:</label>
              <input type="password" id="reset-confirm-password" v-model="passwordResetForm.confirmPassword" required>
            </div>
            <div v-if="passwordResetForm.error" class="error-message">
              <p>{{ passwordResetForm.error }}</p>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="passwordResetForm.step = 2">Back</button>
              <button type="submit" class="btn btn-primary" :disabled="passwordResetForm.loading">
                {{ passwordResetForm.loading ? 'Resetting Password...' : 'Reset Password' }}
              </button>
            </div>
          </form>
        </div>
      `);
    },
    
    showModal(content) {
      // Create modal if it doesn't exist
      let modal = document.getElementById('modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal';
        modal.className = 'modal';
        modal.innerHTML = `
          <div class="modal-content">
            <span class="close" onclick="app.closeModal()">&times;</span>
            <div id="modal-body"></div>
          </div>
        `;
        document.body.appendChild(modal);
      }
      
      // Set content and show modal
      document.getElementById('modal-body').innerHTML = content;
      modal.style.display = 'block';
    },
    
    closeModal() {
      const modal = document.getElementById('modal');
      if (modal) {
        modal.style.display = 'none';
      }
      this.activeForm = null;
    },
    
    // AI Provider Status
    async fetchAIStatus() {
      try {
        this.loading = true;
        const response = await fetch('/api/monitoring/ai-status');
        if (!response.ok) {
          throw new Error(`Error fetching AI status: ${response.statusText}`);
        }
        const data = await response.json();
        this.aiProviders = data.providers;
        this.defaultProvider = data.default_provider;
        
        // Update the AI providers display
        this.renderAIProviders();
      } catch (error) {
        console.error('Error fetching AI status:', error);
        document.getElementById('ai-providers').innerHTML = `
          <div class="error-card">
            <h4>Error Loading AI Providers</h4>
            <p>${error.message}</p>
          </div>
        `;
      } finally {
        this.loading = false;
      }
    },
    
    renderAIProviders() {
      const providersElement = document.getElementById('ai-providers');
      if (!providersElement) return;
      
      let html = '<div class="card-container">';
      
      for (const [name, provider] of Object.entries(this.aiProviders)) {
        const statusClass = provider.enabled && provider.available ? 'status-available' : 'status-unavailable';
        const statusText = provider.enabled && provider.available ? 'Available' : 'Unavailable';
        
        html += `
          <div class="card provider-card">
            <div class="provider-header">
              <h4>${name}</h4>
              <span class="provider-status ${statusClass}">${statusText}</span>
              ${name === this.defaultProvider ? '<span class="default-badge">Default</span>' : ''}
            </div>
            <div class="provider-details">
              <p><strong>Type:</strong> ${provider.type}</p>
              ${provider.model ? `<p><strong>Model:</strong> ${provider.model}</p>` : ''}
              ${provider.capabilities ? this.renderCapabilities(provider.capabilities) : ''}
            </div>
          </div>
        `;
      }
      
      html += '</div>';
      providersElement.innerHTML = html;
    },
    
    renderCapabilities(capabilities) {
      let html = '<div class="capabilities">';
      html += '<p><strong>Capabilities:</strong></p>';
      html += '<ul>';
      
      for (const [capability, enabled] of Object.entries(capabilities)) {
        if (enabled) {
          html += `<li>${this.formatCapabilityName(capability)}</li>`;
        }
      }
      
      html += '</ul></div>';
      return html;
    },
    
    formatCapabilityName(name) {
      return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    
    // AI Usage Statistics
    async fetchAIUsage() {
      try {
        this.loading = true;
        const response = await fetch('/api/monitoring/ai-usage');
        if (!response.ok) {
          throw new Error(`Error fetching AI usage: ${response.statusText}`);
        }
        const data = await response.json();
        this.aiUsage = data;
        
        // Update the AI usage display
        this.renderAIUsage();
      } catch (error) {
        console.error('Error fetching AI usage:', error);
        document.getElementById('ai-usage').innerHTML = `
          <div class="error-card">
            <h4>Error Loading AI Usage</h4>
            <p>${error.message}</p>
          </div>
        `;
      } finally {
        this.loading = false;
      }
    },
    
    renderAIUsage() {
      const usageElement = document.getElementById('ai-usage');
      if (!usageElement || !this.aiUsage) return;
      
      let html = '<div class="usage-summary">';
      
      // Budget information
      html += `
        <div class="card budget-card">
          <h4>Monthly Budget</h4>
          <div class="budget-info">
            <div class="budget-meter">
              <div class="budget-progress" style="width: ${this.aiUsage.budget_percentage}%"></div>
            </div>
            <p>
              <strong>Used:</strong> $${this.aiUsage.budget_status.total_usage_usd.toFixed(2)} of 
              $${this.aiUsage.budget_status.total_budget_usd.toFixed(2)}
              (${this.aiUsage.budget_percentage.toFixed(1)}%)
            </p>
            <p><strong>Remaining:</strong> $${this.aiUsage.budget_remaining_usd.toFixed(2)}</p>
            <p><strong>Projected:</strong> $${this.aiUsage.projected_total_usd.toFixed(2)} 
              (${this.aiUsage.projected_percentage.toFixed(1)}% of budget)
            </p>
          </div>
        </div>
      `;
      
      html += '</div>';
      usageElement.innerHTML = html;
    },
    
    // Analysis Methods
    showContainerAnalysisForm() {
      // Implementation will be added later
      alert('Container Analysis feature is coming soon!');
    },
    
    showLogAnalysisForm() {
      // Implementation will be added later
      alert('Log Analysis feature is coming soon!');
    },
    
    showComposeAnalysisForm() {
      // Implementation will be added later
      alert('Docker Compose Analysis feature is coming soon!');
    },
    
    showDockerfileAnalysisForm() {
      // Implementation will be added later
      alert('Dockerfile Analysis feature is coming soon!');
    },
    
    resetAnalysisResults() {
      this.containerAnalysis.result = null;
      this.containerAnalysis.error = null;
      this.logAnalysis.result = null;
      this.logAnalysis.error = null;
      this.composeAnalysis.result = null;
      this.composeAnalysis.error = null;
      this.dockerfileAnalysis.result = null;
      this.dockerfileAnalysis.error = null;
    }
  },
  mounted() {
    console.log('Vue app mounted');
    
    // Check for existing token in localStorage
    const token = localStorage.getItem('token');
    if (token) {
      this.token = token;
      this.isAuthenticated = true;
      
      // Check if password change is required
      const passwordChangeRequired = localStorage.getItem('passwordChangeRequired');
      this.passwordChangeRequired = passwordChangeRequired === 'true';
      
      // If password change is required, show password change form
      if (this.passwordChangeRequired) {
        this.showPasswordChangeForm();
      } else {
        // Fetch user info
        this.fetchUserInfo();
      }
    } else {
      // Show login form
      this.showLoginForm();
    }
    
    // Add CSS for the new components
    const style = document.createElement('style');
    style.textContent = `
      .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 20px;
      }
      .card {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        flex: 1 1 300px;
        min-width: 250px;
      }
      .dark-mode .card {
        background-color: #2d2d2d;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      }
      .provider-card {
        position: relative;
      }
      .provider-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }
      .provider-status {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
      }
      .status-available {
        background-color: #4caf50;
        color: white;
      }
      .status-unavailable {
        background-color: #f44336;
        color: white;
      }
      .default-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #ff9800;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
      }
      .capabilities ul {
        margin: 0;
        padding-left: 20px;
      }
      .budget-card {
        background-color: #e8f5e9;
      }
      .dark-mode .budget-card {
        background-color: #1b5e20;
      }
      .budget-meter {
        height: 10px;
        background-color: #e0e0e0;
        border-radius: 5px;
        margin: 10px 0;
        overflow: hidden;
      }
      .budget-progress {
        height: 100%;
        background-color: #4caf50;
        border-radius: 5px;
      }
      .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
      }
      .modal-content {
        background-color: #fefefe;
        margin: 10% auto;
        padding: 20px;
        border-radius: 8px;
        width: 80%;
        max-width: 800px;
        max-height: 80vh;
        overflow-y: auto;
      }
      .dark-mode .modal-content {
        background-color: #2d2d2d;
        color: white;
      }
      .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
      }
      .close:hover {
        color: #000;
      }
      .dark-mode .close:hover {
        color: #fff;
      }
      .form-group {
        margin-bottom: 15px;
      }
      .form-group label {
        display: block;
        margin-bottom: 5px;
      }
      .form-group input[type="text"],
      .form-group input[type="password"],
      .form-group textarea {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
      }
      .dark-mode .form-group input[type="text"],
      .dark-mode .form-group input[type="password"],
      .dark-mode .form-group textarea {
        background-color: #424242;
        color: white;
        border-color: #666;
      }
      .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 20px;
      }
      .btn-secondary {
        background-color: #9e9e9e;
      }
      .btn-secondary:hover {
        background-color: #757575;
      }
      .btn-link {
        background: none;
        border: none;
        color: #1976d2;
        text-decoration: underline;
        cursor: pointer;
        padding: 0;
      }
      .btn-link:hover {
        color: #1565c0;
        text-decoration: none;
      }
      .loading-indicator {
        text-align: center;
        margin: 20px 0;
      }
      .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
      }
      .dark-mode .error-message {
        background-color: #4a0f0f;
        color: #ffcdd2;
      }
      .analysis-result {
        margin-top: 20px;
      }
      .analysis-content {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 4px;
        overflow-x: auto;
        margin-top: 10px;
      }
      .dark-mode .analysis-content {
        background-color: #424242;
      }
      .analysis-content pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
      }
    `;
    document.head.appendChild(style);
    
    // Fetch AI status and usage
    this.fetchAIStatus();
    this.fetchAIUsage();
  }
});

app.mount('#app');
