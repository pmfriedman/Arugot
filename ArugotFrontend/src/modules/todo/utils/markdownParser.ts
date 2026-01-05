export interface TodoItem {
  id: string;
  text: string;
  completed: boolean;
  order: number;
}

export interface ParseResult {
  success: boolean;
  todos: TodoItem[];
  error?: string;
  errorLine?: number;
}

/**
 * Parse markdown content into structured todo items
 * Strictly validates that all non-blank lines are valid checkboxes
 * Supports: - [ ] unchecked and - [x] or - [X] checked
 */
export function parseMarkdownTodos(markdown: string): ParseResult {
  const lines = markdown.split("\n");
  const todos: TodoItem[] = [];

  // Regex to match valid checkbox lines
  // - [ ] for unchecked or - [x] / - [X] for checked
  const checkboxRegex = /^- \[([ xX])\] (.*)$/;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;

    const trimmedLine = line.trim();

    // Skip blank lines
    if (trimmedLine === "") {
      continue;
    }

    // Check if line matches checkbox format
    const match = line.match(checkboxRegex);

    if (!match) {
      return {
        success: false,
        todos: [],
        error: `Invalid format: Line must be a checkbox (- [ ] or - [x])`,
        errorLine: i + 1,
      };
    }

    const checkbox = match[1];
    const text = match[2];

    if (!checkbox || text === undefined) {
      return {
        success: false,
        todos: [],
        error: `Invalid format: Line must be a checkbox (- [ ] or - [x])`,
        errorLine: i + 1,
      };
    }

    const completed = checkbox.toLowerCase() === "x";

    todos.push({
      id: generateTodoId(),
      text: text,
      completed: completed,
      order: todos.length,
    });
  }

  return {
    success: true,
    todos: todos,
  };
}

/**
 * Serialize todo items back to markdown format
 */
export function serializeTodosToMarkdown(todos: TodoItem[]): string {
  return todos
    .map((todo) => {
      const checkbox = todo.completed ? "[x]" : "[ ]";
      return `- ${checkbox} ${todo.text}`;
    })
    .join("\n");
}

/**
 * Generate unique ID for todo items
 */
export function generateTodoId(): string {
  return `todo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
