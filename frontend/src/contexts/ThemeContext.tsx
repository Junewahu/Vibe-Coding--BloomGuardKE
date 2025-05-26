import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { PaletteMode } from '@mui/material';
import { createAppTheme } from '../theme';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

interface ThemeContextType {
  mode: PaletteMode;
  toggleTheme: () => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_MODE_KEY = 'theme_mode';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<PaletteMode>(() => {
    const savedMode = localStorage.getItem(THEME_MODE_KEY);
    return (savedMode as PaletteMode) || 'light';
  });

  useEffect(() => {
    localStorage.setItem(THEME_MODE_KEY, mode);
  }, [mode]);

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const isDarkMode = mode === 'dark';
  const toggleDarkMode = toggleTheme;

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme, isDarkMode, toggleDarkMode }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 