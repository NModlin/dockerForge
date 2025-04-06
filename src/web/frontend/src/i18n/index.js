import { createI18n } from 'vue-i18n';

// Import language files
import en from './locales/en.json';
import es from './locales/es.json';

// Add more languages as needed
const messages = {
  en,
  es,
};

// Create i18n instance
const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: localStorage.getItem('language') || 'en', // Default language
  fallbackLocale: 'en', // Fallback language
  messages,
});

export default i18n;
