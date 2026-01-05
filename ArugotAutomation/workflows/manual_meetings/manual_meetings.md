# Manual Meetings

**STATUS: Active**

Scans for manually-written meeting notes and creates Inbox notifications for processing.

## Implementation Steps

### Step 1: Update create_new_note command
**Owner:** Copilot
- Update `main.py` line 165 to write to `meetings/notes/` instead of `_scratch/human/meetings/`
- This ensures new meeting notes are created in the correct location for the workflow

### Step 2: Implement workflow scanning logic
**Owner:** Copilot
- Load `last_run` timestamp from state (default to epoch if first run)
- Scan `meetings/notes/*.md` for files with `mtime > last_run`
- Build list of candidate files

### Step 3: Implement inbox deduplication check
**Owner:** Copilot
- Scan `_inbox/*.md` files
- Parse `source` frontmatter to extract linked file paths
- Build set of files that already have active inbox notifications

### Step 4: Create notifications for modified files
**Owner:** Copilot
- For each candidate file, check if it's in the inbox set
- If not in inbox, create notification using `create_notification()`
- Extract title from file (first H1 or filename)
- Keep metadata minimal

### Step 5: Update state with current run time
**Owner:** Copilot
- After successful notifications, update state with current timestamp
- Return updated state: `{"last_run": "2026-01-03T10:30:00Z"}`

### Step 6: Test the workflow
**Owner:** User
- Create a test meeting note in `meetings/notes/`
- Run workflow with `--dry-run` to verify detection
- Run workflow normally to create notification
- Verify no duplicate notification on second run
- Modify note, run again, verify re-notification

### Step 7: Update documentation
**Owner:** Copilot
- Mark status as "Active"
- Document any learnings or edge cases discovered during testing

---

## Overview

This workflow monitors the `meetings/notes/` directory for manual meeting notes you've typed and creates Inbox notifications so you remember to process them (extract tasks, decisions, follow-ups, etc.).

Unlike the `fireflies` workflow which fetches transcripts from an API, this workflow discovers notes you've manually created in your vault.

## How It Works

1. **Load Last Run Time** - Retrieves `last_run` timestamp from state
2. **Find Modified Files** - Scans `meetings/notes/*.md` for files with `mtime > last_run`
3. **Check Inbox** - For each modified file, checks if `_inbox/` already has an active notification pointing to it
4. **Create Notifications** - Creates inbox notification only if no active notification exists
5. **Update State** - Saves current run time as `last_run` for next execution

## State Schema

State is persisted as JSON:
```json
{
  "last_run": "2026-01-03T10:30:00Z"
}
```

## Notification Logic

The workflow uses mtime-based tracking with inbox deduplication:

- **New files**: Created after last run → notify
- **Modified files**: Edited after last run → notify (if no active inbox notification exists)
- **Already notified**: Active inbox notification exists → skip
- **Processed and archived**: Notification moved to `_archive/`, file edited → re-notify

This prevents spam from:
- Running workflow multiple times before processing notifications (inbox check)
- Typo fixes or minor edits after processing (mtime only updates state on successful notification)

## Artifacts Created

- **Inbox Notifications**: `_inbox/{timestamp} — manual_meeting.md`
  - Created for each new/modified manual meeting note without an existing inbox notification
  - Links to the source note file in `meetings/notes/`
  - Minimal metadata (can be expanded as processing patterns emerge)

## Usage

```sh
# Run once manually
uv run python main.py run manual_meetings

# Dry run to see what would happen
uv run python main.py run manual_meetings --dry-run

# Can be scheduled to run periodically
```

## Design Decisions

### Why Last Run Timestamp Instead of Per-File Tracking?

Simpler state management. The inbox deduplication check handles preventing duplicate notifications, so we only need to know "what changed since last run" rather than tracking notification history per file.

### Why Check Inbox Before Notifying?

Prevents notification spam if the workflow runs multiple times before you process notifications. Once you archive the notification (move to `_archive/`), the workflow will re-notify if you edit the source file.

### Why Use mtime Instead of Frontmatter?

Keeps manual notes pristine - no automated modifications. The workflow observes file changes without touching your content.

### Why No Metadata Extraction?

Following the "start simple" principle. Metadata requirements (meeting date, attendees, topics) should emerge organically from manual processing patterns. Can be added later if pain points become clear.

## Related Workflows

- **fireflies** - Fetches meeting transcripts from Fireflies.ai API and creates inbox notifications
