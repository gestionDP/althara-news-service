"""
HTML text extraction utilities.
Centralizes tag stripping and basic cleaning used across ingestion and adapters.
"""
from __future__ import annotations

import html
import re
from typing import Optional


def strip_html_tags(text: Optional[str]) -> str:
    """
    Remove HTML tags and entities, collapse whitespace.
    Used by RSS ingestors and as base for content cleaning.
    """
    if not text:
        return ""
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = text.decode("latin-1")
            except UnicodeDecodeError:
                text = text.decode("utf-8", errors="replace")
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
