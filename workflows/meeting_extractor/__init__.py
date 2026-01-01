"""Meeting Extractor Workflow

A schedule-driven, idempotent workflow that ensures every ingested
meeting transcript has exactly one corresponding machine-owned working document.

Operates as a filesystem reconciler — no LLM analysis, just structural creation.
"""

from workflows.meeting_extractor.workflow import run

__all__ = ["run"]
