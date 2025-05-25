import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Import language files
import enTranslation from '../locales/en.json';
import swTranslation from '../locales/sw.json';

// Initialize i18next
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslation,
      },
      sw: {
        translation: swTranslation,
      },
    },
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

interface LanguageContextType {
  currentLanguage: string;
  changeLanguage: (lang: string) => void;
  t: (key: string, options?: any) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  currentLanguage: 'en',
  changeLanguage: () => {},
  t: (key: string) => key,
});

export const useLanguage = () => useContext(LanguageContext);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    return localStorage.getItem('language') || 'en';
  });

  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      i18n.changeLanguage(savedLanguage);
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const changeLanguage = useCallback((lang: string) => {
    i18n.changeLanguage(lang);
    setCurrentLanguage(lang);
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
  }, []);

  return (
    <LanguageContext.Provider
      value={{
        currentLanguage,
        changeLanguage,
        t: i18n.t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

// Language switcher component
export const LanguageSwitcher: React.FC = () => {
  const { currentLanguage, changeLanguage } = useLanguage();

  return (
    <select
      value={currentLanguage}
      onChange={(e) => changeLanguage(e.target.value)}
      style={{
        padding: '8px 12px',
        borderRadius: '4px',
        border: '1px solid #ccc',
        backgroundColor: 'transparent',
        cursor: 'pointer',
      }}
    >
      <option value="en">English</option>
      <option value="sw">Swahili</option>
    </select>
  );
};

export default LanguageProvider; 