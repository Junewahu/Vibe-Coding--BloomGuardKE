import { createTheme, ThemeOptions } from '@mui/material/styles';

const themeOptions: ThemeOptions = {
  palette: {
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
  },
};

const theme = createTheme(themeOptions);

export default theme; 