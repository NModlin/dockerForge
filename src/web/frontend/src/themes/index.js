// Theme configuration for DockerForge
export const themes = {
  light: {
    dark: false,
    colors: {
      primary: '#007BFF',      // Main blue from light logo
      secondary: '#6C757D',    // Gray
      accent: '#17A2B8',       // Teal accent
      error: '#DC3545',        // Red for errors
      warning: '#FFC107',      // Yellow for warnings
      info: '#17A2B8',         // Teal for info
      success: '#28A745',      // Green for success
      background: '#F8F9FA',   // Light gray background
      surface: '#FFFFFF',      // White surface
      logoPath: '/img/logos/logo-light.svg', // Path to light theme logo
    },
  },
  dark: {
    dark: true,
    colors: {
      primary: '#0D6EFD',      // Brighter blue from dark logo
      secondary: '#6C757D',    // Gray
      accent: '#0DCAF0',       // Bright teal accent
      error: '#DC3545',        // Red for errors
      warning: '#FFC107',      // Yellow for warnings
      info: '#0DCAF0',         // Teal for info
      success: '#198754',      // Green for success
      background: '#212529',   // Dark background
      surface: '#343A40',      // Dark surface
      logoPath: '/img/logos/logo-dark.svg', // Path to dark theme logo
    },
  },
  highContrast: {
    dark: true,
    colors: {
      primary: '#FFFF00',      // Bright yellow from high contrast logo
      secondary: '#FFFFFF',    // White
      accent: '#00FFFF',       // Cyan accent
      error: '#FF0000',        // Pure red for errors
      warning: '#FFFF00',      // Yellow for warnings
      info: '#00FFFF',         // Cyan for info
      success: '#00FF00',      // Green for success
      background: '#000000',   // Black background
      surface: '#0A0A0A',      // Very dark surface
      logoPath: '/img/logos/logo-high-contrast.svg', // Path to high contrast logo
    },
  },
  blue: {
    dark: false,
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      accent: '#82B1FF',
      error: '#FF5252',
      warning: '#FFC107',
      info: '#2196F3',
      success: '#4CAF50',
      background: '#E3F2FD',
      surface: '#FFFFFF',
    },
  },
  green: {
    dark: false,
    colors: {
      primary: '#388E3C',
      secondary: '#424242',
      accent: '#8BC34A',
      error: '#FF5252',
      warning: '#FFC107',
      info: '#2196F3',
      success: '#4CAF50',
      background: '#E8F5E9',
      surface: '#FFFFFF',
    },
  },
  purple: {
    dark: false,
    colors: {
      primary: '#6A1B9A',
      secondary: '#424242',
      accent: '#CE93D8',
      error: '#FF5252',
      warning: '#FFC107',
      info: '#2196F3',
      success: '#4CAF50',
      background: '#F3E5F5',
      surface: '#FFFFFF',
    },
  },
  orange: {
    dark: false,
    colors: {
      primary: '#E65100',
      secondary: '#424242',
      accent: '#FFB74D',
      error: '#FF5252',
      warning: '#FFC107',
      info: '#2196F3',
      success: '#4CAF50',
      background: '#FFF3E0',
      surface: '#FFFFFF',
    },
  },
  red: {
    dark: false,
    colors: {
      primary: '#C62828',
      secondary: '#424242',
      accent: '#FF8A80',
      error: '#FF5252',
      warning: '#FFC107',
      info: '#2196F3',
      success: '#4CAF50',
      background: '#FFEBEE',
      surface: '#FFFFFF',
    },
  },
};

// Function to get system preference for dark/light mode
export function getSystemTheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

// Function to apply theme
export function applyTheme(themeName, vuetify) {
  // If system theme is selected, determine the actual theme
  if (themeName === 'system') {
    themeName = getSystemTheme();
  }

  // Get theme or fallback to light
  const theme = themes[themeName] || themes.light;

  // Apply theme to Vuetify
  if (vuetify && vuetify.theme) {
    // Create theme if it doesn't exist
    if (!vuetify.theme.themes.value[themeName] && themeName !== 'light' && themeName !== 'dark') {
      vuetify.theme.themes.value[themeName] = theme;
    }

    // Set as current theme
    vuetify.theme.global.name.value = themeName;
  }

  // Store theme preference
  localStorage.setItem('theme', themeName);

  // Apply CSS variables for custom components
  document.documentElement.style.setProperty('--primary-color', theme.colors.primary);
  document.documentElement.style.setProperty('--secondary-color', theme.colors.secondary);
  document.documentElement.style.setProperty('--accent-color', theme.colors.accent);
  document.documentElement.style.setProperty('--background-color', theme.colors.background);
  document.documentElement.style.setProperty('--surface-color', theme.colors.surface);
  document.documentElement.style.setProperty('--logo-path', theme.colors.logoPath);

  // Apply theme classes to body
  document.body.classList.remove('dark-theme', 'high-contrast-theme');

  if (themeName === 'highContrast') {
    document.body.classList.add('high-contrast-theme');
  } else if (theme.dark) {
    document.body.classList.add('dark-theme');
  }

  return themeName;
}
