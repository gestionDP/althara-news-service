"""
Content relevance guardrails.
Generic keyword-based filtering used by Althara and Tech ingestors.
"""
from __future__ import annotations

from typing import Iterable, Optional


def passes_guardrails(
    title: str,
    deny_keywords: Iterable[str],
    allow_keywords: Iterable[str],
    strict_require_allow: bool,
    summary: Optional[str] = None,
    url: str = "",
) -> bool:
    """
    Check if content passes deny/allow keyword filters.
    If strict_require_allow is True, at least one allow keyword must match.
    """
    if not title:
        return False
    text = (title + " " + (summary or "") + " " + url).lower()
    for kw in deny_keywords:
        if kw in text:
            return False
    if strict_require_allow:
        if not any(kw in text for kw in allow_keywords):
            return False
    return True
