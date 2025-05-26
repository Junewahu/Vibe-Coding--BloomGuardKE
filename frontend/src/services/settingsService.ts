import api from './api';
import { Settings } from '../types/settings';

class SettingsService {
  private static instance: SettingsService;
  private cache: Map<string, any> = new Map();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    this.cache = new Map();
  }

  public static getInstance(): SettingsService {
    if (!SettingsService.instance) {
      SettingsService.instance = new SettingsService();
    }
    return SettingsService.instance;
  }

  private isCacheValid(key: string): boolean {
    const cachedData = this.cache.get(key);
    if (!cachedData) return false;
    return Date.now() - cachedData.timestamp < this.cacheTimeout;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  private getCache(key: string): any {
    const cachedData = this.cache.get(key);
    return cachedData?.data;
  }

  public async getSettings(): Promise<Settings> {
    const cacheKey = 'settings';
    if (this.isCacheValid(cacheKey)) {
      return this.getCache(cacheKey);
    }

    try {
      const response = await api.get('/settings');
      this.setCache(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching settings:', error);
      throw error;
    }
  }

  public async updateSettings(settings: Partial<Settings>): Promise<Settings> {
    try {
      const response = await api.put('/settings', settings);
      this.setCache('settings', response.data);
      return response.data;
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  }

  public async resetSettings(): Promise<Settings> {
    try {
      const response = await api.post('/settings/reset');
      this.setCache('settings', response.data);
      return response.data;
    } catch (error) {
      console.error('Error resetting settings:', error);
      throw error;
    }
  }

  public clearCache(): void {
    this.cache.clear();
  }
}

export const settingsService = SettingsService.getInstance(); 