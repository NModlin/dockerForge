<template>
  <div class="keyboard-shortcuts-guide">
    <h2 class="headline mb-3">Keyboard Shortcuts</h2>
    
    <v-card outlined>
      <v-card-text>
        <p class="mb-4">DockerForge provides keyboard shortcuts to help you work more efficiently.</p>
        
        <v-simple-table>
          <template v-slot:default>
            <thead>
              <tr>
                <th>Shortcut</th>
                <th>Action</th>
                <th>Available In</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(shortcut, i) in shortcuts" :key="i">
                <td>
                  <div class="d-flex align-center">
                    <template v-for="(key, j) in shortcut.keys">
                      <kbd :key="'key-'+j">{{ key }}</kbd>
                      <span v-if="j < shortcut.keys.length - 1" :key="'plus-'+j" class="mx-1">+</span>
                    </template>
                  </div>
                </td>
                <td>{{ shortcut.action }}</td>
                <td>{{ shortcut.context }}</td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'KeyboardShortcutsGuide',
  data() {
    return {
      shortcuts: [
        {
          keys: ['?'],
          action: 'Show keyboard shortcuts',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'F'],
          action: 'Open search',
          context: 'Global'
        },
        {
          keys: ['Ctrl', '/'],
          action: 'Toggle chat panel',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'H'],
          action: 'Open help center',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'D'],
          action: 'Go to dashboard',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'C'],
          action: 'Go to containers',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'I'],
          action: 'Go to images',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'S'],
          action: 'Go to security',
          context: 'Global'
        },
        {
          keys: ['Ctrl', 'R'],
          action: 'Refresh current view',
          context: 'Global'
        },
        {
          keys: ['F1'],
          action: 'Show contextual help',
          context: 'Global'
        },
        {
          keys: ['Esc'],
          action: 'Close dialogs/panels',
          context: 'Global'
        },
        // Container-specific shortcuts
        {
          keys: ['S'],
          action: 'Start container',
          context: 'Container List'
        },
        {
          keys: ['P'],
          action: 'Stop container',
          context: 'Container List'
        },
        {
          keys: ['R'],
          action: 'Restart container',
          context: 'Container List'
        },
        {
          keys: ['L'],
          action: 'View logs',
          context: 'Container List'
        },
        {
          keys: ['T'],
          action: 'Open terminal',
          context: 'Container List'
        },
        {
          keys: ['D'],
          action: 'Delete container',
          context: 'Container List'
        },
        // Image-specific shortcuts
        {
          keys: ['P'],
          action: 'Pull image',
          context: 'Image List'
        },
        {
          keys: ['B'],
          action: 'Build image',
          context: 'Image List'
        },
        {
          keys: ['S'],
          action: 'Scan image',
          context: 'Image List'
        },
        {
          keys: ['D'],
          action: 'Delete image',
          context: 'Image List'
        },
        // Terminal shortcuts
        {
          keys: ['Ctrl', 'C'],
          action: 'Interrupt process',
          context: 'Terminal'
        },
        {
          keys: ['Ctrl', 'L'],
          action: 'Clear terminal',
          context: 'Terminal'
        },
        {
          keys: ['Ctrl', 'D'],
          action: 'Exit terminal',
          context: 'Terminal'
        },
        // Log viewer shortcuts
        {
          keys: ['F'],
          action: 'Toggle follow logs',
          context: 'Log Viewer'
        },
        {
          keys: ['Ctrl', 'F'],
          action: 'Search logs',
          context: 'Log Viewer'
        },
        {
          keys: ['C'],
          action: 'Clear logs',
          context: 'Log Viewer'
        }
      ]
    };
  }
};
</script>

<style scoped>
.keyboard-shortcuts-guide {
  max-width: 800px;
  margin: 0 auto;
}

kbd {
  display: inline-block;
  padding: 3px 6px;
  font-family: monospace;
  line-height: 1.4;
  color: #444;
  background-color: #f7f7f7;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}
</style>
