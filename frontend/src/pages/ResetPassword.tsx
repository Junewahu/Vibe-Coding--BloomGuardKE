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
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ResetPassword: React.FC = () => {
  const theme = useTheme();
  const { updatePassword, error } = useAuth();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [formErrors, setFormErrors] = useState({
    password: '',
    confirmPassword: '',
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const validateForm = () => {
    let isValid = true;
    const errors = {
      password: '',
      confirmPassword: '',
    };

    if (!formData.password) {
      errors.password = 'Password is required';
      isValid = false;
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
      isValid = false;
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
      isValid = false;
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    setFormErrors((prev) => ({
      ...prev,
      [name]: '',
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setFormErrors((prev) => ({
        ...prev,
        password: 'Invalid or expired reset token',
      }));
      return;
    }

    if (validateForm()) {
      try {
        await updatePassword(token, formData.password);
        setIsSubmitted(true);
      } catch (err) {
        // Error is handled by the auth context
      }
    }
  };

  if (!token) {
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
            <Alert severity="error" sx={{ mb: 2 }}>
              Invalid or expired reset token
            </Alert>
            <Button
              component={RouterLink}
              to="/forgot-password"
              variant="contained"
              fullWidth
            >
              Request New Reset Link
            </Button>
          </Paper>
        </Box>
      </Container>
    );
  }

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
            Reset Your Password
          </Typography>

          {isSubmitted ? (
            <Box sx={{ width: '100%', textAlign: 'center' }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                Your password has been successfully reset.
              </Alert>
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
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="New Password"
                type="password"
                id="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                error={!!formErrors.password}
                helperText={formErrors.password}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                label="Confirm New Password"
                type="password"
                id="confirmPassword"
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={!!formErrors.confirmPassword}
                helperText={formErrors.confirmPassword}
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
                Reset Password
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

export default ResetPassword; 