import { ref } from "vue";

const DB_NAME = "arugot-vault-db";
const STORE_NAME = "vaultDirectory";
const KEY = "vaultDirectoryHandle";

// Global shared state for the vault directory
const vaultDirectory = ref<FileSystemDirectoryHandle | null>(null);
const isLoading = ref(false);

/**
 * Global composable for managing the Obsidian vault directory.
 * This is a singleton - all components share the same vault directory state.
 */
export function useVaultDirectory() {
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
        mode: "readwrite",
      });
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

  /**
   * Get a file handle for a specific file in the vault
   */
  async function getFileHandle(
    filePath: string
  ): Promise<FileSystemFileHandle | null> {
    if (!vaultDirectory.value) return null;

    try {
      const fileHandle = await vaultDirectory.value.getFileHandle(filePath, {
        create: false,
      });
      return fileHandle;
    } catch {
      return null;
    }
  }

  /**
   * Read a file from the vault
   */
  async function readFile(filePath: string): Promise<string | null> {
    const fileHandle = await getFileHandle(filePath);
    if (!fileHandle) return null;

    try {
      const file = await fileHandle.getFile();
      return await file.text();
    } catch {
      return null;
    }
  }

  /**
   * Write content to a file in the vault
   */
  async function writeFile(
    filePath: string,
    content: string
  ): Promise<boolean> {
    const fileHandle = await getFileHandle(filePath);
    if (!fileHandle) return false;

    try {
      const writable = await (fileHandle as any).createWritable();
      await writable.write(content);
      await writable.close();
      return true;
    } catch {
      return false;
    }
  }

  return {
    vaultDirectory,
    isLoading,
    selectDirectory,
    restoreDirectoryHandle,
    getFileHandle,
    readFile,
    writeFile,
  };
}
