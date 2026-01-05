<template>
  <div class="inbox-manager">
    <div class="header">
      <h2>Inbox</h2>
      <p class="subtitle">Files in your _inbox folder</p>
    </div>

    <div v-if="isLoading" class="loading-status">
      <p>Loading inbox files...</p>
    </div>

    <div v-else-if="inboxFiles.length > 0" class="files-list">
      <p class="files-count">{{ inboxFiles.length }} files in inbox</p>

      <div class="file-items">
        <a
          v-for="file in inboxFiles"
          :key="file.name"
          :href="getObsidianUrl(file.path)"
          class="file-item"
          title="Open in Obsidian"
        >
          <span class="file-icon">📄</span>
          <span class="file-name">{{ file.name }}</span>
        </a>
      </div>
    </div>

    <div v-else-if="vaultDirectory && !isLoading" class="empty-state">
      <p>No files in _inbox folder.</p>
    </div>

    <div v-else class="instructions">
      <p>Please select your Obsidian vault using the vault picker above.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useVaultDirectory } from "../../composables/useVaultDirectory";

interface InboxFile {
  name: string;
  path: string;
}

const { vaultDirectory } = useVaultDirectory();
const inboxFiles = ref<InboxFile[]>([]);
const isLoading = ref(false);

let pollInterval: number | null = null;

// Generate Obsidian deep link
function getObsidianUrl(filePath: string): string {
  const vaultName = vaultDirectory.value?.name || "vault";
  const filePathWithoutExt = filePath.replace(/\.md$/, "");
  return `obsidian://open?vault=${encodeURIComponent(
    vaultName
  )}&file=${encodeURIComponent(filePathWithoutExt)}`;
}

// Watch for vault directory changes and auto-load
watch(
  vaultDirectory,
  async (newVault) => {
    if (newVault) {
      await loadInboxFiles();
      startPolling();
    } else {
      inboxFiles.value = [];
      stopPolling();
    }
  },
  { immediate: true }
);

function startPolling() {
  stopPolling(); // Clear any existing interval
  if (vaultDirectory.value) {
    pollInterval = setInterval(() => {
      loadInboxFiles();
    }, 30000) as unknown as number; // Poll every 30 seconds
  }
}

function stopPolling() {
  if (pollInterval !== null) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

onMounted(() => {
  if (vaultDirectory.value) {
    startPolling();
  }
});

onUnmounted(() => {
  stopPolling();
});

async function loadInboxFiles() {
  if (!vaultDirectory.value) return;

  try {
    isLoading.value = true;
    inboxFiles.value = [];

    // Try to get the _inbox directory
    try {
      const inboxDir = await vaultDirectory.value.getDirectoryHandle("_inbox");

      // List all files in the _inbox directory
      for await (const entry of (inboxDir as any).values()) {
        if (entry.kind === "file") {
          inboxFiles.value.push({
            name: entry.name,
            path: `_inbox/${entry.name}`,
          });
        }
      }

      // Sort files alphabetically
      inboxFiles.value.sort((a, b) => a.name.localeCompare(b.name));
    } catch (err: any) {
      // _inbox folder doesn't exist or we don't have access
      console.log("_inbox folder not found or inaccessible:", err);
    }
  } catch (err: any) {
    console.error("Failed to load inbox files:", err);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.inbox-manager {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header {
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 12px;
}

.header h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.controls {
  display: flex;
  gap: 8px;
}

.btn-secondary {
  padding: 8px 16px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-status,
.empty-state,
.instructions {
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  text-align: center;
  color: #6b7280;
}

.files-count {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.file-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  text-decoration: none;
  color: #374151;
  transition: all 0.2s;
}

.file-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: translateX(4px);
}

.file-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
}
</style>
