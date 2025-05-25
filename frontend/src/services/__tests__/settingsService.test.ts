import { settingsService } from '../settingsService';
import api from '../api';
import { Settings } from '../../types/settings';

// Mock the api module
jest.mock('../api');

describe('SettingsService', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Clear the cache
    settingsService.clearCache();
  });

  describe('getSettings', () => {
    it('should fetch settings from API and cache them', async () => {
      const mockSettings: Settings = {
        language: 'en',
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
          darkMode: false,
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
        clinicName: 'Test Clinic',
        address: '123 Test St',
        phone: '+1234567890',
        email: 'test@example.com',
        workingHours: {
          start: '09:00',
          end: '17:00',
        },
      };

      (api.get as jest.Mock).mockResolvedValueOnce({ data: mockSettings });

      const result = await settingsService.getSettings();

      expect(api.get).toHaveBeenCalledWith('/settings');
      expect(result).toEqual(mockSettings);
    });

    it('should return cached settings if available and valid', async () => {
      const mockSettings: Settings = {
        // ... same mock settings as above
      } as Settings;

      (api.get as jest.Mock).mockResolvedValueOnce({ data: mockSettings });

      // First call to populate cache
      await settingsService.getSettings();
      // Second call should use cache
      const result = await settingsService.getSettings();

      expect(api.get).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockSettings);
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      (api.get as jest.Mock).mockRejectedValueOnce(error);

      await expect(settingsService.getSettings()).rejects.toThrow('API Error');
    });
  });

  describe('updateSettings', () => {
    it('should update settings via API and update cache', async () => {
      const mockSettings: Partial<Settings> = {
        clinicName: 'Updated Clinic',
      };

      const mockResponse = {
        data: {
          ...mockSettings,
          // ... other settings
        },
      };

      (api.put as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await settingsService.updateSettings(mockSettings);

      expect(api.put).toHaveBeenCalledWith('/settings', mockSettings);
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API errors during update', async () => {
      const error = new Error('API Error');
      (api.put as jest.Mock).mockRejectedValueOnce(error);

      await expect(settingsService.updateSettings({})).rejects.toThrow('API Error');
    });
  });

  describe('resetSettings', () => {
    it('should reset settings via API and update cache', async () => {
      const mockResponse = {
        data: {
          // ... default settings
        },
      };

      (api.post as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await settingsService.resetSettings();

      expect(api.post).toHaveBeenCalledWith('/settings/reset');
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API errors during reset', async () => {
      const error = new Error('API Error');
      (api.post as jest.Mock).mockRejectedValueOnce(error);

      await expect(settingsService.resetSettings()).rejects.toThrow('API Error');
    });
  });
}); 