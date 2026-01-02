# Arugot

A modular Python automation framework for Obsidian vaults. Orchestrates workflows that ingest external data, surface actionable items, and enrich your personal knowledge base through scheduled, idempotent processing.

## Features

- **Workflow System**: Extensible workflow architecture with state persistence
- **Scheduler**: Automated workflow execution based on cron schedules
- **State Management**: JSON-based state tracking for each workflow
- **Robust Logging**: Centralized logging to console and files
- **Environment Configuration**: All settings via `.env` file
- **Windows Startup Integration**: Auto-start scheduler on system boot

## Vault Organization

The Obsidian vault is organized into three layers:

- **`_ingest/`** - Raw data from external systems (APIs, tools, files)
- **`_scratch/`** - Scratchpad for work-in-progress: `auto/` (machine workspace) and `human/` (human workspace for notes, todos, drafts)
- **Root-level notes** - Your source of truth, organized however you like (AI-powered search reduces need for strict folder hierarchies)

## Workflow Philosophy

Workflows are organized by layer transitions:

- **Ingest workflows** - Fetch from external sources (APIs, files, tools) → write to `_ingest/`
  - Naming: `ingest_[source]` (e.g., `ingest_fireflies`, `ingest_github_pr`)
- **Extractor workflows** - Surface raw data from `_ingest/` → create records in `_scratch/auto/` for further processing
  - Naming: `extract_[domain]` (e.g., `extract_meetings`, `extract_github_pr`)
- **Synth workflows** - Analyze `_scratch/` and existing notes → propose changes to enrich curated content
  - Naming: `synth_[purpose]` (e.g., `synth_weekly_review`)

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
   ```sh
   cd c:\dev\productivity
   ```

2. Create a `.env` file with required settings:
   ```env
   RUNTIME_ROOT=C:\dev\productivity_runtime
   LOG_LEVEL=INFO
   FIREFLIES_API_KEY=your_api_key_here
   OBSIDIAN_VAULT_DIR=C:\path\to\obsidian\vault
   ```

3. Install dependencies:
   ```sh
   uv sync
   ```

## Usage

### Running Workflows Manually

Run a workflow once:
```sh
uv run python main.py run <workflow_name> [--arg key=value ...] [--dry-run]
```

Example:
```sh
uv run python main.py run ingest_fireflies
```

List available workflows:
```sh
uv run python main.py list
```

### Running the Scheduler

The scheduler automatically runs workflows based on configured schedules.

#### Manual Start (Development)

Start the scheduler in your terminal:
```sh
uv run python main.py schedule
```

Stop with `Ctrl+C` for graceful shutdown.

#### Automated Start (Production)

Use the PowerShell startup script:
```sh
.\start_scheduler.ps1
```

The script will:
- Check for duplicate scheduler instances
- Activate the UV environment
- Start the scheduler in the background
- Redirect output to logs

#### Windows Startup Integration

To run the scheduler automatically when Windows starts:

1. A shortcut to `start_scheduler.ps1` should already be in your Windows Startup folder:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Productivity Scheduler.lnk
   ```

2. The scheduler will start automatically on next login/restart

3. To disable auto-start: Delete or move the shortcut from the Startup folder

#### Stopping the Scheduler

Find the running scheduler process:
```powershell
Get-Process python | Where-Object {$_.CommandLine -like '*schedule*'}
```

Stop it by ID:
```powershell
Stop-Process -Id <PID>
```

Or stop all Python processes (use with caution):
```powershell
Get-Process python | Stop-Process
```

### Viewing Logs

Logs are stored in `{RUNTIME_ROOT}/logs/`:
- **scheduler.log**: Scheduler activity and workflow triggers
- **{workflow_name}.log**: Individual workflow execution logs

View scheduler log:
```powershell
Get-Content C:\dev\productivity_runtime\logs\scheduler.log -Tail 50 -Wait
```

### Checking Scheduler Status

Check if scheduler is running:
```powershell
Get-Process python | Where-Object {$_.CommandLine -like '*schedule*'}
```

Check the PID file:
```powershell
Test-Path C:\dev\productivity_runtime\scheduler.pid
Get-Content C:\dev\productivity_runtime\scheduler.pid
```

## Configuration

All configuration is done via the `.env` file in the project root.

## Updating the Scheduler

To update the scheduler code or configuration:

1. Stop the running scheduler:
   ```powershell
   Get-Process python | Where-Object {$_.CommandLine -like '*schedule*'} | Stop-Process
   ```

2. Pull the latest code:
   ```sh
   git pull
   uv sync
   ```

3. Update `.env` if needed

4. Restart the scheduler:
   ```sh
   .\start_scheduler.ps1
   ```