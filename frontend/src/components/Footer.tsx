import React from 'react';
import { Box, Container, Typography, Link, useTheme } from '@mui/material';

const Footer: React.FC = () => {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: 'background.paper',
        borderTop: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} BloomGuard. All rights reserved.
          </Typography>

          <Box
            sx={{
              display: 'flex',
              gap: 3,
            }}
          >
            <Link
              href="#"
              color="text.secondary"
              underline="hover"
              sx={{ typography: 'body2' }}
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              color="text.secondary"
              underline="hover"
              sx={{ typography: 'body2' }}
            >
              Terms of Service
            </Link>
            <Link
              href="#"
              color="text.secondary"
              underline="hover"
              sx={{ typography: 'body2' }}
            >
              Contact Us
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer; 