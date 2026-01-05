import { ref, watch, unref, type MaybeRef } from "vue";

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
        await saveCallback();
        isModified.value = false;
      }, debounceMs) as unknown as number;
    }
  };

  // Watch for content changes
  watch(
    content,
    () => {
      isModified.value = true;
      triggerAutoSave();
    },
    { deep: true }
  );

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
