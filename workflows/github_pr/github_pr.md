# GitHub PR

**STATUS: Active**

Fetches GitHub pull requests where you're involved and creates Inbox notifications when action signals change.

## Overview

This workflow monitors your GitHub PRs and intelligently notifies you only when something meaningful changes. It tracks "action signals" (state + actor + timestamp) per PR and creates Inbox notifications when these signals change, preventing notification spam while keeping you informed.

## How It Works

1. **Fetch PRs** - Retrieves all open PRs where you're author, reviewer, or assignee
2. **Compute Action Signals** - Determines current state for each PR:
   - `stale_review` - Your review is outdated due to new commits
   - `ignored_pr` - Your PR needs attention (no reviews, requested changes, merge conflicts)
   - `ball_in_your_court` - You need to respond (review requested, changes requested, mentions)
   - `none` - No action needed from you
3. **Detect Changes** - Compares current signals vs. previous state
4. **Notify on Change** - Creates Inbox notification only when action signals change
5. **Persist State** - Saves current signals for next run

## State Schema

State is persisted as JSON:
```json
{
  "prs": {
    "owner/repo/123": {
      "action_type": "ball_in_your_court",
      "last_actor": "teammate",
      "last_event_at": "2026-01-03T10:30:00Z"
    }
  }
}
```

## Artifacts Created

- **PR Files**: `github/prs/{timestamp} — pr-{owner}-{repo}-{number}.md`
  - Full PR details with timeline, reviews, action signals
  - Updated on each run, marked inactive when PR closes
  
- **Inbox Notifications**: `_inbox/{timestamp} — github_pr.md`
  - Created only when action signals change
  - Links to PR file with metadata (action type, actor, role)

## Fault Tolerance

State updates are atomic:
- State only updated after successful notification creation
- On failure, PR excluded from state update
- Next run will retry notification for that PR

## Usage

```sh
# Run once manually
uv run python main.py run github_pr

# Dry run to see what would happen
uv run python main.py run github_pr --dry-run

# Typically scheduled to run periodically
uv run python main.py schedule
```

## Design Decisions

### Why State-Based Change Detection?

Early versions created Inbox notifications for every PR on every run, causing notification spam. State tracking enables smart notifications that fire only when something meaningful changes, keeping the Inbox focused on actionable items.

### Why No Stub Files?

This workflow supersedes the old two-workflow approach (ingest → extract). The extract workflow created "stub" files with state tracking, but that added unnecessary complexity. Now state tracking happens directly in the ingest workflow, eliminating the intermediate layer.

### Why Track Three Fields?

Tracking `action_type`, `last_actor`, and `last_event_at` together provides robust change detection:
- Action type changes (e.g., none → ball_in_your_court)
- Same action but different actor (e.g., new reviewer added)
- Same action/actor but new event (timestamp changed)

Any of these changes trigger a notification.

## Related Workflows

- **extract_github_pr** - SUPERSEDED by this workflow's state tracking
