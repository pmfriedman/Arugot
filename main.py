import argparse
import importlib
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from common.logging import configure_logging
from common.types import RunContext, Trigger
from runner.runner import Runner


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

    args = parser.parse_args()

    if args.command == "list":
        list_workflows()
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

    for py_file in workflows_dir.glob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.startswith("_"):
            continue

        module_name = py_file.stem
        try:
            module = importlib.import_module(f"workflows.{module_name}")
            if callable(getattr(module, "run", None)):
                workflows.append(module_name)
        except Exception as e:
            logging.warning(f"Failed to import workflows.{module_name}: {e}")

    for name in sorted(workflows):
        print(name)


def build_context_from_cli(args) -> RunContext:

    # Parse key=value args into dict
    workflow_args = {}
    for item in args.arg:
        if "=" not in item:
            raise ValueError(f"Invalid --arg '{item}', expected key=value")
        k, v = item.split("=", 1)
        workflow_args[k] = v

    workflow_args["dry_run"] = args.dry_run

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
    )


if __name__ == "__main__":
    main()
