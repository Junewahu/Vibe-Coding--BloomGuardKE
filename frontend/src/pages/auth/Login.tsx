import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Container,
  Alert,
  CircularProgress,
  Link,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../components/auth/AuthProvider';
import { theme as customTheme } from '../../utils/theme';

const Login: React.FC = () => {
  const { t } = useTranslation();
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [validationErrors, setValidationErrors] = useState<{
    email?: string;
    password?: string;
  }>({});

  const validateForm = () => {
    const errors: { email?: string; password?: string } = {};
    
    if (!formData.email) {
      errors.email = t('auth.emailRequired');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('auth.invalidEmail');
    }
    
    if (!formData.password) {
      errors.password = t('auth.passwordRequired');
    } else if (formData.password.length < 6) {
      errors.password = t('auth.passwordTooShort');
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      await login(formData.email, formData.password);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear validation error when user starts typing
    if (validationErrors[name as keyof typeof validationErrors]) {
      setValidationErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
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
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
            backgroundColor: 'background.paper',
            borderRadius: customTheme.borderRadius.lg,
          }}
        >
          <Typography
            component="h1"
            variant="h4"
            sx={{
              mb: 3,
              color: customTheme.colors.deepNavy,
              fontFamily: customTheme.typography.fontFamily.secondary,
              fontWeight: customTheme.typography.fontWeight.bold,
            }}
          >
            {t('auth.welcomeBack')}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label={t('auth.email')}
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              error={!!validationErrors.email}
              helperText={validationErrors.email}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: customTheme.borderRadius.md,
                },
              }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label={t('auth.password')}
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              error={!!validationErrors.password}
              helperText={validationErrors.password}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: customTheme.borderRadius.md,
                },
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading}
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                backgroundColor: customTheme.colors.babyBlue,
                color: customTheme.colors.deepNavy,
                '&:hover': {
                  backgroundColor: customTheme.colors.skyBlue,
                },
                borderRadius: customTheme.borderRadius.md,
                fontFamily: customTheme.typography.fontFamily.primary,
                fontWeight: customTheme.typography.fontWeight.medium,
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                t('auth.login')
              )}
            </Button>
            <Box sx={{ textAlign: 'center' }}>
              <Link
                component={RouterLink}
                to="/forgot-password"
                variant="body2"
                sx={{
                  color: customTheme.colors.deepNavy,
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                {t('auth.forgotPassword')}
              </Link>
            </Box>
          </Box>
        </Paper>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {t('auth.noAccount')}{' '}
            <Link
              component={RouterLink}
              to="/register"
              sx={{
                color: customTheme.colors.deepNavy,
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
              }}
            >
              {t('auth.register')}
            </Link>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default Login; 