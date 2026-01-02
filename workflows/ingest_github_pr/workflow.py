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
    get_last_actor,
    get_last_event_time,
    is_stale_review,
    is_ignored_pr,
)
from workflows.ingest_github_pr import writer

DESCRIPTION = "Fetch GitHub PRs involving the user and write to _ingest/github/"

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
            
            # Compute action signals
            action_signals = await _compute_action_signals(
                pr, timeline, owner, repo, pr_number, my_username
            )
            
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
                    action_signals=action_signals,
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


async def _compute_action_signals(
    pr, timeline: list, owner: str, repo: str, pr_number: int, my_username: str
) -> dict:
    """Compute action signals for a PR.
    
    Args:
        pr: GitHub PR data
        timeline: List of PR events
        owner: Repository owner
        repo: Repository name
        pr_number: PR number
        my_username: Current user's GitHub username
    
    Returns:
        Dict with action_type, last_actor, last_event_at
    """
    author = pr.user.login
    last_event = get_last_event_time(timeline)
    last_actor = get_last_actor(timeline)
    action_type = "none"
    
    # Check 1: Stale review (user reviewed, author updated after)
    if await is_stale_review(owner, repo, pr_number, my_username):
        action_type = "stale_review"
    
    # Check 2: Ignored PR (user authored, no response in 24h)
    elif author == my_username:
        if await is_ignored_pr(owner, repo, pr_number, author, hours=24):
            action_type = "ignored_pr"
    
    # Check 3: Ball in your court (user authored, last actor is someone else)
    elif author == my_username:
        if last_actor and last_actor != my_username:
            action_type = "ball_in_your_court"
    
    return {
        "action_type": action_type,
        "last_actor": last_actor,
        "last_event_at": last_event.isoformat() if last_event else None,
    }


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
