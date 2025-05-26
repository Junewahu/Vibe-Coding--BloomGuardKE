import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Paper,
  useTheme,
  Alert,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ForgotPassword: React.FC = () => {
  const theme = useTheme();
  const { resetPassword, error } = useAuth();
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const validateEmail = () => {
    if (!email) {
      setEmailError('Email is required');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Email is invalid');
      return false;
    }
    setEmailError('');
    return true;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    setEmailError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateEmail()) {
      try {
        await resetPassword(email);
        setIsSubmitted(true);
      } catch (err) {
        // Error is handled by the auth context
      }
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: theme.spacing(4),
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            Reset Password
          </Typography>

          {isSubmitted ? (
            <Box sx={{ width: '100%', textAlign: 'center' }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                Password reset instructions have been sent to your email.
              </Alert>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Please check your email for instructions to reset your password.
              </Typography>
              <Button
                component={RouterLink}
                to="/login"
                variant="contained"
                fullWidth
              >
                Back to Login
              </Button>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Enter your email address and we&apos;ll send you instructions to reset
                your password.
              </Typography>

              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={handleChange}
                error={!!emailError}
                helperText={emailError}
              />

              {error && (
                <Typography color="error" sx={{ mt: 2 }}>
                  {error}
                </Typography>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
              >
                Send Reset Instructions
              </Button>

              <Box sx={{ textAlign: 'center' }}>
                <Link
                  component={RouterLink}
                  to="/login"
                  variant="body2"
                  sx={{ textDecoration: 'none' }}
                >
                  Back to Login
                </Link>
              </Box>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default ForgotPassword; 