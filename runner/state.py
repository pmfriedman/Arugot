import json
import logging
from pathlib import Path

from settings import settings

logger = logging.getLogger(__name__)


def load_state(workflow: str) -> dict:
    """Load state for a workflow.

    Args:
        workflow: Name of the workflow

    Returns:
        Dictionary containing the workflow state data (empty dict if file doesn't exist)

    Raises:
        Exception: If state file exists but contains invalid JSON or is malformed
    """
    state_dir = Path(settings.runtime_root) / "state"
    state_file = state_dir / f"{workflow}.json"

    if not state_file.exists():
        logger.debug(f"No state file found for workflow '{workflow}'")
        return {}

    try:
        with state_file.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in state file for workflow '{workflow}': {e}")
        raise

    # Validate structure
    if not isinstance(state, dict):
        raise ValueError(
            f"State file for workflow '{workflow}' must contain a JSON object"
        )

    if "version" not in state:
        raise ValueError(
            f"State file for workflow '{workflow}' is missing 'version' field"
        )

    if "data" not in state:
        raise ValueError(
            f"State file for workflow '{workflow}' is missing 'data' field"
        )

    logger.debug(f"Loaded state for workflow '{workflow}'")
    return state["data"]


def save_state(workflow: str, data: dict) -> None:
    """Save state for a workflow using atomic write.

    Args:
        workflow: Name of the workflow
        data: Dictionary containing the workflow state data
    """
    state_dir = Path(settings.runtime_root) / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    state_file = state_dir / f"{workflow}.json"
    temp_file = state_dir / f"{workflow}.json.tmp"

    # Wrap data in version structure
    state = {"version": 1, "data": data}

    # Write to temp file
    try:
        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline for better human readability
    except Exception as e:
        logger.error(f"Failed to write state file for workflow '{workflow}': {e}")
        # Clean up temp file if it exists
        if temp_file.exists():
            temp_file.unlink()
        raise

    # Atomic rename
    try:
        temp_file.replace(state_file)
        logger.debug(f"Saved state for workflow '{workflow}'")
    except Exception as e:
        logger.error(f"Failed to rename temp state file for workflow '{workflow}': {e}")
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
        raise
