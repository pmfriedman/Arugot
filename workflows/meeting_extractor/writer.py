"""Meeting Record File Writer

Creates well-formed meeting record files in _scratch/auto/meetings/.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from common.types import RunContext

logger = logging.getLogger(__name__)


@dataclass
class MeetingRecord:
    """Represents a meeting record to be written to disk."""

    meeting_id: str
    created_at: str  # ISO timestamp
    created_by: str = "meeting-extractor"
    workflow: str = "meeting"
    state: str = "unprocessed"
    ingest_source: str = ""  # relative path to ingest file


def generate_meeting_record(
    ingest_file: Path, meeting_id: str, vault_root: Path
) -> MeetingRecord:
    """Generate a meeting record from an ingest file.

    Args:
        ingest_file: Path to the ingest transcript file
        meeting_id: Derived meeting ID
        vault_root: Path to the Obsidian vault root (to compute relative paths)

    Returns:
        MeetingRecord with populated fields
    """
    # Create relative path from vault root for wiki-style link
    try:
        relative_path = ingest_file.relative_to(vault_root)
        ingest_source = str(relative_path).replace(
            "\\", "/"
        )  # Use forward slashes for Obsidian
    except ValueError:
        # If ingest_file is not relative to vault_root, use absolute path
        logger.warning("Ingest file not under vault root: %s", ingest_file)
        ingest_source = str(ingest_file)

    return MeetingRecord(
        meeting_id=meeting_id,
        created_at=datetime.now().isoformat(),
        ingest_source=ingest_source,
    )


def write_meeting_file(
    record: MeetingRecord, output_dir: Path, context: RunContext
) -> Path:
    """Write a meeting record to disk.

    Creates the output directory if it doesn't exist and writes a markdown file
    with YAML frontmatter and structured body.

    Args:
        record: MeetingRecord to write
        output_dir: Directory to write the meeting file (_scratch/auto/meetings/)
        context: Runtime context including dry_run flag

    Returns:
        Path to the created (or would-be-created) file
    """
    output_path = output_dir / f"{record.meeting_id}.md"

    # Generate frontmatter
    frontmatter = f"""---
workflow: {record.workflow}
state: {record.state}
created_by: {record.created_by}
created_at: {record.created_at}
---
"""

    # Generate body with wiki-style link
    # Remove .md extension from source path for Obsidian wiki links
    source_without_ext = record.ingest_source.removesuffix(".md")
    body = f"""# Meeting

Source:
- Transcript: [[{source_without_ext}]]

This file is machine-owned.
"""

    content = frontmatter + "\n" + body

    if context.dry_run:
        logger.info("[DRY-RUN] Would write meeting record: %s", output_path)
        logger.debug("[DRY-RUN] Content:\n%s", content)
        return output_path

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(content, encoding="utf-8")
    logger.info("Created meeting record: %s", output_path)

    return output_path
