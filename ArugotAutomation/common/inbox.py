"""Utilities for working with the Inbox."""

import logging
from datetime import datetime
from pathlib import Path
from settings import settings

logger = logging.getLogger(__name__)


def create_notification(
    title: str,
    source_path: str,
    notification_type: str,
    metadata: dict = None
) -> Path:
    """Create a notification in the Inbox.
    
    Args:
        title: Title for the notification
        source_path: Path to the source artifact (can be absolute or relative to vault)
        notification_type: Type of notification (e.g., 'meeting_transcript', 'github_pr')
        metadata: Optional additional metadata to include in frontmatter
    
    Returns:
        Path to the created notification file
    """
    vault_dir = Path(settings.obsidian_vault_dir)
    inbox_dir = vault_dir / "_inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert source_path to vault-relative path for wikilink
    source_path_obj = Path(source_path)
    if source_path_obj.is_absolute():
        try:
            # Make it relative to vault
            relative_source = source_path_obj.relative_to(vault_dir)
            source_link = str(relative_source).replace('\\', '/')
        except ValueError:
            # Path is outside vault, use as-is
            source_link = str(source_path).replace('\\', '/')
    else:
        source_link = str(source_path).replace('\\', '/')
    
    # Generate filename from timestamp and title
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in (' ', '-') else '' for c in title)
    safe_title = safe_title.replace(' ', '-')[:50]  # Limit length
    filename = f"{timestamp}-{safe_title}.md"
    
    notification_path = inbox_dir / filename
    
    # Build frontmatter
    frontmatter_lines = [
        "---",
        f"type: {notification_type}",
        f"created: {datetime.now().isoformat()}",
        f"source: \"[[{source_link}]]\"",
    ]
    
    if metadata:
        for key, value in metadata.items():
            frontmatter_lines.append(f"{key}: {value}")
    
    frontmatter_lines.append("---")
    
    # Build notification body
    body_lines = [f"# {title}"]
    
    # Add PR URL link if available (for github_pr notifications)
    if notification_type == "github_pr" and metadata and "pr_url" in metadata:
        body_lines.append("")
        body_lines.append(f"🔗 [View PR on GitHub]({metadata['pr_url']})")
    
    body_lines.append("")
    
    # Write notification
    content = "\n".join(frontmatter_lines) + "\n\n" + "\n".join(body_lines)
    notification_path.write_text(content, encoding="utf-8")
    
    logger.info(f"Created Inbox notification: {notification_path.name}")
    return notification_path
