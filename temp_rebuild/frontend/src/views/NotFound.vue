<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-card class="pa-6">
          <v-card-title class="text-h3 justify-center">
            404
          </v-card-title>
          <v-card-subtitle class="text-h5 mt-2">
            Page Not Found
          </v-card-subtitle>
          <v-card-text>
            <p class="text-body-1">
              The page you are looking for does not exist or has been moved.
            </p>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn color="primary" to="/">
              <v-icon left>mdi-home</v-icon>
              Go to Dashboard
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'NotFound',
};
</script>
