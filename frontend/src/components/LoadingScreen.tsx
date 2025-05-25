import React from 'react';
import { Box, CircularProgress, Typography, useTheme } from '@mui/material';
import { keyframes } from '@mui/system';

const pulse = keyframes`
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(189, 224, 254, 0.7);
  }
  
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(189, 224, 254, 0);
  }
  
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(189, 224, 254, 0);
  }
`;

interface LoadingScreenProps {
  message?: string;
  fullScreen?: boolean;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = 'Loading...',
  fullScreen = true,
}) => {
  const theme = useTheme();

  const content = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
      }}
    >
      <Box
        sx={{
          position: 'relative',
          display: 'inline-flex',
          animation: `${pulse} 2s infinite`,
        }}
      >
        <CircularProgress
          size={60}
          thickness={4}
          sx={{
            color: theme.palette.primary.main,
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress
            size={40}
            thickness={4}
            sx={{
              color: theme.palette.secondary.main,
            }}
          />
        </Box>
      </Box>
      <Typography
        variant="h6"
        sx={{
          color: theme.palette.text.primary,
          fontWeight: 500,
        }}
      >
        {message}
      </Typography>
    </Box>
  );

  if (fullScreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: theme.palette.background.default,
          zIndex: theme.zIndex.modal + 1,
        }}
      >
        {content}
      </Box>
    );
  }

  return content;
};

export default LoadingScreen; 