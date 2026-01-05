import { ref } from "vue";

const DB_NAME = "TodoFileManagerDB";
const STORE_NAME = "fileHandles";
const HANDLE_KEY = "lastFileHandle";

export function useFileHandle() {
  const fileHandle = ref<any>(null);
  const fileName = ref<string>("");
  const isRestoring = ref<boolean>(false);

  const openDB = (): Promise<IDBDatabase> => {
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
  };

  const saveHandleToIndexedDB = async (handle: any) => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, "readwrite");
      const store = transaction.objectStore(STORE_NAME);
      store.put(handle, HANDLE_KEY);

      return new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });
    } catch (err) {
      console.error("Error saving handle to IndexedDB:", err);
    }
  };

  const loadHandleFromIndexedDB = async (): Promise<any> => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, "readonly");
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(HANDLE_KEY);

      return new Promise((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    } catch (err) {
      console.error("Error loading handle from IndexedDB:", err);
      return null;
    }
  };

  const openFilePicker = async (): Promise<{
    handle: any;
    name: string;
  } | null> => {
    try {
      const [handle] = await (window as any).showOpenFilePicker({
        types: [
          {
            description: "Markdown Files",
            accept: { "text/markdown": [".md", ".markdown"] },
          },
        ],
        multiple: false,
      });

      fileHandle.value = handle;
      fileName.value = handle.name;

      // Save handle to IndexedDB for future sessions
      await saveHandleToIndexedDB(handle);

      return { handle, name: handle.name };
    } catch (err: any) {
      if (err.name !== "AbortError") {
        throw err;
      }
      return null;
    }
  };

  const restoreFileHandle = async (): Promise<boolean> => {
    isRestoring.value = true;
    try {
      const handle = await loadHandleFromIndexedDB();

      if (handle) {
        // Verify we still have permission
        const permission = await handle.queryPermission({ mode: "read" });

        if (permission === "granted") {
          fileHandle.value = handle;
          fileName.value = handle.name;
          return true;
        }
      }
      return false;
    } catch (err) {
      console.error("Error restoring file handle:", err);
      return false;
    } finally {
      isRestoring.value = false;
    }
  };

  return {
    fileHandle,
    fileName,
    isRestoring,
    openFilePicker,
    restoreFileHandle,
  };
}
