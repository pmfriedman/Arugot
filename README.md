# Arugot

Your command center for work and life. Arugot transforms your Obsidian vault into a living system that captures what matters, surfaces what needs attention, and evolves with you. Start by managing everything manually, then gradually automate as your workflows crystallize—no premature optimization, no rigid structures, just a flexible foundation that grows with your needs.

## Core Concept: The Inbox Pattern

Work flows through an Inbox in three steps:

1. **Create notification** in `_inbox/` when something needs attention
2. **Process however you want**: Manual, Copilot-assisted, or automated
3. **Mark complete**: Move to `_archive/` when done

### Key Principles

**Notifications ≠ Artifacts**  
The Inbox contains messages about work needing attention. Messages point to source artifacts stored elsewhere—they don't contain the content themselves.

**Processing is your choice**  
Manual, Copilot-assisted, or automated. The Inbox doesn't dictate how you work.

**Explicit completion**  
When done, move notification to `_archive/`. Source artifacts stay where they are.

### Vault Structure

**Required:**
- `_inbox/` - Active notifications
- `_archive/` - Completed notifications

**Everything else is up to you:**
- Where artifacts live
- Folder structure
- Notification format
- How notifications are created

The Inbox is just the coordination layer.

---

## Workflows

Workflows are built on top of the Inbox pattern. They automate specific tasks but remain secondary to the core Inbox flow.

### The Workflow Contract

Every workflow must define:

```python
async def run(context: RunContext, state: dict) -> dict:
    """
    The workflow entry point.
    
    Args:
        context: Contains vault_dir, args, trigger info, dry_run flag
        state: Persisted dict from previous runs
    
    Returns:
        Updated state dict to persist
    """
    pass

DESCRIPTION = "One-line description shown by 'list' command"
```

### What the Framework Provides

- **State management**: Persist data between runs via the returned dict
- **Logging**: Use `logging.getLogger(__name__)` for consistent logging
- **Settings access**: Use `from settings import settings` for configuration
- **Idempotence**: Workflows should be safe to run repeatedly
- **Dry-run support**: Respect `context.dry_run` flag for read-only testing

### Design Philosophy

**Start Simple** - Build the minimal workflow that solves your problem, refactor later

**Composition Over Inheritance** - Share functionality through utility modules, not base classes

**Clear Boundaries** - Each workflow has one clear purpose

**Implementation Freedom** - How you accomplish the task is entirely up to you

The framework provides state, logging, and settings—everything else is your choice.

### Documentation Convention

Each workflow should:
- Live in its own folder under `workflows/`
- Include a `[workflow-name].md` file documenting its purpose, design decisions, and usage

This keeps workflow-specific details close to the code without bloating the main README.

---

## Features

- **Workflow System**: Extensible workflow architecture with state persistence
- **Scheduler**: Automated workflow execution based on cron schedules
- **State Management**: JSON-based state tracking for each workflow
- **Robust Logging**: Centralized logging to console and files
- **Environment Configuration**: All settings via `.env` file

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
   ```sh
   cd c:\dev\Arugot
   ```

2. Create a `.env` file with required settings:
   ```env
   RUNTIME_ROOT=C:\dev\productivity_runtime
   LOG_LEVEL=INFO
   OBSIDIAN_VAULT_DIR=C:\path\to\obsidian\vault
   ```

3. Install dependencies:
   ```sh
   uv sync
   ```

### Basic Usage

List available workflows:
```sh
uv run python main.py list
```

Run a workflow:
```sh
uv run python main.py run <workflow_name> [--arg key=value ...] [--dry-run]
```

Start the scheduler:
```sh
uv run python main.py schedule
```

### Tool Customizations

#### Obsidian

- Location for attachments: /assets/images
- Automatically Update Internal Links
- Hotkey for strikethrough (ctrl-hyphen)
- Hotkey for Move To A Different Folder (ctrl-shift-A)

#### AutoHotKey

```autohotkey
#Requires AutoHotkey v2.0

; Create meeting in vault.  Replace file paths to code and uv as needed
^+m::Run A_ComSpec ' /c "cd /d C:\dev\Arugot && C:\Users\phili\.local\bin\uv.exe run python main.py new meeting"'

; Markdown Checkbox
^1::  ; Ctrl+1
{
    Send "{Home}"
    Sleep 20
    Send "- [ ] "
}

---

## Primary Workflows

*(This section will document specific workflows you build on top of the Inbox pattern)*
