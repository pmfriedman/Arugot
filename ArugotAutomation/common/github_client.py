"""GitHub API client for fetching PR and user data."""

import re
import httpx
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from settings import settings


def _headers() -> dict[str, str]:
    """Build GitHub API headers."""
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.github_token}",
    }


class GitHubUser(BaseModel):
    """GitHub user model."""
    login: str
    id: int
    avatar_url: str
    url: str


class GitHubPullRequest(BaseModel):
    """GitHub Pull Request model matching API response structure."""
    number: int
    title: str
    body: str | None
    state: str
    user: GitHubUser
    created_at: str
    updated_at: str
    closed_at: str | None
    merged_at: str | None
    html_url: str
    changed_files: int
    additions: int
    deletions: int
    commits: int
    comments: int
    review_comments: int


class PREvent(BaseModel):
    """Represents an event in a PR timeline."""
    timestamp: datetime
    actor: str
    event_type: str  # "review", "comment", "review_comment", "commit"
    details: dict


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    """Parse a GitHub PR URL to extract owner, repo, and PR number."""
    pattern = r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, pr_url.rstrip("/"))
    
    if not match:
        raise ValueError(f"Invalid GitHub PR URL format: {pr_url}")
    
    owner, repo, pr_number = match.groups()
    return owner, repo, int(pr_number)


async def fetch_user_involved_prs(username: str) -> list[dict]:
    """Fetch all open PRs where the user is involved."""
    query = f"is:pr is:open involves:{username}"
    api_url = "https://api.github.com/search/issues"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            params={"q": query, "per_page": 100},
            headers=_headers(),
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])


async def fetch_pr_data(pr_url: str) -> GitHubPullRequest:
    """Fetch PR data from GitHub API."""
    owner, repo, pr_number = parse_pr_url(pr_url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=_headers(), timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return GitHubPullRequest(**data)


async def fetch_pr_reviews(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all reviews for a pull request."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json()


async def fetch_pr_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all comments for a pull request (both issue comments and review comments)."""
    async with httpx.AsyncClient() as client:
        issue_comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        review_comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        issue_response = await client.get(issue_comments_url, headers=_headers(), timeout=30.0)
        issue_response.raise_for_status()
        
        review_response = await client.get(review_comments_url, headers=_headers(), timeout=30.0)
        review_response.raise_for_status()
        
        return issue_response.json() + review_response.json()


async def fetch_pr_commits(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch commit history for a pull request."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json()


async def build_pr_timeline(owner: str, repo: str, pr_number: int) -> list[PREvent]:
    """Build a timeline of all PR events sorted by timestamp."""
    reviews = await fetch_pr_reviews(owner, repo, pr_number)
    comments = await fetch_pr_comments(owner, repo, pr_number)
    commits = await fetch_pr_commits(owner, repo, pr_number)
    
    events = []
    
    # Convert reviews to PREvent
    for review in reviews:
        events.append(PREvent(
            timestamp=datetime.fromisoformat(review["submitted_at"].replace("Z", "+00:00")),
            actor=review["user"]["login"],
            event_type="review",
            details={"state": review["state"], "body": review.get("body")}
        ))
    
    # Convert comments to PREvent
    for comment in comments:
        event_type = "review_comment" if "pull_request_review_id" in comment else "comment"
        events.append(PREvent(
            timestamp=datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00")),
            actor=comment["user"]["login"],
            event_type=event_type,
            details={"body": comment.get("body")}
        ))
    
    # Convert commits to PREvent
    for commit in commits:
        if commit.get("author"):
            events.append(PREvent(
                timestamp=datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00")),
                actor=commit["author"]["login"],
                event_type="commit",
                details={"sha": commit["sha"], "message": commit["commit"]["message"]}
            ))
    
    # Sort by timestamp
    events.sort(key=lambda e: e.timestamp)
    return events


def get_last_actor(timeline: list[PREvent]) -> str | None:
    """Get the last human actor from the timeline (excluding bots)."""
    for event in reversed(timeline):
        actor = event.actor
        if not _is_bot(actor):
            return actor
    return None


def _is_bot(username: str) -> bool:
    """Check if a username belongs to a bot."""
    username_lower = username.lower()
    return "[bot]" in username_lower or username_lower in {
        "dependabot", "renovate", "github-actions", "codecov", "vercel"
    }


def get_user_last_review(timeline: list[PREvent], username: str) -> PREvent | None:
    """Find the user's most recent review event."""
    for event in reversed(timeline):
        if event.event_type == "review" and event.actor == username:
            return event
    return None


def get_events_after(timeline: list[PREvent], timestamp: datetime) -> list[PREvent]:
    """Filter timeline to events after a given timestamp."""
    return [event for event in timeline if event.timestamp > timestamp]


def has_author_activity_after_review(timeline: list[PREvent], review_timestamp: datetime, author: str) -> bool:
    """Check if the PR author has any activity after a review timestamp."""
    events_after = get_events_after(timeline, review_timestamp)
    return any(event.actor == author for event in events_after)


async def is_stale_review(owner: str, repo: str, pr_number: int, reviewer_username: str) -> bool:
    """Check if a reviewer's review is stale (author has activity after the review)."""
    timeline = await build_pr_timeline(owner, repo, pr_number)
    
    # Find the reviewer's last review
    last_review = get_user_last_review(timeline, reviewer_username)
    if not last_review:
        return False  # Reviewer hasn't reviewed this PR
    
    # Get the PR author
    pr_data = await fetch_pr_data(f"https://github.com/{owner}/{repo}/pull/{pr_number}")
    author = pr_data.user.login
    
    # Check if author has activity after the review
    return has_author_activity_after_review(timeline, last_review.timestamp, author)


def get_last_event_time(timeline: list[PREvent]) -> datetime | None:
    """Get the timestamp of the most recent event in the timeline."""
    return timeline[-1].timestamp if timeline else None


def is_inactive_for_duration(timeline: list[PREvent], hours: int) -> bool:
    """Check if PR has been inactive for specified number of hours."""
    last_event_time = get_last_event_time(timeline)
    if not last_event_time:
        return False
    
    now = datetime.now(timezone.utc)
    time_since_last_event = now - last_event_time
    return time_since_last_event >= timedelta(hours=hours)


def has_others_activity_after(timeline: list[PREvent], timestamp: datetime, author: str) -> bool:
    """Check if anyone besides the author has activity after a timestamp."""
    events_after = get_events_after(timeline, timestamp)
    return any(event.actor != author and not _is_bot(event.actor) for event in events_after)


async def is_ignored_pr(owner: str, repo: str, pr_number: int, author: str, hours: int = 24) -> bool:
    """Check if PR has been ignored (no response from others after specified hours)."""
    timeline = await build_pr_timeline(owner, repo, pr_number)
    
    if not timeline:
        return False
    
    # Check if PR is inactive for the specified duration
    if not is_inactive_for_duration(timeline, hours):
        return False
    
    # Check if anyone besides the author (and bots) has engaged since PR creation
    pr_creation_time = timeline[0].timestamp
    has_others_engaged = has_others_activity_after(timeline, pr_creation_time, author)
    
    # PR is ignored if it's inactive and no one else has engaged
    return not has_others_engaged
