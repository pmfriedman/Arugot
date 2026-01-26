<template>
  <div class="vault-todo-manager">
    <div class="header">
      <h2>Vault Tasks</h2>
      <p class="subtitle">Browse all checkboxes across your Obsidian vault</p>
    </div>

    <div v-if="vaultDirectory" class="controls">
      <button @click="scanVault" :disabled="isScanning" class="btn-secondary">
        {{ isScanning ? "Scanning..." : "Refresh Tasks" }}
      </button>
    </div>

    <div v-if="isScanning" class="scanning-status">
      <p>Scanning vault... Found {{ tasks.length }} tasks so far</p>
    </div>

    <div v-else-if="tasks.length > 0" class="tasks-list">
      <p class="tasks-count">
        Found {{ tasks.length }} tasks in
        {{ Object.keys(groupedTasks).length }} files
      </p>

      <div
        v-for="(fileTasks, filePath) in groupedTasks"
        :key="filePath"
        class="file-group"
      >
        <a
          :href="getObsidianUrl(filePath)"
          class="file-header"
          title="Open in Obsidian"
        >
          <span class="file-name">{{ filePath }}</span>
          <span class="task-count">({{ fileTasks.length }})</span>
        </a>

        <div class="task-items">
          <div v-for="task in fileTasks" :key="task.id" class="task-item">
            <input
              type="checkbox"
              :checked="task.completed"
              disabled
              class="task-checkbox"
            />
            <a
              :href="getObsidianUrl(filePath, task.lineNumber)"
              class="task-link"
              title="Open in Obsidian"
            >
              {{ task.text }}
            </a>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="vaultDirectory && !isScanning" class="empty-state">
      <p>No tasks found. Click "Refresh Tasks" to scan the vault.</p>
    </div>

    <div v-else class="instructions">
      <p>Please select your Obsidian vault using the vault picker above.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useVaultDirectory } from "../../composables/useVaultDirectory";

interface VaultTask {
  id: string;
  filePath: string;
  lineNumber: number;
  text: string;
  completed: boolean;
}

// Toggle this to switch between standard Obsidian links and Advanced URI plugin links
// Set to false to revert to basic file opening (no line numbers)
const USE_ADVANCED_URI = true;

const { vaultDirectory, getFreshDirectoryHandle } = useVaultDirectory();
const tasks = ref<VaultTask[]>([]);
const isScanning = ref(false);

// Group tasks by file (exclude completed)
const groupedTasks = computed(() => {
  const groups: Record<string, VaultTask[]> = {};
  for (const task of tasks.value) {
    if (task.completed) continue; // Skip completed tasks
    if (!groups[task.filePath]) {
      groups[task.filePath] = [];
    }
    groups[task.filePath]!.push(task);
  }
  return groups;
});

// Generate Obsidian deep link
function getObsidianUrl(filePath: string, lineNumber?: number): string {
  const vaultName = vaultDirectory.value?.name || "vault";

  if (USE_ADVANCED_URI && lineNumber) {
    // Advanced URI plugin format: obsidian://advanced-uri?vault=X&filepath=Y&line=Z
    return `obsidian://advanced-uri?vault=${encodeURIComponent(
      vaultName
    )}&filepath=${encodeURIComponent(filePath)}&line=${lineNumber}`;
  } else {
    // Standard Obsidian link (just opens the file)
    const filePathWithoutExt = filePath.replace(/\.md$/, "");
    return `obsidian://open?vault=${encodeURIComponent(
      vaultName
    )}&file=${encodeURIComponent(filePathWithoutExt)}`;
  }
}

// Watch for vault directory changes and auto-scan
watch(
  vaultDirectory,
  async (newVault) => {
    if (newVault) {
      await scanVault();
    } else {
      tasks.value = [];
    }
  },
  { immediate: true }
);

async function scanVault() {
  if (!vaultDirectory.value) return;

  try {
    isScanning.value = true;
    tasks.value = [];

    // Get a fresh handle to ensure we see newly created files/folders
    const freshHandle = await getFreshDirectoryHandle();
    if (!freshHandle) {
      console.error("Failed to get fresh directory handle");
      return;
    }

    await scanDirectory(freshHandle, "");
  } catch (err: any) {
    console.error("Scan failed:", err);
  } finally {
    isScanning.value = false;
  }
}

async function scanDirectory(
  dirHandle: FileSystemDirectoryHandle,
  relativePath: string
) {
  for await (const entry of (dirHandle as any).values()) {
    const entryPath = relativePath
      ? `${relativePath}/${entry.name}`
      : entry.name;

    if (entry.kind === "directory") {
      // Skip hidden directories and common excludes
      if (entry.name.startsWith(".") || entry.name === "node_modules") {
        continue;
      }
      await scanDirectory(entry, entryPath);
    } else if (entry.kind === "file" && entry.name.endsWith(".md")) {
      await scanMarkdownFile(entry, entryPath);
    }
  }
}

async function scanMarkdownFile(
  fileHandle: FileSystemFileHandle,
  filePath: string
) {
  try {
    const file = await fileHandle.getFile();
    const content = await file.text();
    const lines = content.split("\n");

    const checkboxRegex = /^- \[([ x])\] (.+)$/;

    lines.forEach((line, index) => {
      const match = line.match(checkboxRegex);
      if (match && match[2]) {
        const completed = match[1] === "x";
        const text = match[2];
        tasks.value.push({
          id: `${filePath}:${index + 1}`,
          filePath,
          lineNumber: index + 1,
          text,
          completed,
        });
      }
    });
  } catch (err) {
    console.error(`Failed to read ${filePath}:`, err);
  }
}
</script>

<style scoped>
.vault-todo-manager {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  margin-bottom: 1.5rem;
}

.header h2 {
  color: #42b883;
  margin: 0 0 0.25rem 0;
}

.subtitle {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.instructions {
  background: #e3f2fd;
  padding: 1.5rem;
  border-radius: 6px;
  margin-top: 2rem;
  border-left: 4px solid #2196f3;
}

.instructions p {
  margin: 0;
  color: #333;
}

.scanning-status {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.tasks-list {
  flex: 1;
  overflow-y: auto;
  text-align: left;
}

.tasks-count {
  margin: 0 0 15px 0;
  color: #6c757d;
  font-size: 14px;
  text-align: left;
}

.file-group {
  margin-bottom: 28px;
}

.file-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #e7f3ff;
  border-left: 4px solid #007bff;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 700;
  color: #004085;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s, border-left-color 0.2s;
  cursor: pointer;
}

.file-header:hover {
  background-color: #d4e9ff;
  border-left-color: #0056b3;
}

.file-name {
  flex: 1;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.task-count {
  color: #6c757d;
  font-weight: 600;
  font-size: 13px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 0;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.task-item:hover {
  background-color: #f8f9fa;
}

.task-checkbox {
  cursor: not-allowed;
  opacity: 0.7;
  flex-shrink: 0;
}

.task-link {
  flex: 1;
  font-size: 14px;
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.2s;
}

.task-link:hover {
  color: #007bff;
  text-decoration: underline;
}

.task-item:has(.task-checkbox:checked) .task-link {
  text-decoration: line-through;
  color: #6c757d;
}

.task-item:has(.task-checkbox:checked) .task-link:hover {
  color: #545b62;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-state p {
  margin: 0;
}
</style>
