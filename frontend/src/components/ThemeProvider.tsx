import React, { createContext, useContext, useState, useEffect } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme as customTheme } from '../utils/theme';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  mode: 'light',
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const savedMode = localStorage.getItem('themeMode');
    return (savedMode as ThemeMode) || 'light';
  });

  useEffect(() => {
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'light' ? customTheme.colors.skyBlue : customTheme.colors.babyBlue,
        contrastText: customTheme.colors.deepNavy,
      },
      secondary: {
        main: customTheme.colors.candyPink,
        contrastText: customTheme.colors.deepNavy,
      },
      background: {
        default: mode === 'light' ? customTheme.colors.lightBackground : customTheme.colors.darkBackground,
        paper: mode === 'light' ? customTheme.colors.white : customTheme.colors.deepNavy,
      },
      text: {
        primary: mode === 'light' ? customTheme.colors.darkText : customTheme.colors.lightText,
        secondary: mode === 'light' ? customTheme.colors.secondaryText : customTheme.colors.babyBlue,
      },
    },
    typography: {
      fontFamily: customTheme.typography.fontFamily.primary,
      h1: {
        fontFamily: customTheme.typography.fontFamily.secondary,
        fontWeight: customTheme.typography.fontWeight.bold,
      },
      h2: {
        fontFamily: customTheme.typography.fontFamily.secondary,
        fontWeight: customTheme.typography.fontWeight.semibold,
      },
      h3: {
        fontFamily: customTheme.typography.fontFamily.secondary,
        fontWeight: customTheme.typography.fontWeight.medium,
      },
      button: {
        textTransform: 'none',
        fontWeight: customTheme.typography.fontWeight.medium,
      },
    },
    shape: {
      borderRadius: parseInt(customTheme.borderRadius.medium),
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: customTheme.borderRadius.full,
            padding: `${customTheme.spacing.sm} ${customTheme.spacing.lg}`,
            transition: `all ${customTheme.transitions.normal} ${customTheme.transitions.easeInOut}`,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: customTheme.borderRadius.xl,
            boxShadow: customTheme.shadows.soft,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: customTheme.borderRadius.medium,
          },
        },
      },
    },
  });

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeProvider; 