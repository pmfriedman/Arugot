"""Write GitHub PR data to markdown files."""

import logging
from pathlib import Path
from datetime import datetime

from common.github_client import GitHubPullRequest, PREvent

logger = logging.getLogger(__name__)


def format_pr_markdown(
    pr: GitHubPullRequest,
    my_username: str,
    my_role: str,
    timeline: list[PREvent],
    action_signals: dict,
    active: bool = True
) -> str:
    """Format PR data as markdown with YAML frontmatter.
    
    Args:
        pr: GitHub PR data
        my_username: Current user's GitHub username
        my_role: "author", "reviewer", or "both"
        timeline: Sorted list of PR events
        action_signals: Dict with action_type, last_actor, last_event_at
        active: Whether PR is currently active/open
    
    Returns:
        Formatted markdown string with frontmatter
    """
    # Build frontmatter
    frontmatter = f"""---
pr_number: {pr.number}
repo_owner: {pr.html_url.split('/')[3]}
repo_name: {pr.html_url.split('/')[4]}
title: "{pr.title.replace('"', '\\"')}"
state: {pr.state}
url: "{pr.html_url}"

author: {pr.user.login}
created_at: "{pr.created_at}"
updated_at: "{pr.updated_at}"

my_role: {my_role}
my_username: {my_username}

# Action signals
action_type: {action_signals['action_type']}
last_actor: {action_signals['last_actor'] or 'null'}
last_event_at: "{action_signals['last_event_at']}"

active: {str(active).lower()}
---

"""
    
    # Build title and description
    body_lines = [f"# {pr.title}\n"]
    
    if pr.body:
        body_lines.append(pr.body)
        body_lines.append("")
    else:
        body_lines.append("*No description provided*\n")
    
    # Add stats section
    body_lines.append("## Stats")
    body_lines.append(f"- **Changed files**: {pr.changed_files}")
    body_lines.append(f"- **Additions**: +{pr.additions}")
    body_lines.append(f"- **Deletions**: -{pr.deletions}")
    body_lines.append(f"- **Commits**: {pr.commits}")
    body_lines.append(f"- **Comments**: {pr.comments} issue + {pr.review_comments} review")
    body_lines.append("")
    
    # Add timeline section
    body_lines.append("## Timeline")
    body_lines.append("")
    
    for event in timeline:
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        event_desc = _format_event(event)
        body_lines.append(f"- **{timestamp}** - @{event.actor}: {event_desc}")
    
    body_lines.append("")
    
    return frontmatter + "\n".join(body_lines)


def _format_event(event: PREvent) -> str:
    """Format a single timeline event for display."""
    if event.event_type == "commit":
        msg = event.details.get("message", "").split("\n")[0]  # First line only
        sha_short = event.details.get("sha", "")[:7]
        return f"Committed `{sha_short}` - {msg}"
    
    elif event.event_type == "review":
        state = event.details.get("state", "")
        body = event.details.get("body", "")
        state_emoji = {
            "APPROVED": "✅",
            "CHANGES_REQUESTED": "❌",
            "COMMENTED": "💬"
        }.get(state, "📝")
        desc = f"{state_emoji} {state}"
        if body:
            desc += f" - {body[:100]}"
        return desc
    
    elif event.event_type == "comment" or event.event_type == "review_comment":
        body = event.details.get("body", "")[:100]
        return f"💬 Commented - {body}"
    
    else:
        return event.event_type


def write_pr_file(
    pr: GitHubPullRequest,
    my_username: str,
    my_role: str,
    timeline: list[PREvent],
    action_signals: dict,
    output_dir: Path,
    active: bool = True
) -> Path:
    """Write PR data to a markdown file in the output directory.
    
    Args:
        pr: GitHub PR data
        my_username: Current user's GitHub username
        my_role: "author", "reviewer", or "both"
        timeline: Sorted list of PR events
        action_signals: Dict with action_type, last_actor, last_event_at
        output_dir: Directory to write files to (e.g., workspace/_ingest/github)
        active: Whether PR is currently active/open
    
    Returns:
        Path to the written file
    """
    # Extract owner and repo from html_url
    # Format: https://github.com/owner/repo/pull/123
    parts = pr.html_url.split('/')
    owner = parts[3]
    repo = parts[4]
    
    # Create filename with date prefix for chronological sorting
    # Parse created_at ISO string (e.g., "2024-01-15T10:30:00Z")
    created_date = datetime.fromisoformat(pr.created_at.replace('Z', '+00:00'))
    date_str = created_date.strftime("%Y-%m-%d %H%M")
    filename = f"{date_str} — pr-{owner}-{repo}-{pr.number}.md"
    filepath = output_dir / filename
    
    # Generate markdown content
    content = format_pr_markdown(pr, my_username, my_role, timeline, action_signals, active)
    
    # Write file
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    
    logger.info(f"Wrote PR file: {filepath}")
    return filepath


def mark_inactive(filepath: Path) -> None:
    """Update a PR file to mark it as inactive.
    
    Reads the file, updates the 'active' field in frontmatter to false,
    and writes it back.
    
    Args:
        filepath: Path to the PR markdown file
    """
    content = filepath.read_text(encoding="utf-8")
    
    # Simple replacement: find "active: true" and replace with "active: false"
    if "active: true" in content:
        updated = content.replace("active: true", "active: false")
        filepath.write_text(updated, encoding="utf-8")
        logger.info(f"Marked inactive: {filepath}")
