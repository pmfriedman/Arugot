<script setup lang="ts">
import { ref } from "vue";
import type { TodoItem } from "../utils/markdownParser";

const props = defineProps<{
  item: TodoItem;
}>();

const emit = defineEmits<{
  toggle: [id: string];
  "update-text": [id: string, text: string];
  delete: [id: string];
}>();

const isEditing = ref(false);
const editText = ref(props.item.text);

// TODO: Implement inline editing
// - Double-click to enable edit mode
// - Save on blur or Enter key
// - Cancel on Escape key
// - Show edit/delete controls on hover

const handleToggle = () => {
  emit("toggle", props.item.id);
};

const startEdit = () => {
  isEditing.value = true;
  editText.value = props.item.text;
};

const saveEdit = () => {
  if (editText.value.trim()) {
    emit("update-text", props.item.id, editText.value);
  }
  isEditing.value = false;
};

const cancelEdit = () => {
  editText.value = props.item.text;
  isEditing.value = false;
};

const handleDelete = () => {
  emit("delete", props.item.id);
};
</script>

<template>
  <div class="todo-item" :class="{ completed: item.completed }">
    <!-- TODO: Add drag handle icon -->
    <div class="drag-handle">⋮⋮</div>

    <input
      type="checkbox"
      :checked="item.completed"
      @change="handleToggle"
      class="checkbox"
    />

    <div v-if="!isEditing" class="todo-text" @dblclick="startEdit">
      {{ item.text }}
    </div>

    <input
      v-else
      v-model="editText"
      @blur="saveEdit"
      @keyup.enter="saveEdit"
      @keyup.escape="cancelEdit"
      class="todo-input"
      autofocus
    />

    <!-- TODO: Show controls on hover -->
    <div class="todo-actions">
      <button @click="handleDelete" class="btn-delete" title="Delete">
        🗑️
      </button>
    </div>
  </div>
</template>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  transition: all 0.2s;
}

.todo-item:hover {
  border-color: #42b883;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: #999;
}

.drag-handle {
  cursor: grab;
  color: #ccc;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.todo-text {
  flex: 1;
  cursor: text;
  padding: 0.25rem;
}

.todo-input {
  flex: 1;
  padding: 0.25rem 0.5rem;
  border: 1px solid #42b883;
  border-radius: 4px;
  font-size: 1rem;
}

.todo-input:focus {
  outline: none;
  border-color: #42b883;
}

.todo-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.todo-item:hover .todo-actions {
  opacity: 1;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.btn-delete:hover {
  opacity: 1;
}
</style>
