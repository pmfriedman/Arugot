"""Minimal Fireflies API client for fetching meeting metadata."""

import logging
from datetime import datetime, timezone

import httpx

from settings import settings

logger = logging.getLogger(__name__)

FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"


async def list_meetings(since_iso: str | None = None) -> list[dict]:
    """Fetch meetings from Fireflies API with server-side filtering and pagination.

    Args:
        since_iso: Optional ISO 8601 datetime string. If provided, only return meetings
                   created after this time (filters at API level).

    Returns:
        List of raw meeting objects from Fireflies API.
    """
    query = """
    query GetTranscripts($fromDate: DateTime, $limit: Int, $skip: Int) {
      transcripts(fromDate: $fromDate, limit: $limit, skip: $skip) {
        id
        title
        date
        meeting_info {
            summary_status
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.fireflies_api_key}",
    }

    all_meetings = []
    skip = 0
    limit = 50  # Maximum allowed by API

    try:
        async with httpx.AsyncClient() as client:
            while True:
                variables: dict[str, int | str] = {
                    "limit": limit,
                    "skip": skip,
                }

                if since_iso:
                    variables["fromDate"] = since_iso

                response = await client.post(
                    FIREFLIES_API_URL,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    logger.error("Fireflies API returned errors: %s", data["errors"])
                    break

                meetings = data.get("data", {}).get("transcripts", [])

                if not meetings:
                    break  # No more meetings to fetch

                all_meetings.extend(meetings)
                logger.info("Fetched batch: %d meetings (skip=%d)", len(meetings), skip)

                # If we got fewer than limit, we've reached the end
                if len(meetings) < limit:
                    break

                skip += limit

        # Log summary
        logger.info("Fetched %d total meetings from Fireflies API", len(all_meetings))

        if all_meetings:
            # Fireflies date is Unix timestamp in milliseconds
            dates = [
                datetime.fromtimestamp(m["date"] / 1000, tz=timezone.utc)
                for m in all_meetings
            ]
            earliest = min(dates).strftime("%Y-%m-%d")
            latest = max(dates).strftime("%Y-%m-%d")
            logger.info("Meeting date range: %s to %s", earliest, latest)

        return all_meetings

    except httpx.HTTPError as e:
        logger.error("Failed to fetch meetings from Fireflies: %s", e)
        return []


async def get_transcript(meeting_id: str) -> dict | None:
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
        speakers {
            id
            name
        }
        meeting_attendees {
            displayName
            email
            phoneNumber
            name
            location
        }
        summary {
            keywords
            action_items
            outline
            shorthand_bullet
            overview
            bullet_gist
            gist
            short_summary
            short_overview
            meeting_type
            topics_discussed
            transcript_chapters
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.fireflies_api_key}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
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

    except httpx.HTTPError as e:
        logger.warning("Failed to fetch transcript for meeting %s: %s", meeting_id, e)
        return None
