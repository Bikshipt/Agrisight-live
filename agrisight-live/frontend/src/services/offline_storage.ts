/**
 * Offline Storage Manager.
 * Uses IndexedDB to persist offline crop scans for later sync.
 * Expected env vars: None
 * Testing tips: Mock indexedDB in tests and verify CRUD behavior.
 */

const DB_NAME = 'agrisight-offline';
const DB_VERSION = 1;
const STORE_NAME = 'scans';

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export type OfflineScan = {
  id?: number;
  scan_image: string;
  local_prediction: string;
  timestamp: string;
  geo_location?: { lat: number; lon: number } | null;
  sync_status: 'pending' | 'synced';
};

export async function saveOfflineScan(scan: Omit<OfflineScan, 'id' | 'sync_status'>) {
  const db = await openDb();
  return new Promise<number>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const request = store.add({ ...scan, sync_status: 'pending' });
    request.onsuccess = () => resolve(request.result as number);
    request.onerror = () => reject(request.error);
  });
}

export async function getPendingScans(): Promise<OfflineScan[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();
    request.onsuccess = () => {
      const all = (request.result as OfflineScan[]) || [];
      resolve(all.filter((s) => s.sync_status === 'pending'));
    };
    request.onerror = () => reject(request.error);
  });
}

export async function markScanSynced(id: number) {
  const db = await openDb();
  return new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const getReq = store.get(id);
    getReq.onsuccess = () => {
      const record = getReq.result as OfflineScan | undefined;
      if (!record) {
        resolve();
        return;
      }
      record.sync_status = 'synced';
      const putReq = store.put(record);
      putReq.onsuccess = () => resolve();
      putReq.onerror = () => reject(putReq.error);
    };
    getReq.onerror = () => reject(getReq.error);
  });
}

