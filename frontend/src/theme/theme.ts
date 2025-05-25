import { createTheme } from '@mui/material/styles';

export const colors = {
  babyBlue: '#BDE0FE',
  candyPink: '#FFAFCC',
  lavender: '#CDB4DB',
  skyBlue: '#A2D2FF',
  deepNavy: '#22223B',
  white: '#FFFFFF',
  gray: {
    100: '#F8F9FA',
    200: '#E9ECEF',
    300: '#DEE2E6',
    400: '#CED4DA',
    500: '#ADB5BD',
    600: '#6C757D',
    700: '#495057',
    800: '#343A40',
    900: '#212529',
  },
};

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: colors.skyBlue,
      contrastText: colors.deepNavy,
    },
    secondary: {
      main: colors.candyPink,
      contrastText: colors.deepNavy,
    },
    background: {
      default: colors.babyBlue,
      paper: colors.white,
    },
    text: {
      primary: colors.deepNavy,
      secondary: colors.gray[700],
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
    info: {
      main: colors.lavender,
    },
  },
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
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '2rem',
          padding: '0.5rem 1.5rem',
          fontWeight: 600,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '1rem',
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  ...lightTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: colors.skyBlue,
      contrastText: colors.white,
    },
    secondary: {
      main: colors.candyPink,
      contrastText: colors.white,
    },
    background: {
      default: colors.deepNavy,
      paper: colors.gray[800],
    },
    text: {
      primary: colors.white,
      secondary: colors.babyBlue,
    },
  },
}); 