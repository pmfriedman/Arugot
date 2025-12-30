"""Write Fireflies meetings to Obsidian vault as raw ingest notes."""

import logging
from datetime import datetime
from pathlib import Path

from settings import settings
from workflows.fireflies_ingest.model import FirefliesMeeting

logger = logging.getLogger(__name__)


def write_meeting(meeting: FirefliesMeeting) -> Path:
    """Write a single Fireflies meeting as an append-only Obsidian note.

    Args:
        meeting: Normalized FirefliesMeeting object

    Returns:
        Path to the written (or existing) file
    """
    # Determine output directory
    output_dir = Path(settings.obsidian_vault_dir) / "_ingest" / "fireflies"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate deterministic filename
    date_str = meeting.ended_at.strftime("%Y-%m-%d")
    title_part = meeting.title if meeting.title else "Meeting"
    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title_part)
    safe_title = " ".join(safe_title.split())  # Collapse whitespace
    filename = f"{date_str} — {safe_title} — ff_{meeting.meeting_id}.md"

    output_path = output_dir / filename

    # Skip if already exists
    if output_path.exists():
        logger.info("File already exists: %s", output_path)
        return output_path

    # Build file content
    content = _build_note_content(meeting)

    # Write file
    output_path.write_text(content, encoding="utf-8")
    logger.info("Wrote meeting to: %s", output_path)

    return output_path


def _build_note_content(meeting: FirefliesMeeting) -> str:
    """Build the complete markdown content for a meeting note.

    Args:
        meeting: Normalized FirefliesMeeting object

    Returns:
        Complete markdown content with frontmatter and body
    """
    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append("source: fireflies")
    lines.append(f"fireflies_id: {meeting.meeting_id}")
    lines.append(f"meeting_date: {meeting.ended_at.isoformat()}")

    # Participants array (empty if not available)
    lines.append("participants:")
    if meeting.participants:
        for participant in meeting.participants:
            name = participant.get("name", "Unknown")
            lines.append(f"  - {name}")
    else:
        lines.append("  []")

    lines.append("status: raw")
    lines.append("---")
    lines.append("")

    # Fireflies Summary section
    lines.append("## Fireflies Summary")
    lines.append("")
    if meeting.fireflies_summary:
        summary_text = meeting.fireflies_summary.get("text", "")
        lines.append(summary_text.strip())
    else:
        lines.append("(No summary available)")
    lines.append("")

    # Transcript section
    lines.append("## Transcript")
    lines.append("")
    if meeting.transcript_sentences:
        for sentence in meeting.transcript_sentences:
            speaker = sentence.get("speaker_name", "Unknown")
            text = sentence.get("text", "")
            lines.append(f"{speaker}: {text}")
    else:
        lines.append("(No transcript available)")
    lines.append("")

    # Metadata section
    lines.append("## Metadata")
    lines.append("")

    platform = meeting.platform if meeting.platform else "Unknown"
    lines.append(f"- Platform: {platform}")

    if meeting.duration_seconds:
        duration_minutes = meeting.duration_seconds // 60
        lines.append(f"- Duration: {duration_minutes} minutes")
    else:
        lines.append("- Duration: Unknown")

    lines.append("")

    return "\n".join(lines)
