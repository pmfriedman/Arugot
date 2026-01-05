<template>
  <div class="vault-directory-picker" :class="{ compact }">
    <div class="controls">
      <span v-if="vaultDirectory && compact" class="vault-name">{{
        vaultDirectory.name
      }}</span>
      <button
        @click="handleSelectDirectory"
        :class="compact ? 'btn-compact' : 'btn-primary'"
      >
        {{
          vaultDirectory ? (compact ? "📁" : "Change Vault") : "Select Vault"
        }}
      </button>
      <slot name="additional-controls" :vaultDirectory="vaultDirectory"></slot>
    </div>

    <div v-if="vaultDirectory && !compact" class="vault-info">
      <strong>Vault:</strong> {{ vaultDirectory.name }}
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-indicator">Loading vault...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, toRefs } from "vue";

interface Props {
  vaultDirectory: FileSystemDirectoryHandle | null;
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

const { vaultDirectory, isLoading } = toRefs(props);
const error = ref("");

const handleSelectDirectory = () => {
  error.value = "";
  emit("select");
};
</script>

<style scoped>
.vault-directory-picker {
  margin-bottom: 20px;
}

.vault-directory-picker.compact {
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

.vault-name {
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

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-compact {
  padding: 6px 12px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.2s;
  backdrop-filter: blur(10px);
}

.btn-compact:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}

.vault-info {
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  margin-bottom: 10px;
}

.error-message {
  padding: 10px;
  background-color: #ffe6e6;
  border-left: 4px solid #ff4444;
  border-radius: 5px;
  color: #cc0000;
  margin-bottom: 10px;
}

.loading-indicator {
  padding: 10px;
  background-color: #e6f3ff;
  border-radius: 5px;
  color: #0066cc;
}
</style>
