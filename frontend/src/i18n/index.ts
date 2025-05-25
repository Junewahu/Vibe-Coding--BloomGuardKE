import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import translations
import enTranslation from './locales/en.json';
import esTranslation from './locales/es.json';
import frTranslation from './locales/fr.json';
import arTranslation from './locales/ar.json';

const resources = {
  en: {
    translation: enTranslation,
  },
  es: {
    translation: esTranslation,
  },
  fr: {
    translation: frTranslation,
  },
  ar: {
    translation: arTranslation,
  },
};

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

// RTL languages
export const rtlLanguages = ['ar', 'he', 'fa'];

// Get current language direction
export const getLanguageDirection = (language: string): 'ltr' | 'rtl' => {
  return rtlLanguages.includes(language) ? 'rtl' : 'ltr';
};

// Change language and update document direction
export const changeLanguage = async (language: string) => {
  await i18n.changeLanguage(language);
  document.dir = getLanguageDirection(language);
  document.documentElement.lang = language;
};

export default i18n; 