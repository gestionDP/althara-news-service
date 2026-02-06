"""
HTML text extraction utilities.
Centralizes tag stripping and basic cleaning used across ingestion and adapters.
"""
from __future__ import annotations

import html
import re
from typing import Optional

try:
    import ftfy
    HAS_FTFY = True
except ImportError:
    HAS_FTFY = False


def strip_html_tags(text: Optional[str]) -> str:
    """
    Remove HTML tags and entities, collapse whitespace.
    Fixes common encoding mojibake (e.g. participaciÃ³n -> participación).
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
    text = text.strip()
    if HAS_FTFY:
        text = ftfy.fix_text(text)
    return text


def format_paragraphs(text: Optional[str], sentences_per_paragraph: int = 4) -> str:
    """
    Convert block text into HTML paragraphs for readability.
    Preserves existing double newlines; otherwise splits every N sentences.
    """
    if not text or not text.strip():
        return ""
    text = text.strip()
    # Preserve existing paragraph breaks (double newline or more)
    blocks = re.split(r'\n\s*\n+', text)
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # If block is short, keep as one paragraph
        if len(block) < 400:
            escaped = html.escape(block)
            result.append(f"<p>{escaped}</p>")
            continue
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', block)
        sentences = [s.strip() for s in sentences if s.strip()]
        for i in range(0, len(sentences), sentences_per_paragraph):
            chunk = " ".join(sentences[i : i + sentences_per_paragraph])
            if chunk:
                escaped = html.escape(chunk)
                result.append(f"<p>{escaped}</p>")
    return "".join(result)
