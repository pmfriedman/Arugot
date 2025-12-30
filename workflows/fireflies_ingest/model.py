"""Stable internal representation of Fireflies meeting data."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class FirefliesMeeting:
    """Lossless internal model for Fireflies meeting data.

    This is the ingest contract that future workflows can rely on.
    """

    meeting_id: str
    title: str | None
    platform: str | None
    started_at: datetime
    ended_at: datetime
    duration_seconds: int | None

    organizer: dict | None
    participants: list[dict]

    transcript_sentences: list[dict]
    fireflies_summary: dict | None

    source: str = "fireflies"
