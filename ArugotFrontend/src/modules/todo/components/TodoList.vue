<script setup lang="ts">
import { computed } from "vue";
import draggable from "vuedraggable";
import TodoItem from "./TodoItem.vue";
import type { TodoItem as TodoItemType } from "../utils/markdownParser";

const props = defineProps<{
  items: TodoItemType[];
}>();

const emit = defineEmits<{
  "update:items": [items: TodoItemType[]];
  toggle: [id: string];
  "update-text": [id: string, text: string];
  delete: [id: string];
}>();

// Create a computed property for two-way binding with draggable
const localItems = computed({
  get: () => props.items,
  set: (value) => {
    // Update order property based on new positions
    const reordered = value.map((item, index) => ({
      ...item,
      order: index,
    }));
    emit("update:items", reordered);
  },
});

const handleToggle = (id: string) => {
  emit("toggle", id);
};

const handleUpdateText = (id: string, text: string) => {
  emit("update-text", id, text);
};

const handleDelete = (id: string) => {
  emit("delete", id);
};
</script>

<template>
  <div class="todo-list">
    <draggable
      v-model="localItems"
      item-key="id"
      handle=".drag-handle"
      animation="200"
      ghost-class="ghost"
      drag-class="dragging"
    >
      <template #item="{ element }">
        <TodoItem
          :item="element"
          @toggle="handleToggle"
          @update-text="handleUpdateText"
          @delete="handleDelete"
        />
      </template>
    </draggable>

    <div v-if="items.length === 0" class="empty-state">
      No todo items yet. Start typing in the editor below!
    </div>
  </div>
</template>

<style scoped>
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-style: italic;
}

/* Dragging styles */
.ghost {
  opacity: 0.5;
  background: #f0f0f0;
}

.dragging {
  opacity: 0.8;
  transform: rotate(2deg);
  cursor: grabbing !important;
}
</style>
