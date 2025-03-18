<template>
  <div class="chat-commands">
    <v-card outlined class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon left small>mdi-lightning-bolt</v-icon>
        Command Shortcuts
        <v-spacer></v-spacer>
        <v-btn 
          x-small
          icon
          @click="showCreateDialog = true"
          title="Create new shortcut"
        >
          <v-icon small>mdi-plus</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-list dense>
        <v-list-item
          v-for="shortcut in shortcuts"
          :key="shortcut.id"
          @click="useShortcut(shortcut)"
          dense
        >
          <v-list-item-icon class="mr-2">
            <v-icon small>mdi-slash-forward</v-icon>
          </v-list-item-icon>
          
          <v-list-item-content>
            <v-list-item-title class="text-body-2">{{ shortcut.command }}</v-list-item-title>
            <v-list-item-subtitle class="text-caption">{{ shortcut.description }}</v-list-item-subtitle>
          </v-list-item-content>
          
          <v-list-item-action>
            <v-btn 
              icon
              x-small
              @click.stop="confirmDeleteShortcut(shortcut)"
              title="Delete shortcut"
            >
              <v-icon x-small>mdi-delete</v-icon>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
        
        <v-list-item v-if="shortcuts.length === 0">
          <v-list-item-content>
            <v-list-item-subtitle class="text-center">
              No command shortcuts yet. Create your first one!
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
    
    <!-- Create Shortcut Dialog -->
    <v-dialog
      v-model="showCreateDialog"
      max-width="500"
    >
      <v-card>
        <v-card-title>Create Command Shortcut</v-card-title>
        <v-card-text>
          <v-form ref="shortcutForm" v-model="formValid">
            <v-text-field
              v-model="newShortcut.command"
              label="Command (e.g., /logs)"
              :rules="[
                v => !!v || 'Command is required',
                v => v.startsWith('/') || 'Command must start with /',
                v => v.length >= 2 || 'Command must be at least 2 characters'
              ]"
              prefix="/"
              hint="Short command that will expand to the template"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="newShortcut.description"
              label="Description"
              :rules="[v => !!v || 'Description is required']"
              hint="What this command does"
              required
            ></v-text-field>
            
            <v-textarea
              v-model="newShortcut.template"
              label="Template"
              :rules="[v => !!v || 'Template is required']"
              hint="The expanded text when command is used"
              rows="3"
              required
            ></v-textarea>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            text 
            @click="showCreateDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn 
            color="primary" 
            :disabled="!formValid || creating"
            @click="createShortcut"
          >
            Create
            <v-progress-circular
              v-if="creating"
              indeterminate
              size="16"
              class="ml-2"
            ></v-progress-circular>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteDialog"
      max-width="400"
    >
      <v-card>
        <v-card-title>Delete Shortcut</v-card-title>
        <v-card-text>
          Are you sure you want to delete the shortcut 
          <strong>{{ shortcutToDelete ? shortcutToDelete.command : '' }}</strong>?
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            text 
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn 
            color="error" 
            :loading="deleting"
            @click="deleteShortcut"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'ChatCommands',
  
  data() {
    return {
      showCreateDialog: false,
      showDeleteDialog: false,
      shortcutToDelete: null,
      formValid: false,
      creating: false,
      deleting: false,
      newShortcut: {
        command: '',
        description: '',
        template: ''
      }
    };
  },
  
  computed: {
    ...mapState('chat', ['commandShortcuts']),
    
    shortcuts() {
      return this.commandShortcuts || [];
    }
  },
  
  methods: {
    ...mapActions('chat', [
      'loadCommandShortcuts',
      'createCommandShortcut',
      'deleteCommandShortcut',
      'useCommandShortcut'
    ]),
    
    async createShortcut() {
      if (!this.formValid) return;
      
      this.creating = true;
      
      try {
        // Remove leading slash if present
        let command = this.newShortcut.command;
        if (command.startsWith('/')) {
          command = command.substring(1);
        }
        
        await this.createCommandShortcut({
          command,
          description: this.newShortcut.description,
          template: this.newShortcut.template
        });
        
        // Reset form
        this.newShortcut = {
          command: '',
          description: '',
          template: ''
        };
        
        if (this.$refs.shortcutForm) {
          this.$refs.shortcutForm.reset();
        }
        
        // Close dialog
        this.showCreateDialog = false;
        
        // Show success notification
        this.$emit('notification', {
          type: 'success',
          message: 'Command shortcut created successfully'
        });
      } catch (error) {
        console.error('Error creating shortcut:', error);
        
        // Show error notification
        this.$emit('notification', {
          type: 'error',
          message: 'Failed to create command shortcut'
        });
      } finally {
        this.creating = false;
      }
    },
    
    confirmDeleteShortcut(shortcut) {
      this.shortcutToDelete = shortcut;
      this.showDeleteDialog = true;
    },
    
    async deleteShortcut() {
      if (!this.shortcutToDelete) return;
      
      this.deleting = true;
      
      try {
        await this.deleteCommandShortcut(this.shortcutToDelete.id);
        
        // Close dialog
        this.showDeleteDialog = false;
        this.shortcutToDelete = null;
        
        // Show success notification
        this.$emit('notification', {
          type: 'success',
          message: 'Command shortcut deleted successfully'
        });
      } catch (error) {
        console.error('Error deleting shortcut:', error);
        
        // Show error notification
        this.$emit('notification', {
          type: 'error',
          message: 'Failed to delete command shortcut'
        });
      } finally {
        this.deleting = false;
      }
    },
    
    useShortcut(shortcut) {
      this.$emit('use-shortcut', shortcut);
    }
  },
  
  created() {
    // Load shortcuts when component is created
    this.loadCommandShortcuts();
  }
};
</script>

<style scoped>
.chat-commands {
  margin-bottom: 16px;
}
</style>
