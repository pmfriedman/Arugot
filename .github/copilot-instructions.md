# Copilot Instructions for Arugot

## Overview
This project is a modular Python automation framework for Obsidian vaults. It orchestrates workflows that ingest external data, surface actionable items, and enrich your personal knowledge base through scheduled, idempotent processing. The vault is organized into three layers: `_ingest/` (raw data), `_scratch/` (work-in-progress), and root-level notes (curated content).

## Development Workflow

1. **Define Steps First**: When starting a new building block or section in the plan, first add the numbered implementation steps to the plan document
2. **Wait for Step Approval**: Wait for user approval of the proposed steps before beginning implementation
3. **One Step at a Time**: Implement only ONE step at a time, never multiple steps in sequence
4. **Wait for Implementation Approval**: Wait for user approval before moving to the next step
5. **Mark Complete**: Update plan documents with completed checkboxes after implementing each step
6. **Test As You Go**: Validate each building block before moving to the next
7. **Update Documentation**: Keep plan synchronized with actual implementation


## Architecture
- **Entrypoint:** `main.py` parses CLI commands (`run`, `list`, `schedule`) and dispatches to the workflow runner or scheduler.
- **Workflows:** Located in `workflows/`, each workflow is a Python module with an `async def run(context, state)` function. Examples: `workflows/example.py`, `workflows/ingest_fireflies/workflow.py`.
- **Scheduler:** `scheduler/scheduler.py` runs workflows on cron schedules with timezone support.
- **State Management:** Workflow state is persisted as JSON in `{runtime_root}/state/{workflow}.json` via `runner/state.py`.
- **Logging:** Centralized in `common/logging.py`, logs to both console and files under `{runtime_root}/logs/`.
- **Settings:** All configuration is via environment variables or `.env`, loaded by `settings.py` using `pydantic-settings`.
- **Types:** Shared data structures (e.g., `RunContext`, `Trigger`) are in `common/types.py`.
- **Workflow Example:** The `ingest_fireflies` workflow demonstrates API integration, normalization, and writing to an Obsidian vault.

## Key Patterns & Conventions

### Vault Organization
- **`_ingest/`** - Raw data from external systems (APIs, tools, files)
- **`_scratch/auto/`** - Machine workspace for work-in-progress
- **`_scratch/human/`** - Human workspace for notes, todos, drafts
- **Root-level notes** - Curated content, source of truth

### Workflow Types
- **Ingest workflows** - Fetch from external sources → write to `_ingest/`
  - Naming: `ingest_[source]` (e.g., `ingest_fireflies`, `ingest_github_pr`)
- **Extractor workflows** - Surface raw data from `_ingest/` → create records in `_scratch/auto/`
  - Naming: `extract_[domain]` (e.g., `extract_meetings`, `extract_github_pr`)
- **Synth workflows** - Analyze `_scratch/` and existing notes → propose changes to enrich curated content
  - Naming: `synth_[purpose]` (e.g., `synth_weekly_review`)

### Core Conventions
- **Workflow Contract:** Each workflow must define:
  - `async def run(context: RunContext, state: dict) -> dict` - The workflow entry point. State is a dict, persisted between runs.
  - `DESCRIPTION` (str) - A concise one-line description shown by the `list` command
- **Idempotence:** Workflows must be safe to run repeatedly. Use reconciliation patterns (check before create).
- **State Schema:** State files must be JSON objects with `version` and `data` fields. See `runner/state.py` for validation logic.
- **Logging:** Use `logging.getLogger(__name__)` and rely on `configure_logging()` for setup. Avoid side effects at import time.
- **Settings Access:** Use `from settings import settings` for all config. Do not hardcode paths or secrets.
- **Type Safety:** Use pydantic models or dataclasses for data structures. Apply type hints consistently throughout.
- Prefer composition over complex abstractions

## Developer Workflows

This project uses `uv` for Python dependency management and virtual environment handling.  When running Python commands programmatically always use `uv run` prefix.

- **List workflows:** Get a comprehensive list of all available workflows with descriptions
  ```sh
  uv run python main.py list
  ```
  Use this command when you need to discover what workflows exist and what they do.

- **Run a workflow:**
  ```sh
  uv run python main.py run <workflow> [--arg key=value ...] [--dry-run]
  ```
- **Run scheduler:**
  ```sh
  uv run python main.py schedule
  ```


