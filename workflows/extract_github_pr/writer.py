"""PR stub file writer.

Creates minimal stub files in _scratch/auto/github/ that link back to _ingest.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from common.types import RunContext

logger = logging.getLogger(__name__)


@dataclass
class PRStub:
    """Represents a PR stub to be written to disk."""

    pr_number: int
    repo_owner: str
    repo_name: str
    title: str
    pr_state: str  # open/closed
    my_role: str  # author/reviewer/both
    action_type: str = "none"  # Action signal from ingest
    last_actor: str | None = None
    last_event_at: str | None = None
    workflow: str = "github_pr"
    state: str = "unprocessed"  # unprocessed/processed
    created_by: str = "extract-github-pr"
    created_at: str = ""  # ISO timestamp
    ingest_source: str = ""  # relative path to ingest file


def generate_pr_stub(
    ingest_file: Path, pr_data: dict, vault_root: Path
) -> PRStub:
    """Generate a PR stub from an ingest file's frontmatter.

    Args:
        ingest_file: Path to the ingest PR file
        pr_data: Parsed frontmatter from ingest file
        vault_root: Path to the Obsidian vault root (to compute relative paths)

    Returns:
        PRStub with populated fields
    """
    # Create relative path from vault root for wiki-style link
    try:
        relative_path = ingest_file.relative_to(vault_root)
        ingest_source = str(relative_path).replace("\\", "/")
    except ValueError:
        logger.warning("Ingest file not under vault root: %s", ingest_file)
        ingest_source = str(ingest_file)

    return PRStub(
        pr_number=pr_data["pr_number"],
        repo_owner=pr_data["repo_owner"],
        repo_name=pr_data["repo_name"],
        title=pr_data["title"],
        pr_state=pr_data["state"],
        my_role=pr_data["my_role"],
        action_type=pr_data.get("action_type", "none"),
        last_actor=pr_data.get("last_actor"),
        last_event_at=pr_data.get("last_event_at"),
        created_at=datetime.now().isoformat(),
        ingest_source=ingest_source,
    )


def write_pr_stub(
    stub: PRStub, output_dir: Path, context: RunContext
) -> Path:
    """Write a PR stub to disk.

    Creates the output directory if it doesn't exist and writes a markdown file
    with YAML frontmatter and structured body.

    Args:
        stub: PRStub to write
        output_dir: Directory to write the stub file (_scratch/auto/github/)
        context: Runtime context including dry_run flag

    Returns:
        Path to the created (or would-be-created) file
    """
    filename = f"pr-{stub.repo_owner}-{stub.repo_name}-{stub.pr_number}.md"
    output_path = output_dir / filename

    # Generate frontmatter
    frontmatter = f"""---
workflow: {stub.workflow}
state: {stub.state}
created_by: {stub.created_by}
created_at: {stub.created_at}

# Action signals (from ingest)
action_type: {stub.action_type}
last_actor: {stub.last_actor or 'null'}
last_event_at: "{stub.last_event_at}"
---
"""

    # Generate body with wiki-style link
    source_without_ext = stub.ingest_source.removesuffix(".md")
    body = f"""# PR #{stub.pr_number}: {stub.title}

Source: [[{source_without_ext}]]

**My role**: {stub.my_role}
**State**: {stub.pr_state}

This file is machine-owned.
"""

    content = frontmatter + "\n" + body

    if context.dry_run:
        logger.info("[DRY-RUN] Would write PR stub: %s", output_path)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info("Wrote PR stub: %s", output_path)

    return output_path


def update_stub_state(stub_path: Path, new_state: str, context: RunContext) -> None:
    """Update the state field in an existing stub file.

    Args:
        stub_path: Path to the existing stub file
        new_state: New state value (e.g., "unprocessed")
        context: Runtime context including dry_run flag
    """
    if context.dry_run:
        logger.info("[DRY-RUN] Would update state to '%s': %s", new_state, stub_path)
        return

    content = stub_path.read_text(encoding="utf-8")
    
    # Replace state line in frontmatter
    updated = content.replace(
        f"state: processed",
        f"state: {new_state}"
    ).replace(
        f"state: unprocessed",
        f"state: {new_state}"
    )
    
    stub_path.write_text(updated, encoding="utf-8")
    logger.info("Updated stub state to '%s': %s", new_state, stub_path)
