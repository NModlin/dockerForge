<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>DockerForge</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-bell</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-account</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" app>
      <v-list>
        <v-list-item to="/" link>
          <v-list-item-icon>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/containers" link>
          <v-list-item-icon>
            <v-icon>mdi-docker</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Containers</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/images" link>
          <v-list-item-icon>
            <v-icon>mdi-package-variant-closed</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Images</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/volumes" link>
          <v-list-item-icon>
            <v-icon>mdi-database</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Volumes</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/networks" link>
          <v-list-item-icon>
            <v-icon>mdi-lan</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Networks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/compose" link>
          <v-list-item-icon>
            <v-icon>mdi-file-document-multiple</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Compose</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/security" link>
          <v-list-item-icon>
            <v-icon>mdi-shield</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Security</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/backup" link>
          <v-list-item-icon>
            <v-icon>mdi-backup-restore</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Backup</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/monitoring" link>
          <v-list-item-icon>
            <v-icon>mdi-chart-line</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Monitoring</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/settings" link>
          <v-list-item-icon>
            <v-icon>mdi-cog</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} DockerForge</span>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      drawer: true,
    };
  },
};
</script>

<style>
/* Global styles */
</style>
