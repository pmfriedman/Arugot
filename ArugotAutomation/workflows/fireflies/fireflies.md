# Fireflies

Fetches meeting transcripts from Fireflies.ai API, saves them to the vault, and creates Inbox notifications for processing.

## Status

**Active** - Fully migrated to Inbox pattern.

## How It Works

1. Fetches meetings from Fireflies.ai API (last 5 days)
2. Writes transcripts to `meetings/transcripts/`
3. Creates Inbox notification for each new transcript linking to the saved file
4. Tracks processed meeting IDs to avoid duplicates

## Folder Structure

- **Transcripts:** `meetings/transcripts/YYYY-MM-DD HHMM — Title — ff_[id].md`
- **Notifications:** `_inbox/YYYYMMDD-HHMMSS-Process-Title-transcript.md`

## Inbox Integration

**Creates notifications:** Yes, for each new transcript

**Notification includes:**
- Link to transcript file
- Meeting title
- List of speakers
- Duration in minutes

**Processing:** Manual, Copilot-assisted, or eventually automated (your choice)

## Usage

Run manually:
```sh
uv run python main.py run fireflies
```

Typically scheduled to run periodically via the scheduler.

---
