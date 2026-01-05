import { ref } from "vue";

const DB_NAME = "arugot-vault-db";
const STORE_NAME = "vaultDirectory";
const KEY = "vaultDirectoryHandle";

export function useVaultDirectory() {
  const vaultDirectory = ref<FileSystemDirectoryHandle | null>(null);

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
    const handle = await loadDirectoryHandle();
    if (!handle) return false;

    try {
      // Verify we still have permission
      const permission = await (handle as any).queryPermission({ mode: "readwrite" });
      if (permission === "granted") {
        vaultDirectory.value = handle;
        return true;
      }

      // Try to request permission
      const requestPermission = await (handle as any).requestPermission({
        mode: "readwrite",
      });
      if (requestPermission === "granted") {
        vaultDirectory.value = handle;
        return true;
      }
    } catch {
      // Handle no longer valid
    }

    return false;
  }

  async function selectDirectory(): Promise<FileSystemDirectoryHandle | null> {
    try {
      const dirHandle = await (window as any).showDirectoryPicker({
        mode: "readwrite",
      });

      vaultDirectory.value = dirHandle;
      await saveDirectoryHandle(dirHandle);
      return dirHandle;
    } catch (err: any) {
      if (err.name === "AbortError") {
        return null;
      }
      throw err;
    }
  }

  return {
    vaultDirectory,
    selectDirectory,
    restoreDirectoryHandle,
  };
}
