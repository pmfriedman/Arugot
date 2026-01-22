import { ref, watch, unref, type MaybeRef, isRef } from "vue";

export function useAutoSave(
  content: any,
  saveCallback: () => Promise<void>,
  options: { debounceMs?: number; enabled?: MaybeRef<boolean> } = {}
) {
  const { debounceMs = 1000, enabled = true } = options;

  const isModified = ref<boolean>(false);
  let autoSaveTimer: number | null = null;

  const triggerAutoSave = () => {
    if (!unref(enabled)) return;

    // Clear existing timer
    if (autoSaveTimer !== null) {
      clearTimeout(autoSaveTimer);
    }

    // Set new timer for auto-save
    if (isModified.value) {
      autoSaveTimer = setTimeout(async () => {
        // Double-check enabled state before actually saving
        // This prevents race conditions where enabled changed during debounce
        if (!unref(enabled)) {
          console.log("Auto-save cancelled - no longer enabled");
          return;
        }
        await saveCallback();
        isModified.value = false;
      }, debounceMs) as unknown as number;
    }
  };

  // Watch for content changes
  watch(
    content,
    () => {
      // Only mark as modified if auto-save is enabled
      // This prevents marking content as "modified" when loading external changes
      if (unref(enabled)) {
        isModified.value = true;
        triggerAutoSave();
      }
    },
    { deep: true }
  );

  // Watch for enabled state changes - cancel pending saves when disabled
  if (isRef(enabled)) {
    watch(enabled, (newEnabled) => {
      if (!newEnabled) {
        cancelAutoSave();
        isModified.value = false;
      }
    });
  }

  const cancelAutoSave = () => {
    if (autoSaveTimer !== null) {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = null;
    }
  };

  return {
    isModified,
    triggerAutoSave,
    cancelAutoSave,
  };
}
