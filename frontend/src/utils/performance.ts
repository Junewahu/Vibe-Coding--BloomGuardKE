import { PerformanceObserver, PerformanceEntry } from 'perf_hooks';

interface FirstInputEntry extends PerformanceEntry {
  processingStart: number;
  startTime: number;
}

interface LayoutShiftEntry extends PerformanceEntry {
  hadRecentInput: boolean;
  value: number;
}

type PerformanceEntryType = 'first-input' | 'layout-shift' | 'largest-contentful-paint';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();
  private readonly maxMetrics = 1000;
  private readonly reportInterval = 60000; // 1 minute

  constructor() {
    this.initializeObservers();
    this.startPeriodicReporting();
  }

  private initializeObservers() {
    if (typeof PerformanceObserver === 'undefined') {
      console.warn('PerformanceObserver is not supported in this environment');
      return;
    }

    // First Input Delay (FID)
    const fidObserver = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries() as FirstInputEntry[];
      entries.forEach((entry) => {
        this.recordMetric('FID', entry.processingStart - entry.startTime);
      });
    });
    // @ts-ignore - The type definitions are incomplete for newer performance metrics
    fidObserver.observe({ entryTypes: ['first-input'] });

    // Cumulative Layout Shift (CLS)
    const clsObserver = new PerformanceObserver((entryList) => {
      let clsValue = 0;
      const entries = entryList.getEntries() as LayoutShiftEntry[];
      entries.forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      this.recordMetric('CLS', clsValue);
    });
    // @ts-ignore - The type definitions are incomplete for newer performance metrics
    clsObserver.observe({ entryTypes: ['layout-shift'] });

    // Largest Contentful Paint (LCP)
    const lcpObserver = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];
      this.recordMetric('LCP', lastEntry.startTime);
    });
    // @ts-ignore - The type definitions are incomplete for newer performance metrics
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
  }

  private startPeriodicReporting() {
    setInterval(() => {
      this.reportMetrics();
    }, this.reportInterval);
  }

  public recordMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)?.push(value);
  }

  public measureFunction<T>(name: string, fn: () => T): T {
    const start = performance.now();
    try {
      return fn();
    } finally {
      const duration = performance.now() - start;
      this.recordMetric(name, duration);
    }
  }

  public async measureAsyncFunction<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    try {
      return await fn();
    } finally {
      const duration = performance.now() - start;
      this.recordMetric(name, duration);
    }
  }

  private async reportMetrics() {
    if (this.metrics.size === 0) return;

    try {
      // TODO: Replace with actual API endpoint
      await fetch('/api/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.metrics),
      });

      // Clear reported metrics
      this.metrics.clear();
    } catch (error) {
      console.error('Failed to report metrics:', error);
    }
  }

  public getMetrics(): Map<string, number[]> {
    return this.metrics;
  }

  public getAverageMetric(name: string): number {
    const values = this.metrics.get(name);
    if (!values || values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }
}

// Create singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export convenience functions
export const measure = performanceMonitor.measureFunction.bind(performanceMonitor);
export const measureAsync = performanceMonitor.measureAsyncFunction.bind(performanceMonitor);
export const recordMetric = performanceMonitor.recordMetric.bind(performanceMonitor); 