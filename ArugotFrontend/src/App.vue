<script setup lang="ts">
import { onMounted, ref } from "vue";
import InboxManager from "./modules/inbox/InboxManager.vue";
import TodoManager from "./modules/todo/TodoManager.vue";
import VaultTodoManager from "./modules/vaultTodo/VaultTodoManager.vue";
import LogsManager from "./modules/arugotLogs/LogsManager.vue";
import VaultDirectoryPicker from "./components/VaultDirectoryPicker.vue";
import { useVaultDirectory } from "./composables/useVaultDirectory";

const { vaultDirectory, isLoading, selectDirectory, restoreDirectoryHandle } =
  useVaultDirectory();

const showLogs = ref(false);

const handleSelectDirectory = async () => {
  await selectDirectory();
};

const toggleLogs = () => {
  showLogs.value = !showLogs.value;
};

onMounted(async () => {
  await restoreDirectoryHandle();
});
</script>

<template>
  <div class="app-container">
    <nav class="navbar">
      <h1 class="app-title">Arugot</h1>
      <div class="navbar-controls">
        <VaultDirectoryPicker
          :vaultDirectory="vaultDirectory"
          :isLoading="isLoading"
          @select="handleSelectDirectory"
          compact
        />
        <button
          @click="toggleLogs"
          class="logs-toggle"
          :title="showLogs ? 'Hide logs' : 'Show logs'"
        >
          📋
        </button>
      </div>
    </nav>

    <div v-if="showLogs" class="logs-section">
      <LogsManager />
    </div>

    <div class="panels">
      <div class="panel">
        <InboxManager />
      </div>
      <div class="panel">
        <TodoManager />
      </div>
      <div class="panel">
        <VaultTodoManager />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-sizing: border-box;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 24px;

  .navbar-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logs-toggle {
    padding: 6px 10px;
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.2s;
  }

  .logs-toggle:hover {
    background-color: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
  }
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-title {
  margin: 0;
  color: white;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.logs-section {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.panels {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow: hidden;
  padding: 20px;
  background: #f5f7fa;
}

.panel {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
</style>
