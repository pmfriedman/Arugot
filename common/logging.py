"""Logging infrastructure for the automation framework.

No side effects at import time - logging must be explicitly configured.
"""

import logging
import sys
from pathlib import Path

from settings import settings


# Track if logging has been configured to ensure idempotency
_configured = False


def configure_logging(workflow: str | None = None) -> None:
    """Configure logging for the automation framework.

    Sets up console and file handlers with consistent formatting.

    Args:
        workflow: Optional workflow name. If provided, creates a workflow-specific log file.

    Handlers created:
        - Console handler (stdout)
        - File handler: {runtime_root}/logs/automation.log
        - File handler (if workflow): {runtime_root}/logs/{workflow}.log
    """
    global _configured

    # Get the root logger
    root_logger = logging.getLogger()

    # If already configured, remove existing handlers to avoid duplicates
    if _configured:
        root_logger.handlers.clear()

    # Parse and validate log level
    log_level_str = settings.log_level.upper()
    log_level = getattr(logging, log_level_str, None)
    if not isinstance(log_level, int):
        log_level = logging.INFO

    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Ensure logs directory exists
    runtime_root = Path(settings.runtime_root)
    logs_dir = runtime_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # File handler: automation.log
    automation_log_path = logs_dir / "automation.log"
    automation_handler = logging.FileHandler(automation_log_path, encoding="utf-8")
    automation_handler.setLevel(log_level)
    automation_handler.setFormatter(formatter)
    root_logger.addHandler(automation_handler)

    # Workflow-specific file handler (if workflow provided)
    if workflow:
        workflow_log_path = logs_dir / f"{workflow}.log"
        workflow_handler = logging.FileHandler(workflow_log_path, encoding="utf-8")
        workflow_handler.setLevel(log_level)
        workflow_handler.setFormatter(formatter)
        root_logger.addHandler(workflow_handler)

    _configured = True
