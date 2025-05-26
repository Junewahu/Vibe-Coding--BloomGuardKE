import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Button,
  IconButton,
  Box,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Brightness4 as DarkModeIcon, Brightness7 as LightModeIcon } from '@mui/icons-material';
import { useTheme as useCustomTheme } from '../../contexts/ThemeContext';

export const Navbar: React.FC = () => {
  const theme = useTheme();
  const { isDarkMode, toggleDarkMode } = useCustomTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <AppBar
      position="static"
      color="default"
      elevation={1}
      sx={{
        backgroundColor: 'background.paper',
        color: 'text.primary',
      }}
    >
      <Toolbar>
        <Box sx={{ flexGrow: 1 }}>
          <Button
            component={RouterLink}
            to="/"
            sx={{
              fontWeight: 'bold',
              fontSize: '1.25rem',
              color: 'text.primary',
              textTransform: 'none',
            }}
          >
            BloomGuard
          </Button>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            component={RouterLink}
            to="/chw/current/field-tracker"
            variant="text"
            color="inherit"
          >
            Field Tracker
          </Button>
          <IconButton
            onClick={toggleDarkMode}
            color="inherit"
            aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
          >
            {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
}; 