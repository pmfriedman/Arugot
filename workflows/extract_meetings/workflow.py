"""Meeting Extractor Workflow Implementation

Reconciles meeting transcripts in _ingest/fireflies/ with meeting records in
_scratch/auto/meetings/, ensuring every transcript has exactly one record.
"""

import logging
from pathlib import Path
import re

from common.types import RunContext
from settings import settings
from workflows.extract_meetings.writer import (
    generate_meeting_record,
    write_meeting_file,
)

logger = logging.getLogger(__name__)


async def run(context: RunContext, state: dict) -> dict:
    """Execute the meeting extractor workflow.

    Scans for meeting transcripts in the ingest directory and creates
    corresponding meeting records in the working directory if they don't
    already exist.

    Args:
        context: Runtime context including dry_run flag and trigger info
        state: Workflow state (unused - state is implicit via filesystem)

    Returns:
        Empty dict (state is implicit via file existence)
    """
    logger.info("Meeting extractor workflow starting")

    if context.dry_run:
        logger.info("Dry-run mode: no changes will be made")

    # Get directories from settings
    vault_root = Path(settings.obsidian_vault_dir)
    ingest_dir = vault_root / "_ingest/fireflies"
    working_dir = vault_root / "_scratch/auto/meetings"

    logger.info("Vault root: %s", vault_root)

    # Run reconciliation
    try:
        summary = reconcile_meetings(ingest_dir, working_dir, vault_root, context)
        logger.info("Meeting extraction complete: %s", summary)
    except Exception as e:
        logger.error("Meeting extraction failed: %s", str(e), exc_info=True)
        raise

    # Return empty state (state is implicit via file existence)
    return {}


def meeting_record_exists(meeting_id: str, working_dir: Path) -> bool:
    """Check if a meeting record already exists.

    Args:
        meeting_id: Meeting ID to check
        working_dir: Path to _scratch/auto/meetings/ directory

    Returns:
        True if meeting record file exists, False otherwise
    """
    record_path = working_dir / f"{meeting_id}.md"
    return record_path.exists()


def reconcile_meetings(
    ingest_dir: Path, working_dir: Path, vault_root: Path, context: RunContext
) -> dict:
    """Reconcile meeting transcripts with meeting records.

    Scans all transcripts in the ingest directory and ensures each has a
    corresponding record in the working directory. Creates missing records.

    This operation is idempotent - safe to run repeatedly.

    Args:
        ingest_dir: Path to _ingest/fireflies/ directory
        working_dir: Path to _scratch/auto/meetings/ directory
        vault_root: Path to Obsidian vault root (for relative path computation)
        context: Runtime context including dry_run flag

    Returns:
        Summary dict with keys: scanned, existing, created, errors
    """
    logger.info("Starting meeting reconciliation")
    logger.info("Ingest directory: %s", ingest_dir)
    logger.info("Working directory: %s", working_dir)

    # Get all ingest transcripts
    transcript_files = list_ingest_files(ingest_dir)

    scanned = len(transcript_files)
    existing = 0
    created = 0
    errors = 0

    for transcript_file in transcript_files:
        try:
            # Derive meeting ID
            meeting_id = derive_meeting_id(transcript_file)

            # Check if record already exists
            if meeting_record_exists(meeting_id, working_dir):
                logger.debug("Meeting record already exists: %s", meeting_id)
                existing += 1
                continue

            # Create new meeting record
            logger.info("Creating meeting record for: %s", meeting_id)
            record = generate_meeting_record(transcript_file, meeting_id, vault_root)
            write_meeting_file(record, working_dir, context)
            created += 1

        except Exception as e:
            logger.error(
                "Error processing transcript %s: %s",
                transcript_file.name,
                str(e),
                exc_info=True,
            )
            errors += 1
            # Continue processing other files

    summary = {
        "scanned": scanned,
        "existing": existing,
        "created": created,
        "errors": errors,
    }

    logger.info("Reconciliation complete: %s", summary)

    return summary


def list_ingest_files(ingest_dir: Path) -> list[Path]:
    """List all meeting transcript files in the ingest directory.

    All markdown files in the ingest directory are considered meeting transcripts.

    Args:
        ingest_dir: Path to the _ingest/fireflies/ directory

    Returns:
        List of paths to transcript files (*.md files)
    """
    if not ingest_dir.exists():
        logger.warning("Ingest directory does not exist: %s", ingest_dir)
        return []

    if not ingest_dir.is_dir():
        logger.error("Ingest path is not a directory: %s", ingest_dir)
        return []

    # Find all .md files in the ingest directory
    transcript_files = sorted(ingest_dir.glob("*.md"))

    logger.info("Found %d transcript files in %s", len(transcript_files), ingest_dir)

    return transcript_files


def derive_meeting_id(ingest_file: Path) -> str:
    """Derive a deterministic meeting ID from an ingest file path.

    Strategy (v1): Use the filename stem (without extension), sanitized for
    filesystem safety.

    Assumptions:
    - Fireflies.ai filenames are stable and unique
    - Filename stem provides sufficient identification

    Args:
        ingest_file: Path to the meeting transcript file

    Returns:
        Sanitized meeting ID suitable for use as a filename

    Raises:
        ValueError: If the derived ID would be invalid (empty or unsafe)
    """
    # Get filename without extension
    stem = ingest_file.stem

    if not stem:
        raise ValueError(f"Cannot derive meeting ID from empty filename: {ingest_file}")

    # Sanitize for filesystem safety:
    # - Convert to lowercase
    # - Replace spaces with hyphens
    # - Remove or replace unsafe characters
    # - Collapse multiple hyphens
    meeting_id = stem.lower()
    meeting_id = meeting_id.replace(" ", "-")
    meeting_id = re.sub(r"[^\w\-.]", "-", meeting_id)  # Keep word chars, hyphens, dots
    meeting_id = re.sub(r"-+", "-", meeting_id)  # Collapse multiple hyphens
    meeting_id = meeting_id.strip("-")  # Remove leading/trailing hyphens

    # Validate result
    if not meeting_id:
        raise ValueError(
            f"Derived meeting ID is empty after sanitization: {ingest_file}"
        )

    logger.debug("Derived meeting ID '%s' from file: %s", meeting_id, ingest_file.name)

    return meeting_id
