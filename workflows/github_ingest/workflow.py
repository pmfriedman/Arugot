"""GitHub PR ingest workflow."""

import logging
from pathlib import Path

from common.types import RunContext
from settings import settings
from common.github_client import (
    fetch_user_involved_prs,
    fetch_pr_data,
    build_pr_timeline,
    parse_pr_url,
)
from workflows.github_ingest import writer

logger = logging.getLogger(__name__)


async def run(context: RunContext, state: dict) -> dict:
    """Ingest all open PRs where the user is involved.
    
    Fetches current open PRs from GitHub, writes them to _ingest/github/,
    and marks PRs no longer in the query as inactive.
    
    Args:
        context: Workflow run context
        state: Workflow state (not used - this workflow is stateless)
    
    Returns:
        Updated state dict (unchanged)
    """
    workspace = Path(settings.obsidian_vault_dir)
    output_dir = workspace / "_ingest" / "github"
    
    # Get GitHub username from settings
    my_username = settings.github_username
    if not my_username:
        logger.error("github_username not configured in settings")
        return state
    
    logger.info(f"Fetching open PRs for user: {my_username}")
    
    # Fetch all open PRs where user is involved
    pr_issues = await fetch_user_involved_prs(my_username)
    logger.info(f"Found {len(pr_issues)} open PRs")
    
    # Track which PRs we've seen this run
    current_pr_files = set()
    
    # Process each PR
    for pr_issue in pr_issues:
        pr_url = pr_issue["html_url"]
        
        try:
            # Fetch full PR data and timeline
            logger.info(f"Processing PR: {pr_url}")
            pr = await fetch_pr_data(pr_url)
            
            # Parse URL for timeline fetch
            owner, repo, pr_number = parse_pr_url(pr_url)
            timeline = await build_pr_timeline(owner, repo, pr_number)
            
            # Determine user's role
            my_role = _determine_role(pr, timeline, my_username)
            
            if context.dry_run:
                # Just log what would be written
                created_date = pr.created_at.replace('Z', '+00:00')
                from datetime import datetime
                date_str = datetime.fromisoformat(created_date).strftime("%Y-%m-%d %H%M")
                filename = f"{date_str} — pr-{owner}-{repo}-{pr_number}.md"
                output_path = output_dir / filename
                logger.info(f"[DRY-RUN] Would write: {output_path}")
                current_pr_files.add(filename)
            else:
                # Write PR file
                filepath = writer.write_pr_file(
                    pr=pr,
                    my_username=my_username,
                    my_role=my_role,
                    timeline=timeline,
                    output_dir=output_dir,
                    active=True
                )
                current_pr_files.add(filepath.name)
            
        except Exception as e:
            logger.error(f"Failed to process PR {pr_url}: {e}")
            continue
    
    # Mark PRs not in current results as inactive
    if not context.dry_run and output_dir.exists():
        for existing_file in output_dir.glob("pr-*.md"):
            if existing_file.name not in current_pr_files:
                writer.mark_inactive(existing_file)
    
    logger.info(f"GitHub ingest complete. Processed {len(current_pr_files)} active PRs")
    return state


def _determine_role(pr, timeline: list, my_username: str) -> str:
    """Determine user's role in the PR: author, reviewer, or both.
    
    Args:
        pr: GitHub PR data
        timeline: List of PR events
        my_username: Current user's GitHub username
    
    Returns:
        "author", "reviewer", or "both"
    """
    is_author = pr.user.login == my_username
    
    # Check if user has reviewed
    is_reviewer = any(
        event.event_type == "review" and event.actor == my_username
        for event in timeline
    )
    
    if is_author and is_reviewer:
        return "both"
    elif is_author:
        return "author"
    elif is_reviewer:
        return "reviewer"
    else:
        # Default to reviewer if involved but not author
        # (could be mentioned, assigned, etc.)
        return "reviewer"
