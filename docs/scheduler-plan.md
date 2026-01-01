# Scheduler Implementation Plan

## Overview
This document outlines the plan for implementing a scheduler for the `fireflies_ingest` workflow in the productivity automation framework. The scheduler will periodically trigger the workflow based on a configurable schedule, supporting both development and production use cases.

## Schedule Requirements
- **Workflow:** `fireflies_ingest`
- **Frequency:** Twice per hour at :15 and :45 minute marks
- **Hours:** 5:00 AM - 10:00 PM (last run at 22:45)
- **Timezone:** America/New_York (Eastern Time)
- **Days:** Every day (7 days/week)
- **Total Runs:** 36 runs per day (18 hours × 2 runs/hour)

## Building Blocks

### Block 1: Schedule Configuration (settings.py)
**Goal:** Add scheduler-specific settings to the existing Settings class

**Implementation Steps:**
- [x] 1. Add `croniter` library to pyproject.toml dependencies (replaced `schedule` with cron support)
- [x] 2. Add scheduler settings fields to Settings class:
  - `scheduler_check_interval: int = 30` - Seconds between schedule checks
- [x] 3. Run `uv sync` to install new dependencies

### Block 2: Scheduler Core (scheduler/scheduler.py)
**Goal:** Implement the main scheduler loop and job registration

**Implementation Steps:**
- [x] 1. Create `SchedulerConfig` dataclass to hold job configuration (cron expression + timezone)
- [x] 2. Implement `Scheduler` class with:
  - `__init__(self, runner: Runner)` - Store runner instance
  - `register_job(self, workflow: str, cron_expression: str)` - Register workflow schedule
  - `_should_run(self, workflow: str, now: datetime) -> bool` - Check if job should run
  - `_create_context(self, workflow: str) -> RunContext` - Build RunContext with scheduled trigger
  - `run(self)` - Main loop that checks schedule and triggers workflows
  - `_write_pid_file(self)` - Write process ID to file for startup script detection
  - `_remove_pid_file(self)` - Clean up PID file on shutdown
- [x] 3. Add hardcoded schedule for fireflies_ingest:
  - Cron expression: `15,45 5-22 * * *` (at :15 and :45 past each hour, 5 AM to 10 PM)
  - Timezone: America/New_York
- [x] 4. Implement graceful shutdown handling (SIGINT, SIGTERM)
- [x] 5. Add logging for:
  - Scheduler start/stop
  - Job registration
  - Workflow triggers
  - Errors and exceptions

### Block 3: CLI Integration (main.py)
**Goal:** Add `schedule` command to run the scheduler daemon

**Implementation Steps:**
- [x] 1. Add `schedule` subcommand to argument parser
- [x] 2. Import Scheduler class in main.py
- [x] 3. Implement `run_scheduler()` function:
  - Configure logging for scheduler mode
  - Create Scheduler instance with Runner
  - Register fireflies_ingest job
  - Start scheduler loop
- [x] 4. Update command routing to handle `schedule` command

### Block 4: Trigger Type Extension (common/types.py)
**Goal:** Update Trigger to support scheduled execution

**Implementation Steps:**
- [x] 1. Add "scheduled" to Trigger.type Literal type options
- [x] 2. Document expected params for scheduled triggers:
  - `schedule`: Schedule description (e.g., "15,45 5-22 * * * America/New_York")
  - `triggered_at`: ISO timestamp when job was triggered

### Block 5: Startup Script (start_scheduler.ps1)
**Goal:** Create PowerShell script to launch scheduler at Windows startup

**Implementation Steps:**
- [x] 1. Create `start_scheduler.ps1` in project root with:
  - Change to project directory
  - Activate UV environment
  - Start scheduler with output redirect to log
  - Error handling and restart logic
- [x] 2. Add environment validation (check for `.env` file)
- [x] 3. Add process detection (prevent duplicate scheduler instances)
- [x] 4. Configure output redirection to capture startup errors
- [x] 5. Test script manually to verify it works

### Block 6: Testing & Validation
**Goal:** Verify scheduler works correctly in dev and startup scenarios

**Implementation Steps:**
- [ ] 1. Create test schedule configuration (every 2 minutes for testing)
- [ ] 2. Run scheduler manually: `uv run python main.py schedule`
- [ ] 3. Verify workflow executes at expected times
- [ ] 4. Verify state persistence between scheduled runs
- [ ] 5. Verify logs are created correctly
- [ ] 6. Test graceful shutdown (Ctrl+C)
- [ ] 7. Test startup script execution: `.\start_scheduler.ps1`
- [ ] 8. Switch to production schedule and validate timing calculation
- [ ] 9. Simulate system restart and verify auto-start

### Block 7: Windows Startup Integration
**Goal:** Configure Windows to run scheduler on boot

**Implementation Steps:**
- [x] 1. Create Windows shortcut to `start_scheduler.ps1`
- [x] 2. Place shortcut in Windows Startup folder:
  - Location: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- [x] 3. Configure shortcut properties:
  - Start in: `C:\dev\productivity`
  - Run: Minimized (optional)
- [x] 4. Test by restarting Windows
- [x] 5. Verify scheduler starts automatically
- [x] 6. Check logs to confirm successful startup
- [x] 7. **BUGFIX:** Fixed PID file path mismatch to prevent duplicate scheduler instances

### Block 8: Documentation
**Goal:** Document scheduler usage, startup, and troubleshooting

**Implementation Steps:**
- [x] 1. Update README.md with scheduler usage:
  - Starting manually: `uv run python main.py schedule`
  - Starting via script: `.\start_scheduler.ps1`
  - Environment configuration
  - Stopping the scheduler
- [x] 2. Document Windows startup setup:
  - Location of startup script
  - How to enable/disable auto-start
  - Viewing scheduler logs
- [x] 3. Add troubleshooting section:
  - How to check if scheduler is running: `Get-Process python`
  - Where to find logs
  - How to restart scheduler
  - How to modify schedule

## Technical Design Decisions

### Scheduling Library
**Decision:** Use `schedule` library with timezone support via `pytz` or Python 3.9+ `zoneinfo`
**Rationale:** Simple, readable, and sufficient for our needs. Avoids complexity of cron parsers.

### Schedule Storage
**Decision:** Hardcode fireflies_ingest schedule in scheduler.py
**Rationale:** Only one workflow needs scheduling. Can be moved to config if more workflows added later.

### Trigger Tracking
**Decision:** Store last run time in scheduler state file separate from workflow state
**Rationale:** Prevents missed runs if workflow state is reset. Scheduler state is independent concern.

### Error Handling
**Decision:** Log errors but continue running on individual workflow failures
**Rationale:** One failed workflow shouldn't stop entire scheduler. Track failures in logs for investigation.

### Startup Mode
**Decision:** Use PowerShell script in Windows Startup folder for auto-start
**Rationale:** Simple, user-level solution that doesn't require admin rights. More accessible than Task Scheduler or Windows services. Easy to enable/disable by adding/removing shortcut.

## Environment Variables
All existing settings from `.env` will be used by scheduler:
- `RUNTIME_ROOT` - For logs and state
- `LOG_LEVEL` - Logging verbosity
- `FIREFLIES_API_KEY` - Required for fireflies_ingest workflow
- `OBSIDIAN_VAULT_DIR` - Output directory for workflow

New optional settings:
- `SCHEDULER_ENABLED=true` - Enable scheduler (default: false)
- `SCHEDULER_TIMEZONE=America/New_York` - Timezone for schedule
- `SCHEDULER_C (Windows Startup):** 
  - Scheduler runs automatically on Windows login
  - Managed via `start_scheduler.ps1` script
  - No admin rights required (user-level startup)
- **Updates:** 
  - Stop scheduler: Find process with `Get-Process python`, then `Stop-Process -Id <PID>`
  - Pull code changes
  - Restart scheduler: `.\start_scheduler.ps1`
- **Monitoring:** 
  - Check if running: `Get-Process python | Where-Object {$_.CommandLine -like '*schedule*'}`
  - View logs: `{RUNTIME_ROOT}/logs/scheduler.log`
  - Startup errors: Check redirected output from `start_scheduler.ps1
- **Development:** Run manually in terminal, use Ctrl+C to stop
- **Production:** Use Windows Task Scheduler or nssm to run as Windows service
- **Updates:** Stop scheduler, pull changes, restart scheduler
- **Monitoring:** Check logs in `{RUNTIME_ROOT}/logs/scheduler.log`

## Future Enhancements
- [ ] Support multiple workflow schedules via config file
- [ ] Add web UI for schedule management
- [ ] Implement email/webhook notifications for failures
- [ ] Add metrics and monitoring (run counts, success rates, duration)
- [ ] Support cron expressions for more flexible scheduling
