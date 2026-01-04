"""Manual meetings workflow."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from common.types import RunContext
from common.inbox import create_notification
from settings import settings

DESCRIPTION = "Scan manual meeting notes and create inbox notifications"

logger = logging.getLogger(__name__)


async def run(context: RunContext, state: dict) -> dict:
    """Scan for manual meeting notes and create inbox notifications.
    
    Args:
        context: Workflow run context
        state: Workflow state with last run timestamp
    
    Returns:
        Updated state dict with current run timestamp
    """
    vault_dir = Path(settings.obsidian_vault_dir)
    notes_dir = vault_dir / "meetings" / "notes"
    
    if not notes_dir.exists():
        logger.info(f"Notes directory does not exist: {notes_dir}")
        return state
    
    logger.info(f"Scanning for manual meeting notes in {notes_dir}")
    
    # Load last run time (default to epoch if first run)
    last_run_str = state.get("last_run")
    if last_run_str:
        last_run = datetime.fromisoformat(last_run_str)
        logger.info(f"Last run: {last_run_str}")
    else:
        last_run = datetime.fromtimestamp(0, tz=timezone.utc)
        logger.info("First run - will scan all files")
    
    # Scan for modified files
    candidate_files = []
    for md_file in notes_dir.glob("*.md"):
        file_mtime = datetime.fromtimestamp(md_file.stat().st_mtime, tz=timezone.utc)
        if file_mtime > last_run:
            candidate_files.append(md_file)
            logger.info(f"Found modified file: {md_file.name} (mtime: {file_mtime.isoformat()})")
    
    logger.info(f"Found {len(candidate_files)} file(s) modified since last run")
    
    # Check inbox for existing notifications
    inbox_dir = vault_dir / "_inbox"
    files_with_notifications = set()
    
    if inbox_dir.exists():
        for inbox_file in inbox_dir.glob("*.md"):
            try:
                content = inbox_file.read_text(encoding="utf-8")
                # Extract source from frontmatter: source: "[[path/to/file.md]]"
                match = re.search(r'source:\s*"?\[\[([^\]]+)\]\]"?', content)
                if match:
                    source_path = match.group(1)
                    # Normalize to Path object for comparison
                    if not source_path.endswith('.md'):
                        source_path += '.md'
                    files_with_notifications.add(source_path)
            except Exception as e:
                logger.warning(f"Failed to parse inbox file {inbox_file.name}: {e}")
    
    logger.info(f"Found {len(files_with_notifications)} file(s) with existing inbox notifications")
    
    # Create notifications for files without existing inbox notifications
    notifications_created = 0
    
    for candidate_file in candidate_files:
        # Get relative path from vault for comparison
        try:
            relative_path = candidate_file.relative_to(vault_dir)
            relative_path_str = str(relative_path).replace('\\', '/')
        except ValueError:
            logger.warning(f"File outside vault: {candidate_file}")
            continue
        
        # Skip if inbox notification already exists
        if relative_path_str in files_with_notifications:
            logger.info(f"Skipping {candidate_file.name} - inbox notification already exists")
            continue
        
        # Extract title from file (first H1 or use filename)
        title = None
        try:
            content = candidate_file.read_text(encoding="utf-8")
            # Look for first H1
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
        except Exception as e:
            logger.warning(f"Failed to read {candidate_file.name}: {e}")
        
        if not title:
            # Use filename without extension as fallback
            title = candidate_file.stem
        
        if context.dry_run:
            logger.info(f"[DRY-RUN] Would create inbox notification for: {title}")
            notifications_created += 1
        else:
            try:
                notification_path = create_notification(
                    title=f"Meeting: {title}",
                    source_path=candidate_file,
                    notification_type="manual_meeting",
                    metadata={}
                )
                logger.info(f"Created inbox notification: {notification_path.name}")
                notifications_created += 1
            except Exception as e:
                logger.error(f"Failed to create notification for {candidate_file.name}: {e}")
    
    logger.info(f"Created {notifications_created} inbox notification(s)")
    
    # Update state with current run time
    current_run = datetime.now(timezone.utc).isoformat()
    logger.info(f"Updating last_run to: {current_run}")
    
    return {"last_run": current_run}
