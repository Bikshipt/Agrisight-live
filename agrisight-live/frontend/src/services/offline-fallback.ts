/**
 * Offline Fallback Service
 * Handles caching and offline capabilities using Service Workers.
 * Expected env vars: None
 * Testing tips: Test in a browser environment with offline mode enabled.
 */

export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').then(
        (registration) => {
          console.log('SW registered: ', registration);
        },
        (err) => {
          console.log('SW registration failed: ', err);
        }
      );
    });
  }
}
