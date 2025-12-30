"""Fireflies meeting ingest workflow."""

import logging
from datetime import datetime, timezone

from common.types import RunContext
from workflows.fireflies_ingest import client
from workflows.fireflies_ingest.model import FirefliesMeeting
from workflows.fireflies_ingest import writer
from runner.state import save_state

logger = logging.getLogger(__name__)


def normalize_meeting(raw_meeting: dict, transcript_payload: dict) -> FirefliesMeeting:
    """Convert raw Fireflies data into stable internal representation.

    Args:
        raw_meeting: Meeting metadata from list_meetings()
        transcript_payload: Full transcript payload from get_transcript()

    Returns:
        FirefliesMeeting with all fields populated losslessly
    """
    # Extract timestamps from raw meeting
    meeting_ts = raw_meeting["date"] / 1000  # Fireflies uses milliseconds
    ended_at = datetime.fromtimestamp(meeting_ts, tz=timezone.utc)

    # Extract sentences and compute duration
    sentences = transcript_payload.get("sentences", [])
    duration_seconds = None
    if sentences and len(sentences) > 0:
        # Calculate duration from first to last sentence timestamp
        valid_times = [
            s.get("start_time") for s in sentences if s.get("start_time") is not None
        ]
        if valid_times:
            duration_seconds = int(max(valid_times) - min(valid_times))

    # Use ended_at as started_at approximation if we have duration
    started_at = ended_at
    if duration_seconds:
        started_at = datetime.fromtimestamp(
            meeting_ts - duration_seconds, tz=timezone.utc
        )

    return FirefliesMeeting(
        meeting_id=transcript_payload["id"],
        title=transcript_payload.get("title"),
        platform=None,  # Not provided by current API query
        started_at=started_at,
        ended_at=ended_at,
        duration_seconds=duration_seconds,
        organizer=None,  # Not provided by current API query
        participants=[],  # Not provided by current API query
        transcript_sentences=sentences,
        fireflies_summary=transcript_payload.get("summary"),
    )


def run(context: RunContext, state: dict) -> dict:
    """Fetch meetings from Fireflies API with cursor-based deduplication.

    State schema:
        {
            "processed_ids": [],
            "last_meeting_ended_at": null
        }

    No state updates or file writes during dry-run.
    """
    logger.info("Starting Fireflies meeting ingest")

    # Load state with defaults
    processed_ids = state.get("processed_ids", [])
    last_meeting_ended_at = state.get("last_meeting_ended_at")

    # Determine time window
    since_iso = None
    if last_meeting_ended_at:
        since_iso = last_meeting_ended_at
        logger.info("Using cursor: %s", since_iso)
    else:
        logger.info("First run — no cursor found")

    # Fetch meetings
    meetings = client.list_meetings(since_iso=since_iso)
    logger.info("Fetched %d meetings", len(meetings))

    # Convert dates to UTC datetimes and sort
    for meeting in meetings:
        # Fireflies date is Unix timestamp in milliseconds
        meeting_ts = meeting["date"] / 1000
        meeting["ended_at_utc"] = datetime.fromtimestamp(meeting_ts, tz=timezone.utc)

    # Sort by ended_at ascending
    meetings.sort(key=lambda m: m["ended_at_utc"])

    # Deduplicate
    candidates = []
    skipped_count = 0

    for meeting in meetings:
        meeting_id = meeting["id"]

        if meeting_id in processed_ids:
            logger.info("Skipping meeting %s: already processed", meeting_id)
            skipped_count += 1
            continue

        candidates.append(meeting)

    # Log results
    logger.info("Meetings skipped (already processed): %d", skipped_count)
    logger.info("Meetings accepted (new candidates): %d", len(candidates))

    # Fetch transcripts and filter by readiness
    ready_meetings = []
    transcript_not_ready_count = 0

    for meeting in candidates:
        meeting_id = meeting["id"]
        transcript = client.get_transcript(meeting_id)

        if transcript is None:
            logger.info("Skipping meeting %s — transcript not ready", meeting_id)
            transcript_not_ready_count += 1
            continue

        # Attach transcript to meeting
        meeting["transcript"] = transcript

        # Log transcript stats
        sentence_count = len(transcript.get("sentences", []))
        has_summary = bool(transcript.get("summary"))
        logger.info(
            "Meeting %s ready: %d sentences, summary=%s",
            meeting_id,
            sentence_count,
            has_summary,
        )

        ready_meetings.append(meeting)

    # Log transcript fetching results
    logger.info("Meetings ready for ingest: %d", len(ready_meetings))
    logger.info(
        "Meetings skipped (transcript not ready): %d", transcript_not_ready_count
    )

    # Normalize meetings into stable internal representation
    normalized_meetings: list[FirefliesMeeting] = []

    for meeting in ready_meetings:
        normalized = normalize_meeting(meeting, meeting["transcript"])
        normalized_meetings.append(normalized)

        # Log normalization details
        logger.info(
            "Normalized meeting %s: %d sentences, summary=%s",
            normalized.meeting_id,
            len(normalized.transcript_sentences),
            normalized.fireflies_summary is not None,
        )

    logger.info("Meetings normalized successfully: %d", len(normalized_meetings))

    # Write meetings to Obsidian
    successfully_written: list[FirefliesMeeting] = []
    written_count = 0

    if context.args.get("dry_run", False):
        logger.info("[DRY-RUN] Skipping file writes")
        for meeting in normalized_meetings:
            # Compute what the path would be
            from pathlib import Path

            date_str = meeting.ended_at.strftime("%Y-%m-%d")
            title_part = meeting.title if meeting.title else "Meeting"
            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "" for c in title_part
            )
            safe_title = " ".join(safe_title.split())
            filename = f"{date_str} — {safe_title} — ff_{meeting.meeting_id}.md"
            from settings import settings

            output_path = (
                Path(settings.obsidian_vault_dir) / "_ingest" / "fireflies" / filename
            )
            logger.info("[DRY-RUN] Would write: %s", output_path)
    else:
        for meeting in normalized_meetings:
            path = writer.write_meeting(meeting)

            # Verify file exists
            if path.exists():
                # Check if it was newly written or already existed
                if any(
                    meeting.meeting_id == m.meeting_id for m in successfully_written
                ):
                    continue  # Already tracked

                # Determine if this was a new write by checking if file was just created
                # writer.write_meeting logs "File already exists" or "Wrote meeting to"
                # We track success if file exists regardless
                successfully_written.append(meeting)

                # Track if it was new or existing (writer logs this, but count here too)
                written_count += 1

        logger.info("Files written or already existed: %d", written_count)

    # Compute new state in-memory
    new_processed_ids = processed_ids.copy()
    new_last_meeting_ended_at = last_meeting_ended_at

    if successfully_written:
        # Add newly written meeting IDs (union)
        for meeting in successfully_written:
            if meeting.meeting_id not in new_processed_ids:
                new_processed_ids.append(meeting.meeting_id)

        # Advance cursor to max ended_at of successfully written meetings
        max_ended_at = max(m.ended_at for m in successfully_written)
        new_last_meeting_ended_at = max_ended_at.isoformat()

    # Log state changes
    ids_added = len(new_processed_ids) - len(processed_ids)
    logger.info(
        "Processed IDs: %d → %d (added %d)",
        len(processed_ids),
        len(new_processed_ids),
        ids_added,
    )

    if new_last_meeting_ended_at != last_meeting_ended_at:
        logger.info(
            "Cursor advancement: %s → %s",
            last_meeting_ended_at,
            new_last_meeting_ended_at,
        )
    else:
        logger.info("Cursor unchanged: %s", last_meeting_ended_at)

    # Persist state
    if context.args.get("dry_run", False):
        logger.info("[DRY-RUN] State not persisted")
    else:
        if ids_added > 0 or new_last_meeting_ended_at != last_meeting_ended_at:
            new_state = {
                "processed_ids": new_processed_ids,
                "last_meeting_ended_at": new_last_meeting_ended_at,
            }
            save_state("fireflies_ingest", new_state)
            logger.info("State persisted successfully")
        else:
            logger.info("No state changes to persist")

    return {
        "processed_ids": new_processed_ids,
        "last_meeting_ended_at": new_last_meeting_ended_at,
    }
