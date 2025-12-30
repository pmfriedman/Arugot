"""Minimal Fireflies API client for fetching meeting metadata."""

import logging
from datetime import datetime, timezone

import requests

from settings import settings

logger = logging.getLogger(__name__)

FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"


def list_meetings(since_iso: str | None = None) -> list[dict]:
    """Fetch meetings from Fireflies API.

    Args:
        since_iso: Optional ISO 8601 datetime string. If provided, only return meetings
                   ending after this time.

    Returns:
        List of raw meeting objects from Fireflies API.
    """
    query = """
    query {
      transcripts {
        id
        title
        date
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.fireflies_api_key}",
    }

    try:
        response = requests.post(
            FIREFLIES_API_URL,
            json={"query": query},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            logger.error("Fireflies API returned errors: %s", data["errors"])
            return []

        meetings = data.get("data", {}).get("transcripts", [])

        # Filter by date if requested
        if since_iso:
            since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
            filtered = []
            for meeting in meetings:
                # Fireflies date is Unix timestamp in milliseconds
                meeting_ts = meeting["date"] / 1000
                meeting_date = datetime.fromtimestamp(meeting_ts, tz=timezone.utc)
                if meeting_date >= since_dt:
                    filtered.append(meeting)
            meetings = filtered

        # Log summary
        logger.info("Fetched %d meetings from Fireflies API", len(meetings))

        if meetings:
            # Fireflies date is Unix timestamp in milliseconds
            dates = [
                datetime.fromtimestamp(m["date"] / 1000, tz=timezone.utc)
                for m in meetings
            ]
            earliest = min(dates).strftime("%Y-%m-%d")
            latest = max(dates).strftime("%Y-%m-%d")
            logger.info("Meeting date range: %s to %s", earliest, latest)

        return meetings

    except requests.RequestException as e:
        logger.error("Failed to fetch meetings from Fireflies: %s", e)
        return []


def get_transcript(meeting_id: str) -> dict | None:
    """Fetch full transcript and AI summary for a meeting.

    Args:
        meeting_id: Fireflies meeting/transcript ID

    Returns:
        Raw Fireflies payload with transcript and summary, or None if not ready.
    """
    query = """
    query GetTranscript($transcriptId: String!) {
      transcript(id: $transcriptId) {
        id
        title
        date
        sentences {
          text
          start_time
          speaker_name
        }
        summary {
          overview
          shorthand_bullet
          keywords
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.fireflies_api_key}",
    }

    try:
        response = requests.post(
            FIREFLIES_API_URL,
            json={"query": query, "variables": {"transcriptId": meeting_id}},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            logger.warning(
                "Fireflies API errors for meeting %s: %s", meeting_id, data["errors"]
            )
            return None

        transcript_data = data.get("data", {}).get("transcript")
        if not transcript_data:
            return None

        # Check if transcript has content
        sentences = transcript_data.get("sentences", [])
        if not sentences:
            return None

        # Convert sentence timestamps to UTC datetimes if present
        for sentence in sentences:
            if "start_time" in sentence and sentence["start_time"] is not None:
                sentence["start_time_utc"] = datetime.fromtimestamp(
                    sentence["start_time"], tz=timezone.utc
                )

        return transcript_data

    except requests.RequestException as e:
        logger.warning("Failed to fetch transcript for meeting %s: %s", meeting_id, e)
        return None
