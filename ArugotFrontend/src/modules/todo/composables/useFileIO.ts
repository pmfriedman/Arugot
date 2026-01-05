import { ref } from "vue";

export function useFileIO() {
  const fileContent = ref<string>("");
  const originalContent = ref<string>("");
  const permissionStatus = ref<string>("");
  const isSaving = ref<boolean>(false);

  const readFile = async (fileHandle: any): Promise<string> => {
    if (!fileHandle) throw new Error("No file handle provided");

    // Request permission to read
    const permission = await fileHandle.queryPermission({ mode: "read" });
    permissionStatus.value = `Read permission: ${permission}`;

    if (permission === "denied") {
      throw new Error("Permission denied to read file");
    }

    const file = await fileHandle.getFile();
    const content = await file.text();

    fileContent.value = content;
    originalContent.value = content;

    return content;
  };

  const writeFile = async (fileHandle: any, content: string): Promise<void> => {
    if (!fileHandle) throw new Error("No file handle provided");
    if (isSaving.value) return;

    try {
      isSaving.value = true;

      // Request permission to write
      const permission = await fileHandle.queryPermission({
        mode: "readwrite",
      });

      if (permission === "denied" || permission === "prompt") {
        const requestPermission = await fileHandle.requestPermission({
          mode: "readwrite",
        });
        if (requestPermission === "denied") {
          throw new Error("Permission denied to write file");
        }
      }

      permissionStatus.value = `Write permission: granted`;

      // Create a writable stream
      const writable = await fileHandle.createWritable();
      await writable.write(content);
      await writable.close();

      originalContent.value = content;
    } finally {
      isSaving.value = false;
    }
  };

  const isModified = (): boolean => {
    return fileContent.value !== originalContent.value;
  };

  // TODO: Add file watcher functionality
  // - Poll file for changes every N seconds
  // - Detect if file was modified externally
  // - Notify user of external changes
  // - Provide merge/reload options

  return {
    fileContent,
    originalContent,
    permissionStatus,
    isSaving,
    readFile,
    writeFile,
    isModified,
  };
}
