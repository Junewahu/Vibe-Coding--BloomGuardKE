import React from 'react';
import { Container, Box, Typography, Button, useTheme } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { SentimentDissatisfied as SadIcon } from '@mui/icons-material';

const NotFound: React.FC = () => {
  const theme = useTheme();

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <SadIcon
          sx={{
            fontSize: 100,
            color: theme.palette.primary.main,
            mb: 2,
          }}
        />
        <Typography variant="h1" component="h1" sx={{ mb: 2 }}>
          404
        </Typography>
        <Typography variant="h4" component="h2" sx={{ mb: 3 }}>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          The page you are looking for might have been removed, had its name
          changed, or is temporarily unavailable.
        </Typography>
        <Button
          component={RouterLink}
          to="/"
          variant="contained"
          size="large"
          sx={{ px: 4 }}
        >
          Back to Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 