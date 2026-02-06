"""
IG-ready draft generator. Extract + Compose pipeline.
No truncation mid-sentence. Semantic compression: extract facts → compose copy.

Althara: quiet luxury, señal e implicaciones.
Oxono: systems thinking, operacional.
"""
from __future__ import annotations

import re
from typing import Any, List, Optional

from app.brands import get_domain_for_brand
from app.adapters.news_adapter import (
    _clean_html,
    _extract_key_data,
    _extract_keywords,
    _build_strategic_line,
    _build_disclaimer,
)
from app.utils.text_compaction import (
    split_sentences,
    truncate_at_sentence,
    extract_key_sentences,
    extract_bullets,
    compose_slide_body,
    compose_caption_blocks,
)


BODY_MAX = 110
SLIDES_COUNT = 3  # intro, cuerpo, cierre con frases completas de la noticia

ALTHARA_CAPTION_MAX = 900
ALTHARA_HASHTAGS_MIN = 8
ALTHARA_HASHTAGS_MAX = 12

OXONO_CAPTION_MIN = 500
OXONO_CAPTION_MAX = 850
OXONO_HASHTAGS_MIN = 6
OXONO_HASHTAGS_MAX = 10


def _to_slide_body(text: str, max_len: int = BODY_MAX) -> str:
    """Ensure complete sentence, never cut mid-word."""
    if len(text) <= max_len:
        return text
    return truncate_at_sentence(text, max_len)


# ========== ALTHARA ==========

def _extract_althara(
    title: str,
    raw_summary: Optional[str],
    category: Optional[str],
) -> tuple[List[str], str]:
    """Extract frases completas que caben en 110 chars. Sin truncar."""
    cleaned = _clean_html(raw_summary or title)
    frases = extract_key_sentences(title, cleaned, max_chars=BODY_MAX, max_sentences=4)

    strategic = _build_strategic_line(category) or ""
    parts = split_sentences(strategic)
    # Solo usar lectura si la frase completa cabe
    lectura = ""
    if parts:
        first = parts[0].strip()
        if len(first) <= BODY_MAX:
            lectura = first
    if not lectura:
        lectura = "Lectura en el enlace."

    return frases, lectura


def _compose_slides_althara(
    frases: List[str],
    lectura: str,
    seed: int,
) -> List[dict]:
    """3 slides: intro (hecho), cuerpo (contexto), cierre. Solo frases completas de la noticia."""
    slides: List[dict] = []
    ctas = ["Guárdalo.", "Seguimos monitorizando."]
    cta = ctas[seed % len(ctas)]

    # Slide 1: Hecho clave (frase 1)
    s1 = frases[0] if frases else "Hecho en el enlace."
    slides.append({"title": "Hecho", "body": s1})

    # Slide 2: Contexto (frase 2)
    s2 = frases[1] if len(frases) > 1 else "Contexto en el enlace."
    slides.append({"title": "Contexto", "body": s2})

    # Slide 3: Cierre (frase 3, o lectura si cabe, o CTA corto)
    if len(frases) > 2:
        s3 = frases[2]
    elif len(lectura) <= BODY_MAX and lectura != "Lectura en el enlace.":
        s3 = lectura
    else:
        s3 = cta
    slides.append({"title": "Cierre", "body": s3})

    return slides[:SLIDES_COUNT]


def _compose_caption_althara(
    bullets: List[str],
    lectura: str,
    source: str,
    seed: int,
) -> str:
    """Caption: Hook, hechos, lectura, CTA, fuente. No raw summary."""
    hooks = [
        "Señal de reactivación en demanda.",
        "Señal en el desplazamiento del mercado.",
    ]
    hook = hooks[seed % len(hooks)]
    ctas = ["Guárdalo.", "Seguimos monitorizando."]
    cta = ctas[seed % len(ctas)]

    fact_lines = bullets[:3] if bullets else ["Hecho en el enlace."]
    return compose_caption_blocks(hook, fact_lines, lectura, cta, source, ALTHARA_CAPTION_MAX)


def _build_hashtags_althara(category: Optional[str], seed: int) -> List[str]:
    base = ["#inmobiliaria", "#althara"]
    cat_map = {
        "PRECIOS_VIVIENDA": ["#preciosvivienda", "#mercadoinmobiliario"],
        "HIPOTECAS_Y_CREDITO": ["#hipotecas", "#financiacion"],
        "NOTICIAS_HIPOTECAS": ["#hipotecas", "#financiacion"],
        "INVERSION_INSTITUCIONAL": ["#fondosinversion", "#inversioninmobiliaria"],
        "FONDOS_INVERSION_INMOBILIARIA": ["#fondosinversion", "#inversioninmobiliaria"],
    }
    base.extend(cat_map.get(category or "", ["#mercadoinmobiliario"]))
    extra = ["#datos", "#tendencias", "#sector", "#mercado"]
    for i in range(4):
        tag = extra[(seed + i) % len(extra)]
        if tag not in base:
            base.append(tag)
        if len(base) >= ALTHARA_HASHTAGS_MAX:
            break
    while len(base) < ALTHARA_HASHTAGS_MIN:
        base.append(f"#news{(seed + len(base)) % 10}")
    return base[:ALTHARA_HASHTAGS_MAX]


# ========== OXONO ==========

def _extract_oxono(
    title: str,
    raw_summary: Optional[str],
) -> tuple[List[str], str]:
    cleaned = _clean_html(raw_summary or title)
    frases = extract_key_sentences(title, cleaned, max_chars=BODY_MAX, max_sentences=4)
    conclusion = "Impacto técnico en ejecución."
    return frases, conclusion


def _compose_slides_oxono(
    frases: List[str],
    conclusion: str,
    seed: int,
) -> List[dict]:
    """3 slides: tesis, hecho, cierre. Solo frases completas de la noticia."""
    slides: List[dict] = []

    s1 = frases[0] if frases else "Tesis en el enlace."
    slides.append({"title": "Tesis", "body": s1})

    s2 = frases[1] if len(frases) > 1 else "Hecho en el enlace."
    slides.append({"title": "Hecho", "body": s2})

    s3 = frases[2] if len(frases) > 2 else conclusion
    slides.append({"title": "Cierre", "body": s3})

    return slides[:SLIDES_COUNT]


def _compose_caption_oxono(
    bullets: List[str],
    conclusion: str,
    source: str,
    url: Optional[str],
) -> str:
    hook = bullets[0] if bullets else "Contexto técnico."
    takeaways = "• Validar supuestos • Medir impacto • Ajustar criterio"
    source_line = f"Fuente: {source}"
    if url:
        source_line += f" | {url}"
    caption = f"{hook}\n\n{takeaways}\n\n{source_line}"
    if len(caption) > OXONO_CAPTION_MAX:
        caption = truncate_at_sentence(caption, OXONO_CAPTION_MAX)
    return caption


def _build_hashtags_oxono(category: Optional[str], seed: int) -> List[str]:
    base = ["#tech", "#oxono"]
    cat_map = {
        "AI_ML": ["#ia", "#machinelearning"],
        "RELEASE_UPDATE": ["#producto", "#lanzamiento"],
        "TOOL_DISCOVERY": ["#herramientas", "#startups"],
    }
    base.extend(cat_map.get(category or "", ["#tecnologia"]))
    extra = ["#datos", "#sistemas", "#ejecución"]
    for i in range(3):
        tag = extra[(seed + i) % len(extra)]
        if tag not in base:
            base.append(tag)
        if len(base) >= OXONO_HASHTAGS_MAX:
            break
    while len(base) < OXONO_HASHTAGS_MIN:
        base.append(f"#tech{(seed + len(base)) % 10}")
    return base[:OXONO_HASHTAGS_MAX]


# ========== PUBLIC API ==========

def generate_ig_draft(
    news: Any,
    tone: str = "neutral",
    language: str = "es",
    brand: str = "althara",
    seed: Optional[int] = None,
) -> dict:
    """
    Extract + Compose. No mid-sentence truncation.
    """
    domain = get_domain_for_brand(brand) or "real_estate"
    brand_voice = "althara" if domain == "real_estate" else "oxono"
    s = hash(str(news.id)) % 10000 if seed is None else seed

    if brand_voice == "althara":
        bullets, lectura = _extract_althara(
            news.title, news.raw_summary, news.category
        )
        carousel_slides = _compose_slides_althara(bullets, lectura, s)
        caption = _compose_caption_althara(bullets, lectura, news.source, s)
        hashtags = _build_hashtags_althara(news.category, s)
        cta = "Guárdalo." if s % 2 == 0 else "Seguimos monitorizando."
    else:
        bullets, conclusion = _extract_oxono(news.title, news.raw_summary)
        carousel_slides = _compose_slides_oxono(bullets, conclusion, s)
        caption = _compose_caption_oxono(
            bullets, conclusion, news.source, getattr(news, "url", None)
        )
        hashtags = _build_hashtags_oxono(news.category, s)
        cta = "Validar criterio."

    source_line = f"Fuente: {news.source}"
    if news.url:
        source_line += f" | {news.url}"
    disclaimer = _build_disclaimer(news.source, news.url)

    hook = carousel_slides[0]["body"] if carousel_slides else ""

    return {
        "hook": hook,
        "carousel_slides": carousel_slides,
        "caption": caption,
        "hashtags": hashtags,
        "cta": cta,
        "source_line": source_line,
        "disclaimer": disclaimer,
        "tone": tone,
        "language": language,
        "status": "DRAFT",
    }


def generate_variants(
    news: Any,
    n: int = 3,
    tone: str = "neutral",
    language: str = "es",
    brand: str = "althara",
) -> List[dict]:
    """Generate N variants with different seeds."""
    base_seed = hash(str(news.id)) % 10000
    return [
        generate_ig_draft(news, tone=tone, language=language, brand=brand, seed=base_seed + i * 7)
        for i in range(n)
    ]
