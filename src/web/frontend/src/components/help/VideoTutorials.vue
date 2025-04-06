<template>
  <div class="video-tutorials">
    <h2 class="headline mb-3">Video Tutorials</h2>
    
    <v-row>
      <v-col
        v-for="(tutorial, i) in tutorials"
        :key="i"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card outlined class="tutorial-card">
          <v-img
            :src="tutorial.thumbnail"
            height="180"
            class="grey lighten-4"
            @click="playVideo(tutorial)"
          >
            <template v-slot:placeholder>
              <v-row
                class="fill-height ma-0"
                align="center"
                justify="center"
              >
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
              </v-row>
            </template>
            
            <div class="play-button">
              <v-btn
                icon
                x-large
                color="white"
                @click.stop="playVideo(tutorial)"
              >
                <v-icon large>mdi-play</v-icon>
              </v-btn>
            </div>
            
            <div class="video-duration">
              {{ tutorial.duration }}
            </div>
          </v-img>
          
          <v-card-title class="subtitle-1">
            {{ tutorial.title }}
          </v-card-title>
          
          <v-card-subtitle>
            {{ tutorial.description }}
          </v-card-subtitle>
          
          <v-card-actions>
            <v-chip
              small
              outlined
              class="mr-1"
            >
              {{ tutorial.category }}
            </v-chip>
            
            <v-spacer></v-spacer>
            
            <v-btn
              text
              color="primary"
              @click="playVideo(tutorial)"
            >
              <v-icon left>mdi-play</v-icon>
              Watch
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <v-dialog
      v-model="videoDialog"
      max-width="800"
      persistent
    >
      <v-card>
        <v-card-title class="headline">
          {{ selectedVideo ? selectedVideo.title : '' }}
          <v-spacer></v-spacer>
          <v-btn icon @click="videoDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <div v-if="selectedVideo" class="video-container">
            <iframe
              :src="getEmbedUrl(selectedVideo.url)"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
              class="video-iframe"
            ></iframe>
          </div>
          
          <div v-if="selectedVideo" class="mt-4">
            <p>{{ selectedVideo.description }}</p>
            
            <v-divider class="my-3"></v-divider>
            
            <div v-if="selectedVideo.chapters && selectedVideo.chapters.length">
              <h3 class="subtitle-1 font-weight-bold mb-2">Chapters</h3>
              <v-list dense>
                <v-list-item
                  v-for="(chapter, i) in selectedVideo.chapters"
                  :key="i"
                >
                  <v-list-item-icon>
                    <v-icon small>mdi-clock-time-four-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ chapter.title }}</v-list-item-title>
                  </v-list-item-content>
                  <v-list-item-action>
                    {{ chapter.timestamp }}
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'VideoTutorials',
  data() {
    return {
      videoDialog: false,
      selectedVideo: null,
      tutorials: [
        {
          id: 1,
          title: 'Getting Started with DockerForge',
          description: 'Learn the basics of DockerForge and how to navigate the interface.',
          thumbnail: '/img/tutorials/getting-started.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '5:32',
          category: 'Beginner',
          chapters: [
            { title: 'Introduction', timestamp: '0:00' },
            { title: 'Dashboard Overview', timestamp: '0:45' },
            { title: 'Navigation Menu', timestamp: '1:30' },
            { title: 'Quick Actions', timestamp: '2:15' },
            { title: 'User Settings', timestamp: '3:00' },
            { title: 'Help Resources', timestamp: '4:00' }
          ]
        },
        {
          id: 2,
          title: 'Container Management',
          description: 'Learn how to create, start, stop, and manage Docker containers.',
          thumbnail: '/img/tutorials/container-management.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '8:15',
          category: 'Intermediate',
          chapters: [
            { title: 'Container Basics', timestamp: '0:00' },
            { title: 'Creating Containers', timestamp: '1:20' },
            { title: 'Container Lifecycle', timestamp: '3:45' },
            { title: 'Viewing Logs', timestamp: '5:10' },
            { title: 'Using Terminal', timestamp: '6:30' }
          ]
        },
        {
          id: 3,
          title: 'Working with Images',
          description: 'Learn how to pull, build, and manage Docker images.',
          thumbnail: '/img/tutorials/image-management.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '7:45',
          category: 'Intermediate',
          chapters: [
            { title: 'Image Basics', timestamp: '0:00' },
            { title: 'Pulling Images', timestamp: '1:15' },
            { title: 'Building Images', timestamp: '3:00' },
            { title: 'Image Tags', timestamp: '5:30' },
            { title: 'Image Cleanup', timestamp: '6:45' }
          ]
        },
        {
          id: 4,
          title: 'Security Scanning',
          description: 'Learn how to scan containers and images for vulnerabilities.',
          thumbnail: '/img/tutorials/security-scanning.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '6:20',
          category: 'Advanced',
          chapters: [
            { title: 'Security Overview', timestamp: '0:00' },
            { title: 'Scanning Images', timestamp: '1:30' },
            { title: 'Understanding Results', timestamp: '3:15' },
            { title: 'Remediation', timestamp: '4:45' }
          ]
        },
        {
          id: 5,
          title: 'Docker Compose Projects',
          description: 'Learn how to manage multi-container applications with Docker Compose.',
          thumbnail: '/img/tutorials/compose-projects.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '9:10',
          category: 'Advanced',
          chapters: [
            { title: 'Compose Basics', timestamp: '0:00' },
            { title: 'Creating Projects', timestamp: '1:45' },
            { title: 'Managing Services', timestamp: '4:00' },
            { title: 'Scaling Services', timestamp: '6:30' },
            { title: 'Compose Networks', timestamp: '8:00' }
          ]
        },
        {
          id: 6,
          title: 'Using the AI Assistant',
          description: 'Learn how to use the AI Chat Assistant for Docker management.',
          thumbnail: '/img/tutorials/ai-assistant.jpg',
          url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          duration: '4:55',
          category: 'Beginner',
          chapters: [
            { title: 'Assistant Overview', timestamp: '0:00' },
            { title: 'Asking Questions', timestamp: '1:00' },
            { title: 'Using Commands', timestamp: '2:15' },
            { title: 'Advanced Features', timestamp: '3:30' }
          ]
        }
      ]
    };
  },
  methods: {
    playVideo(tutorial) {
      this.selectedVideo = tutorial;
      this.videoDialog = true;
    },
    getEmbedUrl(url) {
      // Handle different video platforms
      if (url.includes('youtube.com/embed/')) {
        return url;
      } else if (url.includes('youtube.com/watch')) {
        const videoId = new URL(url).searchParams.get('v');
        return `https://www.youtube.com/embed/${videoId}`;
      } else if (url.includes('vimeo.com')) {
        const videoId = url.split('/').pop();
        return `https://player.vimeo.com/video/${videoId}`;
      }
      return url;
    }
  }
};
</script>

<style scoped>
.video-tutorials {
  max-width: 1200px;
  margin: 0 auto;
}

.tutorial-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.8;
  transition: opacity 0.2s ease;
}

.v-img:hover .play-button {
  opacity: 1;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8rem;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
