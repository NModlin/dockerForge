/**
 * Vue CLI configuration for DockerForge WebUI
 */
const path = require('path');

module.exports = {
  // Output directory for production build
  outputDir: path.resolve(__dirname, '../../static'),

  // Where to place static assets
  assetsDir: '',

  // Path for static assets in production
  publicPath: '/',

  // Development server configuration
  devServer: {
    port: 8080,
    // Proxy API requests to backend during development
    proxy: {
      '^/api': {
        target: 'http://localhost:54321',
        changeOrigin: true
      },
      '^/ws': {
        target: 'ws://localhost:54321',
        changeOrigin: true,
        ws: true
      }
    }
  },

  // Configure webpack
  configureWebpack: {
    // Performance hints
    performance: {
      hints: process.env.NODE_ENV === 'production' ? 'warning' : false
    },
    // Source maps configuration
    devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'eval-source-map',
    // Resolve paths
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },

  // CSS configuration
  css: {
    sourceMap: true
  },

  // Chain webpack configuration
  chainWebpack: config => {
    // Handle SCSS variables globally
    const types = ['vue-modules', 'vue', 'normal-modules', 'normal'];
    types.forEach(type => {
      addStyleResource(config.module.rule('scss').oneOf(type));
    });
  }
};

// Helper function to add style resources
function addStyleResource(rule) {
  rule.use('style-resource')
    .loader('style-resources-loader')
    .options({
      // Add global SCSS variables here if needed
      // patterns: [path.resolve(__dirname, 'src/styles/variables.scss')]
    });
}
