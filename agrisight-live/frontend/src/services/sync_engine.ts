/**
 * Sync Engine.
 * Syncs offline scans to the backend when connectivity returns.
 * Expected env vars: VITE_API_URL
 * Testing tips: Mock fetch and indexedDB.
 */
import { getPendingScans, markScanSynced } from './offline_storage';

async function syncOnce() {
  const scans = await getPendingScans();
  if (!scans.length) return;

  const baseUrl =
    (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';
  const res = await fetch(`${baseUrl}/api/offline-sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scans }),
  });
  if (!res.ok) return;

  // Mark all as synced on success.
  await Promise.all(scans.map((s) => (s.id ? markScanSynced(s.id) : Promise.resolve())));
}

export function startSyncEngine() {
  // Sync immediately if online.
  if (navigator.onLine) {
    void syncOnce();
  }
  window.addEventListener('online', () => {
    void syncOnce();
  });
}

