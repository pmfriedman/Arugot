"""Extract GitHub PR Workflow Implementation.

Reconciles PR data in _ingest/github/ with stub records in _scratch/auto/github/,
ensuring every active PR has exactly one stub for downstream processing.
"""

import logging
from pathlib import Path
import re

from common.types import RunContext
from settings import settings
from workflows.extract_github_pr.writer import (
    generate_pr_stub,
    write_pr_stub,
    update_stub_state,
)

DESCRIPTION = "Create PR stubs in _scratch/auto/github/ from ingested GitHub PR data"

logger = logging.getLogger(__name__)


async def run(context: RunContext, state: dict) -> dict:
    """Execute the extract GitHub PR workflow.

    Scans for PR files in the ingest directory and creates/updates
    corresponding stub records in the working directory.

    Args:
        context: Runtime context including dry_run flag and trigger info
        state: Workflow state (unused - state is implicit via filesystem)

    Returns:
        Empty dict (state is implicit via file existence)
    """
    logger.info("Extract GitHub PR workflow starting")

    if context.dry_run:
        logger.info("Dry-run mode: no changes will be made")

    # Get directories from settings
    vault_root = Path(settings.obsidian_vault_dir)
    ingest_dir = vault_root / "_ingest/github"
    working_dir = vault_root / "_scratch/auto/github"

    logger.info("Vault root: %s", vault_root)

    # Run reconciliation
    try:
        summary = reconcile_prs(ingest_dir, working_dir, vault_root, context)
        logger.info("PR extraction complete: %s", summary)
    except Exception as e:
        logger.error("PR extraction failed: %s", str(e), exc_info=True)
        raise

    # Return empty state (state is implicit via file existence)
    return {}


def parse_pr_frontmatter(ingest_file: Path) -> dict | None:
    """Parse YAML frontmatter from an ingest PR file.

    Args:
        ingest_file: Path to the ingest PR markdown file

    Returns:
        Dict with frontmatter fields, or None if parsing fails
    """
    try:
        content = ingest_file.read_text(encoding="utf-8")
        
        # Extract frontmatter between --- markers
        if not content.startswith("---"):
            logger.warning("No frontmatter found in: %s", ingest_file)
            return None
        
        # Find the closing ---
        end_marker = content.find("---", 3)
        if end_marker == -1:
            logger.warning("Malformed frontmatter in: %s", ingest_file)
            return None
        
        frontmatter = content[3:end_marker].strip()
        
        # Parse key-value pairs (simple YAML parsing)
        data = {}
        for line in frontmatter.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Convert boolean strings
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                
                # Convert numeric strings
                elif value.isdigit():
                    value = int(value)
                
                data[key] = value
        
        return data
        
    except Exception as e:
        logger.error("Failed to parse frontmatter from %s: %s", ingest_file, e)
        return None


def stub_exists(pr_number: int, repo_owner: str, repo_name: str, working_dir: Path) -> bool:
    """Check if a PR stub already exists.

    Args:
        pr_number: PR number
        repo_owner: Repository owner
        repo_name: Repository name
        working_dir: Path to _scratch/auto/github/ directory

    Returns:
        True if PR stub file exists, False otherwise
    """
    filename = f"pr-{repo_owner}-{repo_name}-{pr_number}.md"
    stub_path = working_dir / filename
    return stub_path.exists()


def get_stub_action_signals(stub_path: Path) -> dict | None:
    """Extract action signals from an existing stub file.

    Args:
        stub_path: Path to the stub file

    Returns:
        Dict with action_type, last_actor, last_event_at, or None if not found
    """
    try:
        # Parse frontmatter from stub
        stub_data = parse_pr_frontmatter(stub_path)
        if not stub_data:
            return None
        
        return {
            "action_type": stub_data.get("action_type", "none"),
            "last_actor": stub_data.get("last_actor"),
            "last_event_at": stub_data.get("last_event_at"),
        }
        
    except Exception as e:
        logger.error("Failed to get action signals from stub %s: %s", stub_path, e)
        return None


def reconcile_prs(
    ingest_dir: Path, working_dir: Path, vault_root: Path, context: RunContext
) -> dict:
    """Reconcile PR ingest files with stub records.

    Scans all active PRs in the ingest directory and ensures each has a
    corresponding stub in the working directory. Creates missing stubs and
    updates stubs when PRs change.

    This operation is idempotent - safe to run repeatedly.

    Args:
        ingest_dir: Path to _ingest/github/ directory
        working_dir: Path to _scratch/auto/github/ directory
        vault_root: Path to Obsidian vault root (for relative path computation)
        context: Runtime context including dry_run flag

    Returns:
        Summary dict with keys: scanned, active, created, updated, skipped
    """
    logger.info("Starting PR reconciliation")
    logger.info("Ingest directory: %s", ingest_dir)
    logger.info("Working directory: %s", working_dir)

    if not ingest_dir.exists():
        logger.warning("Ingest directory does not exist: %s", ingest_dir)
        return {"scanned": 0, "active": 0, "created": 0, "updated": 0, "skipped": 0}

    # Get all ingest PR files (matches both "pr-*.md" and "YYYY-MM-DD HHMM — pr-*.md")
    ingest_files = [f for f in ingest_dir.glob("*.md") if " — pr-" in f.name or f.name.startswith("pr-")]

    scanned = len(ingest_files)
    active = 0
    created = 0
    updated = 0
    skipped = 0

    for ingest_file in ingest_files:
        try:
            # Parse frontmatter
            pr_data = parse_pr_frontmatter(ingest_file)
            if not pr_data:
                logger.warning("Skipping file with invalid frontmatter: %s", ingest_file)
                skipped += 1
                continue

            # Only process active PRs
            if not pr_data.get("active", False):
                logger.debug("Skipping inactive PR: %s", ingest_file)
                skipped += 1
                continue

            active += 1

            pr_number = pr_data["pr_number"]
            repo_owner = pr_data["repo_owner"]
            repo_name = pr_data["repo_name"]
            
            # Get action signals from ingest
            ingest_action_signals = {
                "action_type": pr_data.get("action_type", "none"),
                "last_actor": pr_data.get("last_actor"),
                "last_event_at": pr_data.get("last_event_at"),
            }

            # Check if stub already exists
            if stub_exists(pr_number, repo_owner, repo_name, working_dir):
                # Compare action signals
                stub_path = working_dir / f"pr-{repo_owner}-{repo_name}-{pr_number}.md"
                stub_action_signals = get_stub_action_signals(stub_path)

                if stub_action_signals != ingest_action_signals:
                    # Action signals changed, mark as unprocessed
                    logger.info("PR action signals changed, updating stub: %s", ingest_file.name)
                    update_stub_state(stub_path, "unprocessed", context)
                    updated += 1
                else:
                    logger.debug("PR stub already exists and unchanged: %s", ingest_file.name)
                    skipped += 1
            else:
                # Create new stub
                logger.info("Creating new PR stub for: %s", ingest_file.name)
                stub = generate_pr_stub(ingest_file, pr_data, vault_root)
                write_pr_stub(stub, working_dir, context)
                created += 1

        except Exception as e:
            logger.error("Failed to process %s: %s", ingest_file, e)
            skipped += 1

    return {
        "scanned": scanned,
        "active": active,
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }
