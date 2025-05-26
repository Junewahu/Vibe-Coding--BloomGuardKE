import React, { useState, useEffect } from 'react';
import { useFormik, FormikHelpers } from 'formik';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
  useTheme as useMuiTheme,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save as SaveIcon,
  Language as LanguageIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Sync as SyncIcon,
  Info as InfoIcon,
  Accessibility as AccessibilityIcon,
  DataUsage as DataUsageIcon,
  Backup as BackupIcon,
  Delete,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { settingsService } from '../services/settingsService';
import { useTheme } from '../contexts/ThemeContext';
import { useNotification } from '../components/NotificationSystem';
import { settingsSchema } from '../validations/settingsValidation';
import type { Settings as SettingsType } from '../types/settings';
import { theme as customTheme } from '../utils/theme';

const Settings: React.FC = () => {
  const muiTheme = useMuiTheme();
  const { t, i18n } = useTranslation();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { showNotification } = useNotification();
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const formik = useFormik({
    initialValues: {
      language: i18n.language,
      notifications: {
        email: true,
        sms: true,
        push: true,
        appointmentReminders: true,
        medicationReminders: true,
        vaccinationReminders: true,
        reminderTime: '09:00',
        reminderFrequency: 'daily',
        lowStockAlerts: true,
      },
      security: {
        twoFactorAuth: false,
        sessionTimeout: '30',
        passwordExpiry: '90',
        passwordComplexity: 'medium',
        loginAttempts: '5',
      },
      sync: {
        autoSync: true,
        syncInterval: '15',
        offlineMode: true,
        dataRetention: '90',
        backupFrequency: 'daily',
      },
      display: {
        darkMode: isDarkMode,
        compactView: false,
        showAvatars: true,
        fontSize: 'medium',
        contrast: 'normal',
      },
      accessibility: {
        highContrast: false,
        screenReader: false,
        reducedMotion: false,
        textToSpeech: false,
      },
      data: {
        dataUsage: 'normal',
        cacheSize: '100',
        autoClearCache: false,
        exportFormat: 'json',
      },
      clinicName: 'BloomGuard Clinic',
      address: '123 Medical Center Drive',
      phone: '+1 234 567 8900',
      email: 'contact@bloomguard.com',
      workingHours: {
        start: '09:00',
        end: '17:00',
      },
    } as SettingsType,
    validationSchema: settingsSchema,
    onSubmit: async (values: SettingsType, helpers: FormikHelpers<SettingsType>) => {
      try {
        setIsLoading(true);
        await settingsService.updateSettings(values);
        showNotification(t('settings.saveSuccess'), 'success');
        setOpenSnackbar(true);
      } catch (error) {
        console.error('Failed to save settings:', error);
        showNotification(t('settings.saveError'), 'error');
      } finally {
        setIsLoading(false);
      }
    },
  });

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const savedSettings = await settingsService.getSettings();
        formik.setValues(savedSettings);
      } catch (error) {
        console.error('Failed to load settings:', error);
        showNotification(t('settings.loadError'), 'error');
      } finally {
        setIsLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handleLanguageChange = (event: SelectChangeEvent<string>) => {
    const newLanguage = event.target.value;
    i18n.changeLanguage(newLanguage);
    formik.setFieldValue('language', newLanguage);
  };

  const handleSnackbarClose = () => {
    setOpenSnackbar(false);
  };

  const handleDeleteAccount = () => {
    // Implement delete account logic
    setDeleteDialogOpen(false);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography>{t('common.loading')}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography
          variant="h4"
          sx={{
            color: customTheme.colors.deepNavy,
            fontFamily: customTheme.typography.fontFamily.secondary,
            fontWeight: customTheme.typography.fontWeight.bold,
          }}
        >
          {t('settings.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={() => formik.handleSubmit()}
          disabled={isLoading || !formik.dirty}
          sx={{
            backgroundColor: customTheme.colors.babyBlue,
            color: customTheme.colors.deepNavy,
            '&:hover': {
              backgroundColor: customTheme.colors.skyBlue,
            },
            borderRadius: customTheme.borderRadius.md,
          }}
        >
          {t('settings.save')}
        </Button>
      </Box>

      {/* Settings Sections */}
      <Grid container spacing={3}>
        {/* Language Settings */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <LanguageIcon
                  sx={{
                    color: customTheme.colors.babyBlue,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('settings.language')}
                </Typography>
              </Box>
              <FormControl fullWidth>
                <InputLabel>{t('settings.selectLanguage')}</InputLabel>
                <Select
                  value={formik.values.language}
                  label={t('settings.selectLanguage')}
                  onChange={handleLanguageChange}
                  onBlur={formik.handleBlur}
                  sx={{
                    borderRadius: customTheme.borderRadius.md,
                  }}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Español</MenuItem>
                  <MenuItem value="fr">Français</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NotificationsIcon
                  sx={{
                    color: customTheme.colors.lavender,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('settings.notifications')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.notifications.email}
                      onChange={formik.handleChange}
                      name="notifications.email"
                    />
                  }
                  label={t('settings.emailNotifications')}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.notifications.sms}
                      onChange={formik.handleChange}
                      name="notifications.sms"
                    />
                  }
                  label={t('settings.smsNotifications')}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.notifications.push}
                      onChange={formik.handleChange}
                      name="notifications.push"
                    />
                  }
                  label={t('settings.pushNotifications')}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon
                  sx={{
                    color: customTheme.colors.candyPink,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('settings.security')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.security.twoFactorAuth}
                      onChange={formik.handleChange}
                      name="security.twoFactorAuth"
                    />
                  }
                  label={t('settings.twoFactorAuth')}
                />
                <TextField
                  label={t('settings.sessionTimeout')}
                  type="number"
                  value={formik.values.security.sessionTimeout}
                  onChange={formik.handleChange}
                  name="security.sessionTimeout"
                  InputProps={{
                    endAdornment: <Typography>minutes</Typography>,
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Backup Settings */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BackupIcon
                  sx={{
                    color: customTheme.colors.skyBlue,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('settings.backup')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.sync.autoSync}
                      onChange={formik.handleChange}
                      name="sync.autoSync"
                    />
                  }
                  label={t('settings.autoBackup')}
                />
                <FormControl fullWidth>
                  <InputLabel>{t('settings.backupFrequency')}</InputLabel>
                  <Select
                    value={formik.values.sync.backupFrequency}
                    label={t('settings.backupFrequency')}
                    onChange={formik.handleChange}
                    name="sync.backupFrequency"
                    sx={{
                      borderRadius: customTheme.borderRadius.md,
                    }}
                  >
                    <MenuItem value="daily">{t('settings.daily')}</MenuItem>
                    <MenuItem value="weekly">{t('settings.weekly')}</MenuItem>
                    <MenuItem value="monthly">{t('settings.monthly')}</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Danger Zone */}
        <Grid item xs={12}>
          <Card
            sx={{
              borderRadius: customTheme.borderRadius.lg,
              boxShadow: customTheme.shadows.soft,
              border: `1px solid ${customTheme.colors.candyPink}`,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Delete
                  sx={{
                    color: customTheme.colors.candyPink,
                    mr: 1,
                  }}
                />
                <Typography
                  variant="h6"
                  sx={{
                    color: customTheme.colors.deepNavy,
                    fontFamily: customTheme.typography.fontFamily.secondary,
                  }}
                >
                  {t('settings.dangerZone')}
                </Typography>
              </Box>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                {t('settings.dangerZoneDescription')}
              </Typography>
              <Button
                variant="outlined"
                color="error"
                onClick={() => setDeleteDialogOpen(true)}
                sx={{
                  borderColor: customTheme.colors.candyPink,
                  color: customTheme.colors.candyPink,
                  '&:hover': {
                    borderColor: customTheme.colors.candyPink,
                    backgroundColor: customTheme.colors.candyPink + '20',
                  },
                }}
              >
                {t('settings.deleteAccount')}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Delete Account Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        PaperProps={{
          sx: {
            borderRadius: customTheme.borderRadius.lg,
            boxShadow: customTheme.shadows.medium,
          },
        }}
      >
        <DialogTitle sx={{ color: customTheme.colors.deepNavy }}>
          {t('settings.deleteAccount')}
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            {t('settings.deleteAccountConfirmation')}
          </Typography>
          <TextField
            label={t('settings.typeDelete')}
            fullWidth
            placeholder="DELETE"
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            sx={{ color: customTheme.colors.deepNavy }}
          >
            {t('common.cancel')}
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteAccount}
            sx={{
              backgroundColor: customTheme.colors.candyPink,
              '&:hover': {
                backgroundColor: customTheme.colors.candyPink + '80',
              },
            }}
          >
            {t('settings.deleteAccount')}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          {t('settings.settingsSaved')}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings; 