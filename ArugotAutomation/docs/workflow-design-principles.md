# Workflow Design Principles

Workflows are built on top of the Inbox pattern. They're secondary to the core Inbox flow but follow common design principles while remaining free to abstract their own implementation details.

## Common Framework

All workflows share these characteristics:

### The Workflow Contract

Every workflow must define:

```python
async def run(context: RunContext, state: dict) -> dict:
    """
    The workflow entry point.
    
    Args:
        context: Contains vault_dir, args, trigger info, dry_run flag
        state: Persisted dict from previous runs
    
    Returns:
        Updated state dict to persist
    """
    pass

DESCRIPTION = "One-line description shown by 'list' command"
```

### Common Capabilities

- **State management**: Workflows can persist state between runs via the returned dict
- **Logging**: Use `logging.getLogger(__name__)` for consistent logging
- **Settings access**: Use `from settings import settings` for configuration
- **Idempotence**: Workflows should be safe to run repeatedly
- **Dry-run support**: Respect `context.dry_run` flag for read-only testing


## Design Principles

### Start Simple

Don't abstract prematurely. Build the minimal workflow that solves your problem, then refactor common patterns into utilities only when they emerge naturally.

### Composition Over Inheritance

Workflows are standalone modules. Share functionality through utility modules, not base classes or complex hierarchies.

### Clear Boundaries

Each workflow has a clear purpose. If a workflow is doing too many things, split it. If multiple workflows share significant logic, extract a utility module.

### Implementation Freedom

How a workflow accomplishes its task is entirely up to it:
- Direct file operations
- Helper classes
- Shared utilities
- External tools

The framework provides state, logging, and settings—everything else is your choice.

