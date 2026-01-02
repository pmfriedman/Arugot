# Manual Meeting Notes Design

## Overview
Support human-authored meeting notes in a format that synth workflows can consume alongside automated Fireflies transcripts.

## File Location
```
_scratch/human/meetings/
```

Separates human-authored notes from machine-generated records in `_scratch/auto/meetings/`.

## Filename Convention
```
YYYY-MM-DD HHMM — Meeting Title.md
```

Examples:
- `2026-01-02 1430 — Quarterly Planning.md`
- `2026-01-05 0900 — Standup.md`

## Frontmatter Schema

### Required Fields
```yaml
---
source: manual
meeting_date: 2026-01-02T14:30:00-08:00  # ISO 8601 with timezone
---
```

## Quick Capture Workflow

### CLI Command (MVP)
```bash
uv run python main.py new meeting
```

Creates a timestamped meeting note and opens it in Obsidian:
1. Auto-generates filename: `YYYY-MM-DD HHMM — Meeting.md`
2. Creates file in `_scratch/human/meetings/` with frontmatter template
3. Opens in Obsidian via `obsidian://` URI protocol

**PowerShell alias:**
```powershell
function meeting { uv run python main.py new meeting }
```

**AutoHotkey (ultimate zero friction):**
```ahk
^!m::  ; Ctrl+Alt+M
Run, uv run python main.py new meeting, C:\dev\Arugot
return
```

Press `Ctrl+Alt+M` → meeting note created and opened in Obsidian instantly.

### Future: Outlook Calendar Integration

Long-term vision: `ingest_outlook_calendar` workflow that:
- Fetches today's meetings from Outlook (Microsoft Graph API)
- Pre-creates meeting notes with calendar metadata (title, participants, time)
- Runs on schedule (e.g., daily at 8am) or on-demand
- Provides OneNote-like experience with zero manual work
