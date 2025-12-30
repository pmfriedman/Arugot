import logging
from common.types import RunContext

logger = logging.getLogger(__name__)


def run(context: RunContext, state: dict) -> dict:
    count = state.get("count", 0)
    logger.info("Current count: %s", count)

    count += 1
    logger.info("Incremented count to: %s", count)

    return {"count": count}
