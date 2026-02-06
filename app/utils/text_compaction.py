"""
Text compaction: truncate at sentence/word boundary, extract bullets, compose copy.
No mid-word or mid-sentence cuts. Semantic compression via extraction + composition.
"""
from __future__ import annotations

import re
from typing import List, Optional


def split_sentences(text: str) -> List[str]:
    """Split text into sentences. Keeps trailing punctuation."""
    if not text or not text.strip():
        return []
    # Split on . ! ? followed by space or end
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def truncate_at_sentence(text: str, max_chars: int) -> str:
    """
    Truncate at sentence boundary. If no sentence end in range, truncate at last space.
    Never cuts mid-word.
    """
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    # Prefer cut at sentence end
    for sep in [". ", "! ", "? "]:
        last = truncated.rfind(sep)
        if last >= 0 and (last >= 10 or last > max_chars // 2):
            return truncated[: last + len(sep)].rstrip()
    # Fallback: cut at word boundary; avoid ending with dangling prepositions (a, de, en, y, etc.)
    _DANGLING = frozenset(["a", "de", "en", "y", "o", "u", "con", "por", "para", "al", "del", "un", "una"])
    while True:
        last_space = truncated.rfind(" ")
        if last_space <= 0:
            break
        result = truncated[:last_space].rstrip()
        last_word = result.split()[-1] if result.split() else ""
        if last_word.lower() not in _DANGLING:
            return result
        truncated = result
    return truncated.rstrip()


def extract_key_sentences(
    title: str,
    cleaned: str,
    max_chars: int = 110,
    max_sentences: int = 4,
) -> List[str]:
    """
    Extract ONLY complete sentences that fit in max_chars. No truncation.
    Prefers sentences with numbers. Returns sentences in importance order.
    """
    candidates: List[tuple[int, str]] = []
    has_number = re.compile(r'\d+[.,]?\d*\s*%|\d+[.,]?\d*')

    # Title first if it fits
    title_clean = title.strip()
    if title_clean and len(title_clean) <= max_chars and not title_clean.endswith("…"):
        candidates.append((2, title_clean))  # title gets priority

    for s in split_sentences(cleaned):
        s = s.strip()
        if len(s) < 15 or len(s) > max_chars:
            continue
        if any(s[:25] in c or c[:25] in s for _, c in candidates):
            continue
        score = 2 if has_number.search(s) else 1
        candidates.append((score, s))

    candidates.sort(key=lambda x: (-x[0], -len(x[1])))  # higher score first, then longer
    seen: set[str] = set()
    result: List[str] = []
    for _, s in candidates:
        key = s[:40]
        if key in seen:
            continue
        seen.add(key)
        result.append(s)
        if len(result) >= max_sentences:
            break
    return result


def extract_bullets(
    title: str,
    raw_summary: Optional[str],
    cleaned: str,
    max_bullets: int = 4,
) -> List[str]:
    """Alias: extract key sentences that fit in 110 chars."""
    return extract_key_sentences(title, cleaned, max_chars=110, max_sentences=max_bullets)


def compose_slide_body(bullets: List[str], fallback: str, max_chars: int = 110) -> str:
    """Take first bullet or fallback, ensure complete sentence and <= max_chars."""
    if bullets:
        s = bullets[0]
    else:
        s = fallback
    if len(s) <= max_chars:
        return s
    return truncate_at_sentence(s, max_chars)


def compose_caption_blocks(
    hook: str,
    bullets: List[str],
    lectura: str,
    cta: str,
    source: str,
    max_total: int = 900,
) -> str:
    """
    Compose caption from blocks. If over max_total, shorten bullets/lectura
    using truncate_at_sentence, never cutting mid-sentence.
    """
    blocks = [
        hook,
        "\n".join(bullets[:3]) if bullets else "",
        lectura,
        cta,
        f"Fuente: {source}",
    ]
    parts = [b.strip() for b in blocks if b.strip()]
    caption = "\n\n".join(parts)

    if len(caption) <= max_total:
        return caption

    # Shorten from the middle: reduce lectura and bullets
    target = max_total - len(hook) - len(cta) - len(f"Fuente: {source}") - 30
    if bullets:
        bullet_text = "\n".join(bullets[:2])
        if len(bullet_text) > target // 2:
            bullet_text = truncate_at_sentence(bullet_text, target // 2)
        lectura_short = truncate_at_sentence(lectura, target // 2) if lectura else ""
        caption = f"{hook}\n\n{bullet_text}\n\n{lectura_short}\n\n{cta}\n\nFuente: {source}"
    else:
        lectura_short = truncate_at_sentence(lectura, target) if lectura else ""
        caption = f"{hook}\n\n{lectura_short}\n\n{cta}\n\nFuente: {source}"

    return truncate_at_sentence(caption, max_total) if len(caption) > max_total else caption
