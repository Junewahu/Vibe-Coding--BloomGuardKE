import { createTheme, ThemeOptions, responsiveFontSizes } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';

declare module '@mui/material/styles' {
  interface Palette {
    status: {
      success: string;
      warning: string;
      error: string;
      info: string;
    };
    accent: {
      main: string;
      light: string;
      dark: string;
    };
  }
  interface PaletteOptions {
    status?: {
      success: string;
      warning: string;
      error: string;
      info: string;
    };
    accent?: {
      main: string;
      light: string;
      dark: string;
    };
  }
}

// Common theme configuration
const commonTheme = {
  typography: {
    fontFamily: '"Inter", "Nunito", "Poppins", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
  transitions: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
  },
};

// Light theme
const lightTheme: ThemeOptions = {
  ...commonTheme,
  palette: {
    mode: 'light',
    primary: {
      main: '#A2D2FF',
      light: '#BDE0FE',
      dark: '#22223B',
      contrastText: '#22223B',
    },
    secondary: {
      main: '#FFAFCC',
      light: '#FFC8DD',
      dark: '#CDB4DB',
      contrastText: '#22223B',
    },
    background: {
      default: '#BDE0FE',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#22223B',
      secondary: '#343A40',
    },
    error: {
      main: '#FF6B6B',
    },
    warning: {
      main: '#FFD93D',
    },
    success: {
      main: '#6BCB77',
    },
  },
};

// Dark theme
const darkTheme: ThemeOptions = {
  ...commonTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#8b5cf6',
      light: '#a78bfa',
      dark: '#7c3aed',
      contrastText: '#ffffff',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
    },
    error: {
      main: '#FF6B6B',
    },
    warning: {
      main: '#FFD93D',
    },
    success: {
      main: '#6BCB77',
    },
  },
};

// Create theme based on mode
export const createAppTheme = (mode: PaletteMode) => {
  const theme = createTheme(mode === 'light' ? lightTheme : darkTheme);
  return responsiveFontSizes(theme);
};

// Responsive breakpoints
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
};

// Spacing utilities
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Animation durations
export const animationDurations = {
  shortest: 150,
  shorter: 200,
  short: 250,
  standard: 300,
  complex: 375,
  enteringScreen: 225,
  leavingScreen: 195,
};

// Z-index layers
export const zIndex = {
  mobileStepper: 1000,
  speedDial: 1050,
  appBar: 1100,
  drawer: 1200,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500,
};

export default createAppTheme('light'); 