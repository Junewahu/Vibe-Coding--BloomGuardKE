declare global {
  interface Window {
    workbox: {
      register: () => void;
      unregister: () => void;
      messageSkipWaiting: () => void;
      addEventListener: (event: string, callback: (event: any) => void) => void;
    };
  }
}

export function registerServiceWorker() {
  if (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    window.workbox !== undefined
  ) {
    const wb = window.workbox;

    // Add event listeners to handle PWA lifecycle
    addEventListener('message', (event: MessageEvent) => {
      if (event.data && event.data.type === 'SKIP_WAITING') {
        wb.messageSkipWaiting();
      }
    });

    // Register the service worker after event listeners are added
    wb.register();

    // Handle updates
    wb.addEventListener('installed', (event: { isUpdate: boolean }) => {
      if (event.isUpdate) {
        if (confirm('New content is available! Click OK to refresh.')) {
          window.location.reload();
        }
      }
    });

    // Handle errors
    wb.addEventListener('error', (event: ErrorEvent) => {
      console.error('Service worker error:', event);
    });

    // Handle offline status
    wb.addEventListener('offline', () => {
      console.log('Application is offline');
    });

    wb.addEventListener('online', () => {
      console.log('Application is online');
    });

    // Handle background sync
    wb.addEventListener('sync', (event: { tag: string }) => {
      if (event.tag === 'sync-queue') {
        console.log('Background sync triggered');
      }
    });
  }
}

export function unregisterServiceWorker() {
  if (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    window.workbox !== undefined
  ) {
    window.workbox.unregister();
  }
} 