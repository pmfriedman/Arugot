from common.types import RunContext


class Runner:
    def run(self, context: RunContext) -> None:
        """
        Execute a workflow run.

        Stub implementation:
        - validates input
        - logs intent
        - exits
        """
        print("=== Runner invoked ===")
        print(f"Workflow : {context.workflow}")
        print(f"Run ID   : {context.run_id}")
        print(f"Trigger : {context.trigger.type}")
        print(f"Args    : {context.args}")
        print(f"Started : {context.started_at.isoformat()}")
