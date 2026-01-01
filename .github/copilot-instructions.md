# Copilot Instructions for productivity

## Overview
This project is a modular Python automation framework for running and managing workflows, with a focus on stateful, repeatable data processing. It is structured for extensibility and robust logging/state management.

## Development Workflow

1. **Define Steps First**: When starting a new building block or section in the plan, first add the numbered implementation steps to the plan document
2. **Wait for Step Approval**: Wait for user approval of the proposed steps before beginning implementation
3. **One Step at a Time**: Implement only ONE step at a time, never multiple steps in sequence
4. **Wait for Implementation Approval**: Wait for user approval before moving to the next step
5. **Mark Complete**: Update plan documents with completed checkboxes after implementing each step
6. **Test As You Go**: Validate each building block before moving to the next
7. **Update Documentation**: Keep plan synchronized with actual implementation


## Architecture
- **Entrypoint:** `main.py` parses CLI commands (`run`, `list`) and dispatches to the workflow runner.
- **Workflows:** Located in `workflows/`, each workflow is a Python module with a `run(context, state)` function. Example: `workflows/example.py`, `workflows/fireflies_ingest/workflow.py`.
- **State Management:** Workflow state is persisted as JSON in `{runtime_root}/state/{workflow}.json` via `runner/state.py`.
- **Logging:** Centralized in `common/logging.py`, logs to both console and files under `{runtime_root}/logs/`.
- **Settings:** All configuration is via environment variables or `.env`, loaded by `settings.py` using `pydantic-settings`.
- **Types:** Shared data structures (e.g., `RunContext`, `Trigger`) are in `common/types.py`.
- **Workflow Example:** The `fireflies_ingest` workflow demonstrates API integration, normalization, and writing to an Obsidian vault.

## Key Patterns & Conventions
- **Workflow Contract:** Each workflow must define `run(context: RunContext, state: dict) -> dict`. State is a dict, persisted between runs.
- **State Schema:** State files must be JSON objects with `version` and `data` fields. See `runner/state.py` for validation logic.
- **Logging:** Use `logging.getLogger(__name__)` and rely on `configure_logging()` for setup. Avoid side effects at import time.
- **Settings Access:** Use `from settings import settings` for all config. Do not hardcode paths or secrets.
- **Obsidian Integration:** For workflows writing to Obsidian, use `settings.obsidian_vault_dir` and write to `_ingest/` subfolders.
- Prefer composition over complex abstractions
- Use type hints consistently

## Developer Workflows

This project uses `uv` for Python dependency management and virtual environment handling.  When running Python commands programmatically always use `uv run` prefix.

- **Run a workflow:**
  ```sh
  uv run python main.py run <workflow> [--arg key=value ...] [--dry-run]
  ```
- **List workflows:**
  ```sh
  uv run python main.py list
  ```


