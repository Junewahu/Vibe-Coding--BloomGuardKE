import React from 'react';
import {
  CircularProgress,
  Box,
  Typography,
  useTheme,
  LinearProgress,
} from '@mui/material';

export interface LoadingProps {
  variant?: 'circular' | 'linear';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'inherit';
  text?: string;
  fullScreen?: boolean;
  overlay?: boolean;
}

const Loading: React.FC<LoadingProps> = ({
  variant = 'circular',
  size = 'medium',
  color = 'primary',
  text,
  fullScreen = false,
  overlay = false,
}) => {
  const theme = useTheme();

  const getSize = () => {
    switch (size) {
      case 'small':
        return 24;
      case 'large':
        return 48;
      default:
        return 36;
    }
  };

  const getThickness = () => {
    switch (size) {
      case 'small':
        return 3;
      case 'large':
        return 4;
      default:
        return 3.5;
    }
  };

  const containerStyles = {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing(2),
    ...(fullScreen && {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: overlay
        ? 'rgba(255, 255, 255, 0.8)'
        : 'transparent',
      zIndex: theme.zIndex.modal,
    }),
  };

  if (variant === 'linear') {
    return (
      <Box sx={containerStyles}>
        <Box sx={{ width: '100%', maxWidth: 400 }}>
          <LinearProgress
            color={color}
            sx={{
              height: getThickness(),
              borderRadius: getThickness() / 2,
            }}
          />
        </Box>
        {text && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1 }}
          >
            {text}
          </Typography>
        )}
      </Box>
    );
  }

  return (
    <Box sx={containerStyles}>
      <CircularProgress
        size={getSize()}
        thickness={getThickness()}
        color={color}
      />
      {text && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {text}
        </Typography>
      )}
    </Box>
  );
};

export default Loading; 