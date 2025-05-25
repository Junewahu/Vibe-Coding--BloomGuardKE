interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private readonly maxMetrics = 1000;
  private readonly reportInterval = 60000; // 1 minute

  constructor() {
    this.initializePerformanceObserver();
    this.startPeriodicReporting();
  }

  private initializePerformanceObserver() {
    if (typeof PerformanceObserver !== 'undefined') {
      // Observe Largest Contentful Paint
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.recordMetric('LCP', lastEntry.startTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // Observe First Input Delay
      const fidObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          this.recordMetric('FID', entry.processingStart - entry.startTime);
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // Observe Cumulative Layout Shift
      const clsObserver = new PerformanceObserver((entryList) => {
        let clsValue = 0;
        const entries = entryList.getEntries();
        entries.forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
        this.recordMetric('CLS', clsValue);
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    }
  }

  private startPeriodicReporting() {
    setInterval(() => {
      this.reportMetrics();
    }, this.reportInterval);
  }

  public recordMetric(name: string, value: number, tags?: Record<string, string>) {
    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
      tags,
    });

    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }
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
    if (this.metrics.length === 0) return;

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
      this.metrics = [];
    } catch (error) {
      console.error('Failed to report metrics:', error);
    }
  }

  public getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  public clearMetrics() {
    this.metrics = [];
  }
}

// Create singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export convenience functions
export const measure = performanceMonitor.measureFunction.bind(performanceMonitor);
export const measureAsync = performanceMonitor.measureAsyncFunction.bind(performanceMonitor);
export const recordMetric = performanceMonitor.recordMetric.bind(performanceMonitor); 