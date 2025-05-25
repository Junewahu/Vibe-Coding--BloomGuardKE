import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { useTheme } from './ThemeProvider';
import { theme as customTheme } from '../utils/theme';

const ThemeToggle: React.FC = () => {
  const { mode, toggleTheme } = useTheme();

  return (
    <Tooltip title={mode === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}>
      <IconButton
        onClick={toggleTheme}
        sx={{
          color: mode === 'light' ? customTheme.colors.deepNavy : customTheme.colors.babyBlue,
          backgroundColor: mode === 'light' ? customTheme.colors.babyBlue : customTheme.colors.deepNavy,
          '&:hover': {
            backgroundColor: mode === 'light' ? customTheme.colors.skyBlue : customTheme.colors.darkNavy,
          },
          transition: `all ${customTheme.transitions.normal} ${customTheme.transitions.easeInOut}`,
        }}
      >
        {mode === 'light' ? <Brightness4 /> : <Brightness7 />}
      </IconButton>
    </Tooltip>
  );
};

export default ThemeToggle; 