import React from 'react';
import { Box, Typography, Button, Paper, useTheme } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Security as SecurityIcon } from '@mui/icons-material';

const Unauthorized: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        p: 3,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 600,
          width: '100%',
          textAlign: 'center',
          borderRadius: theme.shape.borderRadius,
        }}
      >
        <SecurityIcon
          color="error"
          sx={{ fontSize: 64, mb: 2 }}
        />
        <Typography variant="h4" component="h1" gutterBottom>
          Access Denied
        </Typography>
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mb: 3 }}
        >
          You don't have permission to access this page. Please contact your administrator if you believe this is a mistake.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Unauthorized; 