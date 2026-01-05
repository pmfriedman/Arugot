<script setup lang="ts">
import TodoManager from "./modules/todo/TodoManager.vue";
import VaultTodoManager from "./modules/vaultTodo/VaultTodoManager.vue";
</script>

<template>
  <div class="app-container">
    <div class="panel">
      <TodoManager />
    </div>
    <div class="panel">
      <VaultTodoManager />
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  gap: 20px;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.panel {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: white;
}
</style>
