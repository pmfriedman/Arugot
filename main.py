import argparse
import importlib
import logging
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from common.logging import configure_logging
from common.types import RunContext, Trigger
from runner.runner import Runner
from scheduler.scheduler import Scheduler
from settings import settings


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("workflow", help="Workflow name")
    run_parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Workflow arg in key=value form (repeatable)",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without persisting state",
    )

    subparsers.add_parser("list")
    subparsers.add_parser("schedule", help="Run the scheduler daemon")

    new_parser = subparsers.add_parser("new", help="Create new notes")
    new_parser.add_argument("note_type", choices=["meeting"], help="Type of note to create")

    args = parser.parse_args()

    if args.command == "list":
        list_workflows()
        return
    
    if args.command == "schedule":
        run_scheduler()
        return
    
    if args.command == "new":
        create_new_note(args.note_type)
        return

    context = build_context_from_cli(args)
    configure_logging(workflow=context.workflow)

    runner = Runner()
    try:
        runner.run(context)
    except Exception:
        sys.exit(1)


def list_workflows():
    workflows_dir = Path(__file__).parent / "workflows"
    workflows = []

    # Check for top-level .py files
    for py_file in workflows_dir.glob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.startswith("_"):
            continue

        module_name = py_file.stem
        try:
            module = importlib.import_module(f"workflows.{module_name}")
            if callable(getattr(module, "run", None)):
                description = getattr(module, "DESCRIPTION", None)
                workflows.append((module_name, description))
        except Exception as e:
            logging.warning(f"Failed to import workflows.{module_name}: {e}")

    # Check for subdirectories with workflow modules
    for subdir in workflows_dir.iterdir():
        if not subdir.is_dir() or subdir.name.startswith("_"):
            continue

        module_name = subdir.name
        try:
            module = importlib.import_module(f"workflows.{module_name}")
            if callable(getattr(module, "run", None)):
                description = getattr(module, "DESCRIPTION", None)
                workflows.append((module_name, description))
        except Exception as e:
            logging.warning(f"Failed to import workflows.{module_name}: {e}")

    for name, description in sorted(workflows):
        if description:
            print(f"{name}: {description}")
        else:
            print(f"{name}: (no description)")


def run_scheduler():
    """Run the scheduler daemon."""
    configure_logging(workflow="scheduler")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting scheduler daemon")
    
    runner = Runner()
    scheduler = Scheduler(runner)
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
    except Exception:
        logger.exception("Scheduler failed")
        sys.exit(1)


def build_context_from_cli(args) -> RunContext:

    # Parse key=value args into dict
    workflow_args = {}
    for item in args.arg:
        if "=" not in item:
            raise ValueError(f"Invalid --arg '{item}', expected key=value")
        k, v = item.split("=", 1)
        workflow_args[k] = v

    trigger = Trigger(
        type="manual",
        params={},
    )

    return RunContext(
        workflow=args.workflow,
        trigger=trigger,
        run_id=str(uuid.uuid4()),
        started_at=datetime.now(timezone.utc),
        args=workflow_args,
        dry_run=args.dry_run,
    )


def create_new_note(note_type: str):
    """Create a new note and open it in Obsidian.
    
    Args:
        note_type: Type of note to create (currently only "meeting" supported)
    """
    if note_type != "meeting":
        print(f"Unsupported note type: {note_type}")
        sys.exit(1)
    
    # Validate required settings
    if not settings.obsidian_vault_dir:
        print("Error: OBSIDIAN_VAULT_DIR not configured in .env")
        sys.exit(1)
    
    # Create meeting note
    vault_root = Path(settings.obsidian_vault_dir)
    vault_name = vault_root.name
    meetings_dir = vault_root / "meetings" / "notes"
    meetings_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H%M")
    filename = f"{timestamp_str} — Meeting.md"
    file_path = meetings_dir / filename
    
    # Generate frontmatter with timezone
    iso_timestamp = now.astimezone().isoformat()
    content = f"""---
source: manual
meeting_date: {iso_timestamp}
---


"""
    
    # Write file
    file_path.write_text(content, encoding="utf-8")
    print(f"Created: {file_path}")
    
    # Open in Obsidian
    relative_path = file_path.relative_to(vault_root)
    # Remove .md extension and convert to forward slashes for Obsidian URI
    note_path = str(relative_path.with_suffix("")).replace("\\", "/")
    encoded_path = quote(note_path)
    encoded_vault = quote(vault_name)
    
    obsidian_uri = f"obsidian://open?vault={encoded_vault}&file={encoded_path}"
    
    try:
        # Use start command with proper quoting for URIs
        subprocess.Popen(f'start "" "{obsidian_uri}"', shell=True)
        print(f"Opening in Obsidian: {note_path}")
    except Exception as e:
        print(f"Failed to open in Obsidian: {e}")
        print(f"URI: {obsidian_uri}")
        sys.exit(1)


if __name__ == "__main__":
    main()
