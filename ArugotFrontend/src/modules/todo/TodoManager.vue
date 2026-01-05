<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useVaultDirectory } from "../../composables/useVaultDirectory";
import { useAutoSave } from "./composables/useAutoSave";
import { useFileWatcher } from "./composables/useFileWatcher";
import {
  parseMarkdownTodos,
  serializeTodosToMarkdown,
  type TodoItem,
  type ParseResult,
} from "./utils/markdownParser";
import TodoList from "./components/TodoList.vue";

const GLOBAL_TODO_FILE = "Global TODO.md";

const error = ref<string>("");
const parseError = ref<string>("");
const fileContent = ref<string>("");
const isSaving = ref<boolean>(false);
const fileExists = ref<boolean>(false);

// Check if File System Access API is supported
const isSupported = "showDirectoryPicker" in window;

// Composables
const { vaultDirectory, readFile, writeFile } = useVaultDirectory();
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
    return parseResult.value.todos.filter((todo) => !todo.completed);
  } else {
    parseError.value = `Line ${parseResult.value.errorLine}: ${parseResult.value.error}`;
    return [];
  }
});

const hasValidFormat = computed(() => parseResult.value.success);

const loadFile = async () => {
  if (!vaultDirectory.value) return;

  try {
    error.value = "";
    const content = await readFile(GLOBAL_TODO_FILE);

    if (content === null) {
      fileExists.value = false;
      error.value = `File "${GLOBAL_TODO_FILE}" not found in vault root. Please create this file in your Obsidian vault.`;
      fileContent.value = "";
      return;
    }

    fileExists.value = true;
    fileContent.value = content;

    // Start watching for external changes with auto-reload
    const fileHandle = await vaultDirectory.value.getFileHandle(
      GLOBAL_TODO_FILE,
      { create: false }
    );
    if (fileHandle) {
      startWatching(fileHandle, 2000, async (event) => {
        console.log("External file change detected, auto-reloading...", event);
        await handleAutoReload();
      });
    }
  } catch (err: any) {
    fileExists.value = false;
    error.value = `Error reading "${GLOBAL_TODO_FILE}": ${err.message}`;
  }
};

const handleAutoReload = async () => {
  try {
    const content = await readFile(GLOBAL_TODO_FILE);
    if (content !== null) {
      fileContent.value = content;
      clearExternalChanges();

      // Update tracked state after reload
      const fileHandle = await vaultDirectory.value?.getFileHandle(
        GLOBAL_TODO_FILE,
        { create: false }
      );
      if (fileHandle) {
        await updateTrackedState(fileHandle);
      }
    }
  } catch (err: any) {
    error.value = `Error auto-reloading file: ${err.message}`;
  }
};

const saveFile = async () => {
  if (!vaultDirectory.value || !fileExists.value) return;

  try {
    error.value = "";
    isSaving.value = true;

    const success = await writeFile(GLOBAL_TODO_FILE, fileContent.value);
    if (!success) {
      error.value = `Error saving "${GLOBAL_TODO_FILE}"`;
      return;
    }

    // Update tracked state after save to prevent false positive detection
    const fileHandle = await vaultDirectory.value.getFileHandle(
      GLOBAL_TODO_FILE,
      { create: false }
    );
    if (fileHandle) {
      await updateTrackedState(fileHandle);
    }
  } catch (err: any) {
    error.value = `Error saving file: ${err.message}`;
  } finally {
    isSaving.value = false;
  }
};

// Auto-save setup
useAutoSave(fileContent, saveFile, {
  debounceMs: 1000,
  enabled: computed(
    () => !!vaultDirectory.value && fileExists.value && hasValidFormat.value
  ),
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

// Watch for vault directory changes and load the file
watch(
  vaultDirectory,
  async (newVault) => {
    if (newVault) {
      await loadFile();
    } else {
      fileContent.value = "";
      fileExists.value = false;
      error.value = "";
    }
  },
  { immediate: true }
);
</script>

<template>
  <div class="todo-manager">
    <div class="header">
      <h2>Global TODO</h2>
      <p class="subtitle">Manage tasks from {{ GLOBAL_TODO_FILE }}</p>
    </div>

    <div v-if="!isSupported" class="error">
      ⚠️ File System Access API is not supported in this browser. Please use
      Chrome, Edge, or Opera.
    </div>

    <div v-if="isSupported && vaultDirectory && fileExists" class="controls">
      <span v-if="isSaving" class="saving-indicator">💾 Saving...</span>
      <span
        v-if="isWatching"
        class="watching-indicator"
        title="Automatically reloading on external changes"
        >👁️</span
      >
    </div>

    <div v-if="error" class="error">❌ {{ error }}</div>

    <div v-if="parseError" class="error">
      ❌ Invalid file format: {{ parseError }}
    </div>

    <!-- Checkbox UI -->
    <TodoList
      v-if="vaultDirectory && fileExists && hasValidFormat"
      :items="todos"
      @toggle="handleToggle"
      @update-text="handleUpdateText"
      @delete="handleDelete"
      @update:items="handleUpdateItems"
    />

    <!-- Raw markdown editor (fallback for invalid format) -->
    <div v-if="vaultDirectory && fileExists && !hasValidFormat" class="editor">
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

    <div v-if="!vaultDirectory && isSupported" class="instructions">
      <h3>Getting Started:</h3>
      <p>1. Select your Obsidian vault using the vault picker above</p>
      <p>2. Ensure "{{ GLOBAL_TODO_FILE }}" exists in the vault root</p>
      <p>3. Edit tasks directly in the interface</p>
      <p>4. Changes auto-save after 1 second of inactivity! 🎉</p>
    </div>
  </div>
</template>

<style scoped>
.todo-manager {
  padding: 1rem;
}

.header {
  margin-bottom: 1.5rem;
}

.header h2 {
  color: #42b883;
  margin: 0 0 0.25rem 0;
}

.subtitle {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: #607d8b;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #455a64;
}

.btn-secondary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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

.error {
  background: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #c00;
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
