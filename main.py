import argparse
import uuid
from datetime import datetime, timezone

from common.types import RunContext, Trigger
from runner.runner import Runner


def main():
    context = build_context_from_cli()
    runner = Runner()
    runner.run(context)


def build_context_from_cli() -> RunContext:
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

    args = parser.parse_args()

    if args.command != "run":
        raise ValueError("Unsupported command")

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
    )


if __name__ == "__main__":
    main()
