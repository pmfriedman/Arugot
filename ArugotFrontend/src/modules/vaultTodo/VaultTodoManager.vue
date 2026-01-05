<template>
  <div class="vault-todo-manager">
    <div class="header">
      <h2>Vault Tasks</h2>
      <p class="subtitle">Browse all checkboxes across your Obsidian vault</p>
    </div>

    <div class="controls">
      <button @click="selectVaultDirectory" class="btn-primary">
        {{ vaultDirectory ? "Change Vault" : "Select Vault" }}
      </button>
      <button
        @click="scanVault"
        :disabled="!vaultDirectory || isScanning"
        class="btn-secondary"
      >
        {{ isScanning ? "Scanning..." : "Refresh Tasks" }}
      </button>
    </div>

    <div v-if="vaultDirectory" class="vault-info">
      <strong>Vault:</strong> {{ vaultDirectory.name }}
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
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
              :href="getObsidianUrl(filePath)"
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useVaultDirectory } from "./composables/useVaultDirectory";

interface VaultTask {
  id: string;
  filePath: string;
  lineNumber: number;
  text: string;
  completed: boolean;
}

const { vaultDirectory, selectDirectory, restoreDirectoryHandle } =
  useVaultDirectory();
const tasks = ref<VaultTask[]>([]);
const isScanning = ref(false);
const error = ref("");

// Group tasks by file
const groupedTasks = computed(() => {
  const groups: Record<string, VaultTask[]> = {};
  for (const task of tasks.value) {
    if (!groups[task.filePath]) {
      groups[task.filePath] = [];
    }
    groups[task.filePath]!.push(task);
  }
  return groups;
});

// Generate Obsidian deep link
function getObsidianUrl(filePath: string): string {
  const vaultName = vaultDirectory.value?.name || "vault";
  // Remove .md extension for Obsidian links
  const filePathWithoutExt = filePath.replace(/\.md$/, "");
  return `obsidian://open?vault=${encodeURIComponent(
    vaultName
  )}&file=${encodeURIComponent(filePathWithoutExt)}`;
}

async function selectVaultDirectory() {
  try {
    error.value = "";
    await selectDirectory();
    tasks.value = [];
  } catch (err: any) {
    error.value = `Failed to select directory: ${err.message}`;
  }
}

onMounted(async () => {
  const restored = await restoreDirectoryHandle();
  if (restored) {
    await scanVault();
  }
});

async function scanVault() {
  if (!vaultDirectory.value) return;

  try {
    error.value = "";
    isScanning.value = true;
    tasks.value = [];

    await scanDirectory(vaultDirectory.value, "");
  } catch (err: any) {
    error.value = `Scan failed: ${err.message}`;
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
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vault-info {
  padding: 10px;
  background: #e7f3ff;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #004085;
}

.error-message {
  padding: 12px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  margin-bottom: 20px;
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
