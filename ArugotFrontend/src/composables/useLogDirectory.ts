import { ref } from "vue";

const DB_NAME = "arugot-log-db";
const STORE_NAME = "logDirectory";
const KEY = "logDirectoryHandle";

// Global shared state for the log directory
const logDirectory = ref<FileSystemDirectoryHandle | null>(null);
const isLoading = ref(false);

/**
 * Global composable for managing the automation log directory.
 * This is a singleton - all components share the same log directory state.
 */
export function useLogDirectory() {
  async function openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME);
        }
      };
    });
  }

  async function saveDirectoryHandle(
    handle: FileSystemDirectoryHandle
  ): Promise<void> {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE_NAME, "readwrite");
      const store = transaction.objectStore(STORE_NAME);
      const request = store.put(handle, KEY);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async function loadDirectoryHandle(): Promise<FileSystemDirectoryHandle | null> {
    try {
      const db = await openDB();
      return new Promise((resolve, reject) => {
        const transaction = db.transaction(STORE_NAME, "readonly");
        const store = transaction.objectStore(STORE_NAME);
        const request = store.get(KEY);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
      });
    } catch {
      return null;
    }
  }

  async function restoreDirectoryHandle(): Promise<boolean> {
    isLoading.value = true;
    try {
      const handle = await loadDirectoryHandle();
      if (!handle) return false;

      // Verify we still have permission
      const permission = await (handle as any).queryPermission({
        mode: "read",
      });
      if (permission === "granted") {
        logDirectory.value = handle;
        return true;
      }

      // Try to request permission
      const requestPermission = await (handle as any).requestPermission({
        mode: "read",
      });
      if (requestPermission === "granted") {
        logDirectory.value = handle;
        return true;
      }

      return false;
    } catch {
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function selectDirectory(): Promise<FileSystemDirectoryHandle | null> {
    try {
      const dirHandle = await (window as any).showDirectoryPicker({
        mode: "read",
      });

      logDirectory.value = dirHandle;
      await saveDirectoryHandle(dirHandle);
      return dirHandle;
    } catch (error: any) {
      // User cancelled
      if (error.name === "AbortError") {
        return null;
      }
      throw error;
    }
  }

  function clearDirectory() {
    logDirectory.value = null;
  }

  return {
    logDirectory,
    isLoading,
    selectDirectory,
    restoreDirectoryHandle,
    clearDirectory,
  };
}
