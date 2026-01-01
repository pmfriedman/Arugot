import importlib
import logging

from common.types import RunContext
from runner.state import load_state, save_state

logger = logging.getLogger(__name__)


class Runner:
    def run(self, context: RunContext) -> None:
        logger.info("Starting workflow '%s'", context.workflow)

        module_name = f"workflows.{context.workflow}"

        try:
            workflow_module = importlib.import_module(module_name)
        except ImportError as e:
            raise RuntimeError(f"Workflow '{context.workflow}' not found") from e

        if not hasattr(workflow_module, "run"):
            raise RuntimeError(
                f"Workflow '{context.workflow}' does not define a run(context, state) function"
            )

        state = load_state(context.workflow)
        logger.info("Loaded state: %s", state)

        try:
            new_state = workflow_module.run(context, state)

            if not isinstance(new_state, dict):
                raise RuntimeError(
                    f"Workflow '{context.workflow}' returned non-dict state"
                )

            if context.dry_run:
                logger.info("Dry-run enabled; state not persisted")
            else:
                save_state(context.workflow, new_state)
                logger.info("Saved state: %s", new_state)

            logger.info("Finished workflow '%s'", context.workflow)
        except Exception:
            logger.exception(
                "Workflow '%s' failed (run_id=%s)",
                context.workflow,
                context.run_id,
            )
            raise
