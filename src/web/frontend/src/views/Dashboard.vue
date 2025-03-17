<template>
  <div class="dashboard">
    <h1 class="text-h4 mb-4">Dashboard</h1>

    <v-row>
      <!-- System Overview -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-server</v-icon>
            System Overview
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <div class="text-subtitle-1">Docker Version</div>
                <div class="text-body-1">20.10.23</div>
              </v-col>
              <v-col cols="6">
                <div class="text-subtitle-1">API Version</div>
                <div class="text-body-1">1.41</div>
              </v-col>
              <v-col cols="6">
                <div class="text-subtitle-1">OS/Arch</div>
                <div class="text-body-1">linux/amd64</div>
              </v-col>
              <v-col cols="6">
                <div class="text-subtitle-1">Kernel Version</div>
                <div class="text-body-1">5.15.0-76-generic</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Resource Usage -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-chart-line</v-icon>
            Resource Usage
          </v-card-title>
          <v-card-text>
            <div class="mb-2">
              <div class="d-flex justify-space-between align-center">
                <span>CPU Usage</span>
                <span>45%</span>
              </div>
              <v-progress-linear
                color="primary"
                height="10"
                rounded
                value="45"
              ></v-progress-linear>
            </div>
            <div class="mb-2">
              <div class="d-flex justify-space-between align-center">
                <span>Memory Usage</span>
                <span>2.1 GB / 8 GB</span>
              </div>
              <v-progress-linear
                color="info"
                height="10"
                rounded
                value="26"
              ></v-progress-linear>
            </div>
            <div>
              <div class="d-flex justify-space-between align-center">
                <span>Disk Usage</span>
                <span>15.4 GB / 50 GB</span>
              </div>
              <v-progress-linear
                color="success"
                height="10"
                rounded
                value="31"
              ></v-progress-linear>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- Container Status -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-docker</v-icon>
            Container Status
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="4" class="text-center">
                <v-avatar color="success" size="48" class="mb-2">
                  <span class="text-h6 white--text">5</span>
                </v-avatar>
                <div>Running</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <v-avatar color="warning" size="48" class="mb-2">
                  <span class="text-h6 white--text">2</span>
                </v-avatar>
                <div>Paused</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <v-avatar color="error" size="48" class="mb-2">
                  <span class="text-h6 white--text">3</span>
                </v-avatar>
                <div>Stopped</div>
              </v-col>
            </v-row>
            <v-btn
              color="primary"
              block
              class="mt-4"
              to="/containers"
              >View All Containers</v-btn
            >
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Activity -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-history</v-icon>
            Recent Activity
          </v-card-title>
          <v-list dense>
            <v-list-item v-for="(activity, i) in recentActivities" :key="i">
              <v-list-item-icon>
                <v-icon :color="activity.color">{{ activity.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>{{ activity.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ activity.time }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <!-- Quick Actions -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-lightning-bolt</v-icon>
            Quick Actions
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6" sm="3">
                <v-btn block color="primary" to="/containers/create">
                  <v-icon left>mdi-plus</v-icon>
                  New Container
                </v-btn>
              </v-col>
              <v-col cols="6" sm="3">
                <v-btn block color="info" to="/images/pull">
                  <v-icon left>mdi-download</v-icon>
                  Pull Image
                </v-btn>
              </v-col>
              <v-col cols="6" sm="3">
                <v-btn block color="success" to="/backup/create">
                  <v-icon left>mdi-backup-restore</v-icon>
                  Create Backup
                </v-btn>
              </v-col>
              <v-col cols="6" sm="3">
                <v-btn block color="warning" to="/security/scan">
                  <v-icon left>mdi-shield-search</v-icon>
                  Security Scan
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      recentActivities: [
        {
          icon: 'mdi-play',
          color: 'success',
          title: 'Container nginx started',
          time: '5 minutes ago',
        },
        {
          icon: 'mdi-stop',
          color: 'error',
          title: 'Container redis stopped',
          time: '10 minutes ago',
        },
        {
          icon: 'mdi-download',
          color: 'info',
          title: 'Image postgres:latest pulled',
          time: '15 minutes ago',
        },
        {
          icon: 'mdi-shield',
          color: 'warning',
          title: 'Security scan completed',
          time: '30 minutes ago',
        },
        {
          icon: 'mdi-backup-restore',
          color: 'success',
          title: 'Backup created',
          time: '1 hour ago',
        },
      ],
    };
  },
};
</script>

<style scoped>
.dashboard {
  padding: 16px;
}
</style>
