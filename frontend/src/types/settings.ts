export interface WorkingHours {
  start: string;
  end: string;
}

export interface Notifications {
  email: boolean;
  sms: boolean;
  push: boolean;
  appointmentReminders: boolean;
  medicationReminders: boolean;
  vaccinationReminders: boolean;
  reminderTime: string;
  reminderFrequency: string;
  lowStockAlerts: boolean;
}

export interface Security {
  twoFactorAuth: boolean;
  sessionTimeout: string;
  passwordExpiry: string;
  passwordComplexity: string;
  loginAttempts: string;
}

export interface Sync {
  autoSync: boolean;
  syncInterval: string;
  offlineMode: boolean;
  dataRetention: string;
  backupFrequency: string;
}

export interface Display {
  darkMode: boolean;
  compactView: boolean;
  showAvatars: boolean;
  fontSize: string;
  contrast: string;
}

export interface Accessibility {
  highContrast: boolean;
  screenReader: boolean;
  reducedMotion: boolean;
  textToSpeech: boolean;
}

export interface Data {
  dataUsage: string;
  cacheSize: string;
  autoClearCache: boolean;
  exportFormat: string;
}

export interface Settings {
  language: string;
  notifications: Notifications;
  security: Security;
  sync: Sync;
  display: Display;
  accessibility: Accessibility;
  data: Data;
  clinicName: string;
  address: string;
  phone: string;
  email: string;
  workingHours: WorkingHours;
}
