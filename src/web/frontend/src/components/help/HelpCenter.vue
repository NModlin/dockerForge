<template>
  <v-card class="help-center" outlined>
    <v-card-title class="primary white--text">
      <v-icon left color="white">mdi-help-circle</v-icon>
      Help Center
      <v-spacer></v-spacer>
      <v-btn icon @click="$emit('close')" class="white--text">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <v-tabs v-model="activeTab" background-color="transparent" grow>
        <v-tab v-for="tab in tabs" :key="tab.id">
          <v-icon left>{{ tab.icon }}</v-icon>
          {{ tab.title }}
        </v-tab>
      </v-tabs>
      
      <v-divider></v-divider>
      
      <v-tabs-items v-model="activeTab" class="mt-3">
        <v-tab-item v-for="tab in tabs" :key="tab.id">
          <component :is="tab.component" :category="tab.id"></component>
        </v-tab-item>
      </v-tabs-items>
    </v-card-text>
  </v-card>
</template>

<script>
import ChatHelp from './ChatHelp.vue';
import AgentHelp from './AgentHelp.vue';
import CommandReference from './CommandReference.vue';
import GeneralHelp from './GeneralHelp.vue';

export default {
  name: 'HelpCenter',
  components: {
    ChatHelp,
    AgentHelp,
    CommandReference,
    GeneralHelp
  },
  data() {
    return {
      activeTab: 0,
      tabs: [
        {
          id: 'general',
          title: 'General',
          icon: 'mdi-information-outline',
          component: 'GeneralHelp'
        },
        {
          id: 'chat',
          title: 'Chat Interface',
          icon: 'mdi-message-text',
          component: 'ChatHelp'
        },
        {
          id: 'agents',
          title: 'Agent System',
          icon: 'mdi-robot',
          component: 'AgentHelp'
        },
        {
          id: 'commands',
          title: 'Commands',
          icon: 'mdi-console',
          component: 'CommandReference'
        }
      ]
    };
  }
};
</script>

<style scoped>
.help-center {
  max-width: 900px;
  margin: auto;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.v-card-text {
  flex-grow: 1;
  overflow-y: auto;
}

.v-tabs-items {
  min-height: 400px;
}
</style>
