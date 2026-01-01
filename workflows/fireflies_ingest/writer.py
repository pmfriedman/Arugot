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

    # Generate deterministic filename with timestamp for chronological sorting
    datetime_str = meeting.ended_at.strftime("%Y-%m-%d %H%M")
    title_part = meeting.title if meeting.title else "Meeting"
    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title_part)
    safe_title = " ".join(safe_title.split())  # Collapse whitespace
    filename = f"{datetime_str} — {safe_title} — ff_{meeting.meeting_id}.md"

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

    # Participants array - only include speakers in frontmatter
    lines.append("participants:")
    if meeting.participants:
        speakers_only = [p for p in meeting.participants if p.get("source") == "speakers"]
        if speakers_only:
            for participant in speakers_only:
                name = participant.get("name", "Unknown")
                lines.append(f"  - {name}")
        else:
            lines.append("  []")
    else:
        lines.append("  []")

    lines.append("status: raw")
    lines.append("---")
    lines.append("")

    # Fireflies Summary section
    lines.append("## Fireflies Summary")
    lines.append("")
    if meeting.fireflies_summary:
        summary = meeting.fireflies_summary

        # Overview/Short Summary
        if summary.get("overview"):
            lines.append("### Overview")
            lines.append("")
            lines.append(summary["overview"].strip())
            lines.append("")
        elif summary.get("short_overview"):
            lines.append("### Overview")
            lines.append("")
            lines.append(summary["short_overview"].strip())
            lines.append("")
        elif summary.get("short_summary"):
            lines.append("### Summary")
            lines.append("")
            lines.append(summary["short_summary"].strip())
            lines.append("")

        # Keywords
        if summary.get("keywords"):
            lines.append("### Keywords")
            lines.append("")
            if isinstance(summary["keywords"], list):
                lines.append(", ".join(summary["keywords"]))
            else:
                lines.append(str(summary["keywords"]))
            lines.append("")

        # Action Items
        if summary.get("action_items"):
            lines.append("### Action Items")
            lines.append("")
            if isinstance(summary["action_items"], list):
                for item in summary["action_items"]:
                    lines.append(f"- {item}")
            else:
                lines.append(summary["action_items"].strip())
            lines.append("")

        # Topics Discussed
        if summary.get("topics_discussed"):
            lines.append("### Topics Discussed")
            lines.append("")
            if isinstance(summary["topics_discussed"], list):
                for topic in summary["topics_discussed"]:
                    lines.append(f"- {topic}")
            else:
                lines.append(summary["topics_discussed"].strip())
            lines.append("")

        # Outline
        if summary.get("outline"):
            lines.append("### Outline")
            lines.append("")
            lines.append(summary["outline"].strip())
            lines.append("")

        # Bullet Gist or Shorthand Bullet
        if summary.get("bullet_gist"):
            lines.append("### Key Points")
            lines.append("")
            if isinstance(summary["bullet_gist"], list):
                for bullet in summary["bullet_gist"]:
                    lines.append(f"- {bullet}")
            else:
                lines.append(summary["bullet_gist"].strip())
            lines.append("")
        elif summary.get("shorthand_bullet"):
            lines.append("### Key Points")
            lines.append("")
            if isinstance(summary["shorthand_bullet"], list):
                for bullet in summary["shorthand_bullet"]:
                    lines.append(f"- {bullet}")
            else:
                lines.append(summary["shorthand_bullet"].strip())
            lines.append("")

        # Gist
        if summary.get("gist"):
            lines.append("### Gist")
            lines.append("")
            lines.append(summary["gist"].strip())
            lines.append("")

        # Meeting Type
        if summary.get("meeting_type"):
            lines.append(f"**Meeting Type:** {summary['meeting_type']}")
            lines.append("")

        # Transcript Chapters
        if summary.get("transcript_chapters"):
            lines.append("### Chapters")
            lines.append("")
            if isinstance(summary["transcript_chapters"], list):
                for chapter in summary["transcript_chapters"]:
                    if isinstance(chapter, dict):
                        title = chapter.get("title", "")
                        start = chapter.get("start_time", "")
                        lines.append(f"- **{title}** ({start})")
                    else:
                        lines.append(f"- {chapter}")
            else:
                lines.append(summary["transcript_chapters"].strip())
            lines.append("")
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
