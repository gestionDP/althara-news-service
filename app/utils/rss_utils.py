"""
RSS parsing utilities.
Centralizes common helpers for feed parsing and entry handling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def parse_published_date(entry: Any) -> datetime:
    """
    Parse publication/update date from a feedparser entry.
    Falls back to current UTC time if parsing fails.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc)
