import { createTheme } from '@mui/material/styles';

// Color palette
const colors = {
  primary: {
    main: '#BDE0FE', // Baby Blue
    light: '#A2D2FF', // Sky Blue
    dark: '#8BB8E8',
  },
  secondary: {
    main: '#FFAFCC', // Candy Pink
    light: '#FFC8DD',
    dark: '#E69FB8',
  },
  accent: {
    main: '#CDB4DB', // Lavender
    light: '#D8C3E3',
    dark: '#B39BC8',
  },
  text: {
    primary: '#22223B', // Deep Navy
    secondary: '#4A4A6A',
    disabled: '#8B8BA3',
  },
  background: {
    default: '#FFFFFF',
    paper: '#F8F9FA',
    card: '#FFFFFF',
  },
  status: {
    success: '#4CAF50',
    warning: '#FFC107',
    error: '#F44336',
    info: '#2196F3',
  },
};

// Typography
const typography = {
  fontFamily: '"Inter", "Nunito", "Poppins", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.4,
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
    fontWeight: 500,
  },
};

// Component styles
const components = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: '2rem',
        padding: '0.5rem 1.5rem',
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        },
      },
      contained: {
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: '1rem',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 6px 24px rgba(0, 0, 0, 0.12)',
        },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: '1rem',
        fontWeight: 500,
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: '1rem',
        },
      },
    },
  },
};

// Create theme
const theme = createTheme({
  palette: colors,
  typography,
  components,
  shape: {
    borderRadius: 16,
  },
  shadows: [
    'none',
    '0 2px 8px rgba(0, 0, 0, 0.05)',
    '0 4px 12px rgba(0, 0, 0, 0.08)',
    '0 6px 16px rgba(0, 0, 0, 0.1)',
    '0 8px 24px rgba(0, 0, 0, 0.12)',
    // ... add more shadow levels as needed
  ],
});

export default theme; 