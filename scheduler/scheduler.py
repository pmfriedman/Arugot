"""
Scheduler emits RunContext objects.
No execution logic lives here.
"""

import logging
import signal
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo
import uuid

from croniter import croniter

from common.types import RunContext, Trigger
from runner.runner import Runner
from settings import settings


logger = logging.getLogger(__name__)


@dataclass
class SchedulerConfig:
    """Configuration for a scheduled job."""

    workflow: str
    cron_expression: str  # Standard cron format (e.g., "15,45 5-22 * * *")
    timezone: str  # Timezone string (e.g., "America/New_York")


class Scheduler:
    """Main scheduler that triggers workflows based on cron schedules."""

    def __init__(self, runner: Runner):
        """Initialize scheduler with a workflow runner."""
        self.runner = runner
        self.jobs: Dict[str, SchedulerConfig] = {}
        self.last_run: Dict[str, datetime] = {}
        self.running = False
        self._setup_signal_handlers()
        self._register_default_jobs()
        logger.info("Scheduler initialized")
    
    def _register_default_jobs(self):
        """Register default hardcoded schedules for workflows."""
        # Fireflies ingest: Run at :15 and :45 past each hour from 5 AM to 10 PM
        self.register_job(
            workflow="fireflies_ingest",
            cron_expression="15,45 5-22 * * *",
            timezone="America/New_York"
        )

    def _setup_signal_handlers(self):
        """Set up graceful shutdown on SIGINT and SIGTERM."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def register_job(self, workflow: str, cron_expression: str, timezone: str):
        """Register a workflow to run on a cron schedule."""
        config = SchedulerConfig(
            workflow=workflow, cron_expression=cron_expression, timezone=timezone
        )
        self.jobs[workflow] = config
        logger.info(
            f"Registered job: {workflow} with schedule '{cron_expression}' in {timezone}"
        )

    def _should_run(self, workflow: str, now: datetime) -> bool:
        """Check if a workflow should run at the current time."""
        if workflow not in self.jobs:
            return False

        config = self.jobs[workflow]
        tz = ZoneInfo(config.timezone)
        now_tz = now.astimezone(tz)

        # Get the last run time (or epoch if never run)
        last_run = self.last_run.get(workflow)
        if last_run is None:
            last_run = datetime.fromtimestamp(0, tz=tz)

        # Calculate next scheduled run after last_run
        cron = croniter(config.cron_expression, last_run)
        next_run = cron.get_next(datetime)

        # Should run if current time has passed the next scheduled time
        return now_tz >= next_run

    def _create_context(self, workflow: str) -> RunContext:
        """Create a RunContext for a scheduled workflow execution."""
        config = self.jobs[workflow]
        tz = ZoneInfo(config.timezone)
        triggered_at = datetime.now(tz)

        trigger = Trigger(
            type="scheduled",
            params={
                "schedule": config.cron_expression,
                "triggered_at": triggered_at.isoformat(),
                "timezone": config.timezone,
            },
        )

        return RunContext(
            workflow=workflow,
            trigger=trigger,
            run_id=str(uuid.uuid4()),
            started_at=triggered_at,
            args={},
        )

    def _write_pid_file(self):
        """Write process ID to file for startup script detection."""
        if settings.runtime_root:
            pid_file = Path(settings.runtime_root) / "scheduler.pid"
            pid_file.write_text(str(Path.cwd().resolve()))
            logger.info(f"Wrote PID file to {pid_file}")

    def _remove_pid_file(self):
        """Clean up PID file on shutdown."""
        if settings.runtime_root:
            pid_file = Path(settings.runtime_root) / "scheduler.pid"
            if pid_file.exists():
                pid_file.unlink()
                logger.info(f"Removed PID file {pid_file}")

    def run(self):
        """Main scheduler loop - checks schedule and triggers workflows."""
        logger.info("Starting scheduler loop")
        self.running = True
        self._write_pid_file()

        try:
            while self.running:
                now = datetime.now()

                for workflow in self.jobs:
                    try:
                        if self._should_run(workflow, now):
                            logger.info(
                                f"Triggering scheduled run for workflow: {workflow}"
                            )
                            context = self._create_context(workflow)

                            # Run the workflow through the runner
                            self.runner.run(context)

                            # Update last run time
                            config = self.jobs[workflow]
                            tz = ZoneInfo(config.timezone)
                            self.last_run[workflow] = datetime.now(tz)
                            logger.info(
                                f"Completed scheduled run for workflow: {workflow}"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error running scheduled workflow {workflow}: {e}",
                            exc_info=True,
                        )

                # Sleep for configured interval
                time.sleep(settings.scheduler_check_interval)

        except Exception as e:
            logger.error(f"Scheduler loop error: {e}", exc_info=True)
        finally:
            self._remove_pid_file()
            logger.info("Scheduler stopped")
