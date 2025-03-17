const app = Vue.createApp({
  data() {
    return {
      message: 'Welcome to DockerForge Web UI',
      loading: false,
      error: null,
      darkMode: false,
    };
  },
  methods: {
    toggleDarkMode() {
      document.body.classList.toggle('dark-mode', this.darkMode);
    },
  },
  mounted() {
    console.log('Vue app mounted');
  },
});

app.mount('#app');
