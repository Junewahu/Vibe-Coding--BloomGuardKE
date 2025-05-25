import * as yup from 'yup';

export const workingHoursSchema = yup.object().shape({
  start: yup.string().required('Start time is required'),
  end: yup.string().required('End time is required'),
});

export const notificationsSchema = yup.object().shape({
  email: yup.boolean(),
  sms: yup.boolean(),
  push: yup.boolean(),
  appointmentReminders: yup.boolean(),
  medicationReminders: yup.boolean(),
  vaccinationReminders: yup.boolean(),
  reminderTime: yup.string().required('Reminder time is required'),
  reminderFrequency: yup.string().required('Reminder frequency is required'),
  lowStockAlerts: yup.boolean(),
});

export const securitySchema = yup.object().shape({
  twoFactorAuth: yup.boolean(),
  sessionTimeout: yup.string().required('Session timeout is required'),
  passwordExpiry: yup.string().required('Password expiry is required'),
  passwordComplexity: yup.string().required('Password complexity is required'),
  loginAttempts: yup.string().required('Login attempts is required'),
});

export const syncSchema = yup.object().shape({
  autoSync: yup.boolean(),
  syncInterval: yup.string().required('Sync interval is required'),
  offlineMode: yup.boolean(),
  dataRetention: yup.string().required('Data retention is required'),
  backupFrequency: yup.string().required('Backup frequency is required'),
});

export const displaySchema = yup.object().shape({
  darkMode: yup.boolean(),
  compactView: yup.boolean(),
  showAvatars: yup.boolean(),
  fontSize: yup.string().required('Font size is required'),
  contrast: yup.string().required('Contrast is required'),
});

export const accessibilitySchema = yup.object().shape({
  highContrast: yup.boolean(),
  screenReader: yup.boolean(),
  reducedMotion: yup.boolean(),
  textToSpeech: yup.boolean(),
});

export const dataSchema = yup.object().shape({
  dataUsage: yup.string().required('Data usage is required'),
  cacheSize: yup.string().required('Cache size is required'),
  autoClearCache: yup.boolean(),
  exportFormat: yup.string().required('Export format is required'),
});

export const settingsSchema = yup.object().shape({
  language: yup.string().required('Language is required'),
  notifications: notificationsSchema,
  security: securitySchema,
  sync: syncSchema,
  display: displaySchema,
  accessibility: accessibilitySchema,
  data: dataSchema,
  clinicName: yup.string().required('Clinic name is required'),
  address: yup.string().required('Address is required'),
  phone: yup.string()
    .required('Phone number is required')
    .matches(/^\+?[\d\s-]+$/, 'Invalid phone number format'),
  email: yup.string()
    .required('Email is required')
    .email('Invalid email format'),
  workingHours: workingHoursSchema,
}); 