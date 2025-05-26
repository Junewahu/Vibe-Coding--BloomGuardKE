import { createTheme } from '@mui/material/styles';
import { PaletteColorOptions } from '@mui/material';

declare module '@mui/material/styles' {
  interface Theme {
    colors: {
      babyBlue: string;
      skyBlue: string;
      lavender: string;
      deepNavy: string;
      darkGray: string;
      lightGray: string;
      white: string;
      candyPink: string;
    };
    borderRadius: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
  }
  interface ThemeOptions {
    colors?: {
      babyBlue?: string;
      skyBlue?: string;
      lavender?: string;
      deepNavy?: string;
      darkGray?: string;
      lightGray?: string;
      white?: string;
      candyPink?: string;
    };
    borderRadius?: {
      sm?: string;
      md?: string;
      lg?: string;
      xl?: string;
    };
  }
}

const colors = {
  babyBlue: '#BDE0FE',
  skyBlue: '#A2D2FF',
  lavender: '#CDB4DB',
  deepNavy: '#22223B',
  darkGray: '#343A40',
  lightGray: '#F5F7FA',
  white: '#FFFFFF',
  candyPink: '#FFAFCC',
};

const borderRadius = {
  sm: '4px',
  md: '8px',
  lg: '16px',
  xl: '24px',
};

export const theme = createTheme({
  palette: {
    primary: {
      main: colors.babyBlue,
      contrastText: colors.deepNavy,
    },
    secondary: {
      main: colors.lavender,
      contrastText: colors.deepNavy,
    },
    error: {
      main: colors.candyPink,
      contrastText: colors.deepNavy,
    },
    background: {
      default: colors.lightGray,
      paper: colors.white,
    },
    text: {
      primary: colors.deepNavy,
      secondary: colors.darkGray,
    },
  },
  typography: {
    fontFamily: '"Inter", "Nunito", "Poppins", sans-serif',
    h1: {
      fontWeight: 700,
      color: colors.deepNavy,
    },
    h2: {
      fontWeight: 600,
      color: colors.deepNavy,
    },
    h3: {
      fontWeight: 600,
      color: colors.deepNavy,
    },
    h4: {
      fontWeight: 500,
      color: colors.deepNavy,
    },
    h5: {
      fontWeight: 500,
      color: colors.deepNavy,
    },
    h6: {
      fontWeight: 500,
      color: colors.deepNavy,
    },
    body1: {
      color: colors.deepNavy,
    },
    body2: {
      color: colors.darkGray,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: borderRadius.md,
          padding: '8px 16px',
          '&:hover': {
            backgroundColor: colors.skyBlue,
          },
        },
        contained: {
          backgroundColor: colors.babyBlue,
          color: colors.deepNavy,
          '&:hover': {
            backgroundColor: colors.skyBlue,
          },
        },
        outlined: {
          borderColor: colors.deepNavy,
          color: colors.deepNavy,
          '&:hover': {
            borderColor: colors.deepNavy,
            backgroundColor: `${colors.deepNavy}10`,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.lg,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: borderRadius.md,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: borderRadius.md,
        },
      },
    },
  },
  colors,
  borderRadius,
});

export const customTheme = theme;

// Custom spacing for consistent layout
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
};

// Custom breakpoints for responsive design
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
};

// Custom transitions for smooth animations
export const transitions = {
  default: 'all 0.3s ease',
  fast: 'all 0.15s ease',
  slow: 'all 0.5s ease',
};

// Custom z-index values for proper layering
export const zIndex = {
  drawer: 1200,
  appBar: 1100,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500,
};

// Export all theme-related constants
export const themeConstants = {
  colors,
  spacing,
  breakpoints,
  transitions,
  zIndex,
}; 