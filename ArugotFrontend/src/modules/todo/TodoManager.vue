<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useFileHandle } from "./composables/useFileHandle";
import { useFileIO } from "./composables/useFileIO";
import { useAutoSave } from "./composables/useAutoSave";
import { useFileWatcher } from "./composables/useFileWatcher";
import {
  parseMarkdownTodos,
  serializeTodosToMarkdown,
  type TodoItem,
  type ParseResult,
} from "./utils/markdownParser";
import TodoList from "./components/TodoList.vue";

const error = ref<string>("");
const parseError = ref<string>("");

// Check if File System Access API is supported
const isSupported = "showOpenFilePicker" in window;

// Composables
const { fileHandle, fileName, isRestoring, openFilePicker, restoreFileHandle } =
  useFileHandle();
const { fileContent, permissionStatus, isSaving, readFile, writeFile } =
  useFileIO();
const { isWatching, startWatching, clearExternalChanges, updateTrackedState } =
  useFileWatcher();

// Parse markdown into structured TodoItems
const parseResult = computed<ParseResult>(() => {
  if (!fileContent.value) {
    return { success: true, todos: [] };
  }
  return parseMarkdownTodos(fileContent.value);
});

const todos = computed<TodoItem[]>(() => {
  if (parseResult.value.success) {
    parseError.value = "";
    return parseResult.value.todos;
  } else {
    parseError.value = `Line ${parseResult.value.errorLine}: ${parseResult.value.error}`;
    return [];
  }
});

const hasValidFormat = computed(() => parseResult.value.success);
// TODO: Parse markdown into structured TodoItems
// const todos = computed(() => parseMarkdownTodos(fileContent.value));

const handleOpenFile = async () => {
  try {
    error.value = "";

    const result = await openFilePicker();
    if (result) {
      await loadFile();
    }
  } catch (err: any) {
    error.value = `Error opening file: ${err.message}`;
  }
};

const loadFile = async () => {
  try {
    await readFile(fileHandle.value);

    // Start watching for external changes with auto-reload
    if (fileHandle.value) {
      startWatching(fileHandle.value, 2000, async (event) => {
        console.log("External file change detected, auto-reloading...", event);
        await handleAutoReload();
      });
    }
  } catch (err: any) {
    error.value = `Error reading file: ${err.message}`;
  }
};

const handleAutoReload = async () => {
  try {
    await readFile(fileHandle.value);
    clearExternalChanges();

    // Update tracked state after reload
    if (fileHandle.value) {
      await updateTrackedState(fileHandle.value);
    }
  } catch (err: any) {
    error.value = `Error auto-reloading file: ${err.message}`;
  }
};

const handleReload = async () => {
  try {
    error.value = "";
    await readFile(fileHandle.value);
    clearExternalChanges();

    // Update tracked state after reload
    if (fileHandle.value) {
      await updateTrackedState(fileHandle.value);
    }
  } catch (err: any) {
    error.value = `Error reloading file: ${err.message}`;
  }
};

const saveFile = async () => {
  if (!fileHandle.value) return;

  try {
    error.value = "";

    await writeFile(fileHandle.value, fileContent.value);

    // Update tracked state after save to prevent false positive detection
    await updateTrackedState(fileHandle.value);
  } catch (err: any) {
    error.value = `Error saving file: ${err.message}`;
  }
};

// Auto-save setup
useAutoSave(fileContent, saveFile, {
  debounceMs: 1000,
  enabled: computed(() => !!fileHandle.value && hasValidFormat.value),
});

// Handle todo item events
const handleToggle = (id: string) => {
  const updated = todos.value.map((todo) =>
    todo.id === id ? { ...todo, completed: !todo.completed } : todo
  );
  fileContent.value = serializeTodosToMarkdown(updated);
};

const handleUpdateText = (id: string, text: string) => {
  const updated = todos.value.map((todo) =>
    todo.id === id ? { ...todo, text } : todo
  );
  fileContent.value = serializeTodosToMarkdown(updated);
};

const handleDelete = (id: string) => {
  const updated = todos.value.filter((todo) => todo.id !== id);
  fileContent.value = serializeTodosToMarkdown(updated);
};

const handleUpdateItems = (items: TodoItem[]) => {
  fileContent.value = serializeTodosToMarkdown(items);
};

// Restore file handle on mount
onMounted(async () => {
  if (!isSupported) return;

  const restored = await restoreFileHandle();
  if (restored) {
    await loadFile();
  }
});

// - Delete item
// - Reorder items
// - Serialize back to markdown and update fileContent
</script>

<template>
  <div class="todo-manager">
    <h1>TODO List Manager</h1>

    <div v-if="!isSupported" class="error">
      ⚠️ File System Access API is not supported in this browser. Please use
      Chrome, Edge, or Opera.
    </div>

    <div v-if="isSupported" class="controls">
      <button @click="handleOpenFile" class="btn btn-primary">
        {{ fileHandle ? "📂 Open Different File" : "📂 Open TODO File" }}
      </button>

      <button v-if="fileHandle" @click="handleReload" class="btn btn-secondary">
        🔄 Reload
      </button>

      <span v-if="isSaving" class="saving-indicator">💾 Saving...</span>
      <span
        v-if="isWatching"
        class="watching-indicator"
        title="Watching for external changes"
        >👁️</span
      >
    </div>

    <div v-if="fileName" class="file-info">
      <h3>Current File:</h3>
      <p>
        <strong>📄 {{ fileName }}</strong>
      </p>
      <p v-if="permissionStatus" class="permission-status">
        {{ permissionStatus }}
      </p>
    </div>

    <div v-if="error" class="error">❌ {{ error }}</div>

    <div v-if="parseError" class="error">
      ❌ Invalid file format: {{ parseError }}
    </div>

    <!-- Checkbox UI -->
    <TodoList
      v-if="fileHandle && hasValidFormat"
      :items="todos"
      @toggle="handleToggle"
      @update-text="handleUpdateText"
      @delete="handleDelete"
      @update:items="handleUpdateItems"
    />

    <!-- Raw markdown editor (fallback for invalid format) -->
    <div v-if="fileHandle && !hasValidFormat" class="editor">
      <h3>Raw Markdown (Fix format errors):</h3>
      <textarea
        v-model="fileContent"
        placeholder="Your TODO list content..."
        spellcheck="false"
      ></textarea>
      <div class="editor-info">
        Lines: {{ fileContent.split("\n").length }} | Characters:
        {{ fileContent.length }}
      </div>
    </div>

    <div v-if="!fileHandle && isSupported && !isRestoring" class="instructions">
      <h3>Getting Started:</h3>
      <p>1. Click "Open TODO File" to select your markdown file</p>
      <p>2. Edit the content in the text area</p>
      <p>3. Changes auto-save after 1 second of inactivity!</p>
      <p>
        4. Your file will automatically reload when you refresh the page! 🎉
      </p>
    </div>
  </div>
</template>

<style scoped>
.todo-manager {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #42b883;
  margin-bottom: 2rem;
}

.info {
  background: #e3f2fd;
  color: #1976d2;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #2196f3;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.saving-indicator {
  color: #2196f3;
  font-weight: 500;
  animation: pulse 1s ease-in-out infinite;
}

.watching-indicator {
  color: #666;
  font-size: 1.2rem;
  cursor: help;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.warning {
  background: #fff3e0;
  color: #e65100;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #ff9800;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.btn-inline {
  padding: 0.5rem 1rem;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-inline:hover {
  background: #f57c00;
  transform: translateY(-1px);
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-secondary {
  background: #607d8b;
  color: white;
}

.file-info {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.file-info h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.file-info p {
  margin: 0.5rem 0;
}

.permission-status {
  color: #666;
  font-size: 0.9rem;
}

.modified-indicator {
  color: #ff9800;
  font-weight: bold;
}

.error {
  background: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #c00;
}

.success {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #2e7d32;
}

.editor {
  margin-top: 2rem;
}

.editor h3 {
  margin-bottom: 0.5rem;
}

textarea {
  width: 100%;
  min-height: 400px;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
}

textarea:focus {
  outline: none;
  border-color: #42b883;
}

.editor-info {
  margin-top: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.instructions {
  background: #e3f2fd;
  padding: 1.5rem;
  border-radius: 6px;
  margin-top: 2rem;
  border-left: 4px solid #2196f3;
}

.instructions h3 {
  margin-top: 0;
  color: #1976d2;
}

.instructions p {
  margin: 0.5rem 0;
  color: #333;
}
</style>
