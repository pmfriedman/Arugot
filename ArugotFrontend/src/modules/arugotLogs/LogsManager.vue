<template>
  <div class="logs-manager">
    <div class="header">
      <h2>Automation Logs</h2>
      <p class="subtitle">Recent log entries from scheduler.log</p>
    </div>

    <LogDirectoryPicker
      :logDirectory="logDirectory"
      :isLoading="isLoadingDir"
      @select="handleSelectDirectory"
    />

    <div v-if="isLoadingLogs" class="loading-status">
      <p>Loading log file...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-text">{{ error }}</p>
    </div>

    <div v-else-if="logLines.length > 0" class="logs-container">
      <div class="logs-header">
        <span class="logs-count">Last {{ logLines.length }} lines</span>
      </div>

      <div class="log-content">
        <div v-for="(line, index) in logLines" :key="index" class="log-line">
          {{ line }}
        </div>
      </div>
    </div>

    <div v-else-if="logDirectory && !isLoadingLogs" class="empty-state">
      <p>No log entries found in scheduler.log</p>
    </div>

    <div v-else class="instructions">
      <p>Please select the folder containing your automation logs.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useLogDirectory } from "../../composables/useLogDirectory";
import LogDirectoryPicker from "../../components/LogDirectoryPicker.vue";

const {
  logDirectory,
  isLoading: isLoadingDir,
  selectDirectory,
  restoreDirectoryHandle,
} = useLogDirectory();

const logLines = ref<string[]>([]);
const isLoadingLogs = ref(false);
const error = ref("");

const handleSelectDirectory = async () => {
  await selectDirectory();
};

async function loadLogFile() {
  if (!logDirectory.value) {
    logLines.value = [];
    return;
  }

  isLoadingLogs.value = true;
  error.value = "";

  try {
    // Get the logs subdirectory
    const logsDir = await logDirectory.value.getDirectoryHandle("logs");
    // Get the scheduler.log file from the logs directory
    const fileHandle = await logsDir.getFileHandle("scheduler.log");
    const file = await fileHandle.getFile();
    const content = await file.text();

    // Split by lines and get the last 10 non-empty lines
    const allLines = content.split("\n");
    const nonEmptyLines = allLines.filter((line) => line.trim() !== "");
    logLines.value = nonEmptyLines.slice(-10);
  } catch (err: any) {
    if (err.name === "NotFoundError") {
      error.value = "logs/scheduler.log file not found in the selected folder.";
    } else {
      error.value = `Error loading log file: ${err.message}`;
    }
    logLines.value = [];
  } finally {
    isLoadingLogs.value = false;
  }
}

// Watch for directory changes and auto-load
watch(
  logDirectory,
  async (newDir) => {
    if (newDir) {
      await loadLogFile();
    } else {
      logLines.value = [];
      error.value = "";
    }
  },
  { immediate: true }
);

// Restore directory on mount
restoreDirectoryHandle();
</script>

<style scoped>
.logs-manager {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 20px;
}

.subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.loading-status,
.error-state,
.empty-state,
.instructions {
  padding: 20px;
  text-align: center;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 15px;
}

.error-state {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
}

.error-text {
  margin: 0;
  color: #856404;
}

.logs-container {
  margin-top: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.logs-count {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 6px;
  padding: 15px;
  font-family: "Courier New", Courier, monospace;
}

.log-line {
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  text-align: left;
}

.log-line:last-child {
  margin-bottom: 0;
}
</style>
