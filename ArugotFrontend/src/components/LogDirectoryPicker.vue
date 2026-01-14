<template>
  <div class="log-directory-picker" :class="{ compact }">
    <div class="controls">
      <span v-if="logDirectory && compact" class="directory-name">{{
        logDirectory.name
      }}</span>
      <button
        @click="handleSelectDirectory"
        :class="compact ? 'btn-compact' : 'btn-primary'"
      >
        {{
          logDirectory ? (compact ? "📁" : "Change Folder") : "Select Folder"
        }}
      </button>
      <slot name="additional-controls" :logDirectory="logDirectory"></slot>
    </div>

    <div v-if="logDirectory && !compact" class="directory-info">
      <strong>Log Folder:</strong> {{ logDirectory.name }}
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-indicator">Loading folder...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, toRefs } from "vue";

interface Props {
  logDirectory: FileSystemDirectoryHandle | null;
  isLoading?: boolean;
  compact?: boolean;
}

interface Emits {
  (e: "select"): void;
  (e: "error", error: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  compact: false,
});

const emit = defineEmits<Emits>();

const { logDirectory, isLoading } = toRefs(props);
const error = ref("");

const handleSelectDirectory = () => {
  error.value = "";
  emit("select");
};
</script>

<style scoped>
.log-directory-picker {
  margin-bottom: 20px;
}

.log-directory-picker.compact {
  margin-bottom: 0;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}

.compact .controls {
  margin-bottom: 0;
  gap: 12px;
}

.directory-name {
  color: white;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.95;
}

.btn-primary {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-compact {
  padding: 6px 10px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.btn-compact:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.directory-info {
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  margin-bottom: 10px;
  font-size: 14px;
}

.error-message {
  padding: 10px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 5px;
  margin-bottom: 10px;
  font-size: 14px;
}

.loading-indicator {
  padding: 10px;
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
  border-radius: 5px;
  margin-bottom: 10px;
  font-size: 14px;
}
</style>
