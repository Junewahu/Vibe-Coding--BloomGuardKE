import React from 'react';
import { Card, CardContent, CardHeader, CardActions, Typography, Box, Chip } from '@mui/material';
import { styled } from '@mui/material/styles';

interface BloomCardProps {
  title?: string;
  subtitle?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
  syncStatus?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  onClick?: () => void;
  elevation?: number;
}

const StyledCard = styled(Card)<{ elevation?: number }>(({ theme, elevation = 1 }) => ({
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[elevation],
  transition: 'all 0.3s ease-in-out',
  cursor: 'pointer',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[elevation + 2],
  },
}));

const StatusIndicator = styled(Box)<{ status?: string }>(({ theme, status }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: status ? theme.palette.status[status] : 'transparent',
  marginRight: theme.spacing(1),
  animation: status === 'warning' ? 'pulse 2s infinite' : 'none',
  '@keyframes pulse': {
    '0%': {
      transform: 'scale(1)',
      opacity: 1,
    },
    '50%': {
      transform: 'scale(1.2)',
      opacity: 0.7,
    },
    '100%': {
      transform: 'scale(1)',
      opacity: 1,
    },
  },
}));

const SyncChip = styled(Chip)(({ theme }) => ({
  backgroundColor: theme.palette.accent.light,
  color: theme.palette.text.primary,
  '& .MuiChip-label': {
    fontSize: '0.75rem',
  },
}));

export const BloomCard: React.FC<BloomCardProps> = ({
  title,
  subtitle,
  status,
  syncStatus,
  children,
  actions,
  onClick,
  elevation,
}) => {
  return (
    <StyledCard elevation={elevation} onClick={onClick}>
      {(title || subtitle) && (
        <CardHeader
          title={
            <Box display="flex" alignItems="center">
              {status && <StatusIndicator status={status} />}
              <Typography variant="h6" component="div">
                {title}
              </Typography>
            </Box>
          }
          subheader={subtitle}
          action={
            syncStatus && (
              <SyncChip
                label={syncStatus}
                size="small"
                variant="outlined"
              />
            )
          }
        />
      )}
      <CardContent>{children}</CardContent>
      {actions && <CardActions>{actions}</CardActions>}
    </StyledCard>
  );
};

export default BloomCard; 