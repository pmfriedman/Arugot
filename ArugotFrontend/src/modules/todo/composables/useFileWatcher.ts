import { ref, onUnmounted } from "vue";

export interface FileChangeEvent {
  lastModified: number;
  size: number;
}

export function useFileWatcher() {
  const isWatching = ref<boolean>(false);
  const hasExternalChanges = ref<boolean>(false);
  const lastCheckedModified = ref<number>(0);
  const lastCheckedSize = ref<number>(0);

  let watchInterval: number | null = null;

  /**
   * Start watching a file for external changes
   * @param fileHandle - The file handle to watch
   * @param intervalMs - How often to check for changes (default: 2000ms)
   * @param onExternalChange - Callback when external changes are detected
   */
  const startWatching = async (
    fileHandle: any,
    intervalMs: number = 2000,
    onExternalChange?: (event: FileChangeEvent) => void
  ) => {
    if (!fileHandle) {
      console.warn("No file handle provided to watch");
      return;
    }

    // Stop any existing watcher
    stopWatching();

    // Get initial file state
    try {
      const file = await fileHandle.getFile();
      lastCheckedModified.value = file.lastModified;
      lastCheckedSize.value = file.size;
      hasExternalChanges.value = false;
      isWatching.value = true;
    } catch (err) {
      console.error("Error getting initial file state:", err);
      return;
    }

    // Start polling
    watchInterval = setInterval(async () => {
      try {
        const file = await fileHandle.getFile();

        // Check if file has been modified externally
        if (
          file.lastModified > lastCheckedModified.value ||
          file.size !== lastCheckedSize.value
        ) {
          hasExternalChanges.value = true;

          if (onExternalChange) {
            onExternalChange({
              lastModified: file.lastModified,
              size: file.size,
            });
          }

          // Update tracked state
          lastCheckedModified.value = file.lastModified;
          lastCheckedSize.value = file.size;
        }
      } catch (err) {
        console.error("Error checking file changes:", err);
        // If we can't read the file, stop watching
        stopWatching();
      }
    }, intervalMs) as unknown as number;
  };

  /**
   * Stop watching the file
   */
  const stopWatching = () => {
    if (watchInterval !== null) {
      clearInterval(watchInterval);
      watchInterval = null;
    }
    isWatching.value = false;
  };

  /**
   * Reset the external changes flag (e.g., after user reloads the file)
   */
  const clearExternalChanges = () => {
    hasExternalChanges.value = false;
  };

  /**
   * Update the tracked file state (e.g., after saving)
   */
  const updateTrackedState = async (fileHandle: any) => {
    try {
      const file = await fileHandle.getFile();
      lastCheckedModified.value = file.lastModified;
      lastCheckedSize.value = file.size;
    } catch (err) {
      console.error("Error updating tracked file state:", err);
    }
  };

  // Cleanup on unmount
  onUnmounted(() => {
    stopWatching();
  });

  return {
    isWatching,
    hasExternalChanges,
    startWatching,
    stopWatching,
    clearExternalChanges,
    updateTrackedState,
  };
}
