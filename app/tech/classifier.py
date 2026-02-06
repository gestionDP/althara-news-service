"""
Tech news classifier: infer category, extract tags, compute relevance score.
Used by tech RSS ingestor.
"""
import re
from typing import List, Optional

from app.constants_tech import TechNewsCategory


def infer_category(title: str, summary: Optional[str] = None) -> str:
    """
    Infer tech category from title and optional summary.
    """
    text = (title + " " + (summary or "")).lower()

    # AI/ML keywords
    ai_ml = [
        "inteligencia artificial", "ia ", " ai ", "machine learning", "ml ",
        "deep learning", "neural", "llm", "gpt", "claude", "chatgpt",
        "openai", "anthropic", "modelo de lenguaje", "generative ai",
    ]
    if any(kw in text for kw in ai_ml):
        return TechNewsCategory.AI_ML

    # Release/Update
    release = [
        "lanza", "lanzamiento", "actualización", "update", "release",
        "nueva versión", "v2", "v3", "beta", "ga ", "general availability",
    ]
    if any(kw in text for kw in release):
        return TechNewsCategory.RELEASE_UPDATE

    # Tool/Discovery
    tool = [
        "herramienta", "tool", "descubrimiento", "nuevo producto",
        "startup lanza", "plataforma", "software", "app ",
    ]
    if any(kw in text for kw in tool):
        return TechNewsCategory.TOOL_DISCOVERY

    # Research
    research = [
        "investigación", "research", "estudio", "paper", "paper publicado",
        "universidad", "laboratorio", "mit ", "stanford", "nature", "science",
    ]
    if any(kw in text for kw in research):
        return TechNewsCategory.RESEARCH

    # Startups
    startup = [
        "startup", "seed", "serie a", "serie b", "funding", "financiación",
        "venture", "aceleradora", "incubadora", "unicornio",
    ]
    if any(kw in text for kw in startup):
        return TechNewsCategory.STARTUPS

    # Big Tech
    big_tech = [
        "google", "microsoft", "apple", "amazon", "meta", "facebook",
        "alphabet", "nvidia", "tesla", "netflix",
    ]
    if any(kw in text for kw in big_tech):
        return TechNewsCategory.BIG_TECH

    # Security
    security = [
        "cve", "vulnerability", "vulnerabilidad", "patch", "exploit",
        "zero-day", "zeroday", "seguridad", "security", "hack", "ransomware",
    ]
    if any(kw in text for kw in security):
        return TechNewsCategory.SECURITY

    # Policy/Ethics
    policy = [
        "regulación", "regulation", "ética", "ethics", "privacy",
        "privacidad", "gdpr", "antitrust", "competencia", "ley ",
    ]
    if any(kw in text for kw in policy):
        return TechNewsCategory.POLICY_ETHICS

    return TechNewsCategory.OTHER_TECH


def extract_tags(title: str, summary: Optional[str] = None) -> str:
    """
    Extract relevant tags as comma-separated string.
    """
    text = (title + " " + (summary or "")).lower()
    tag_candidates = set()

    # Tech terms
    tech_terms = [
        "ai", "ia", "ml", "llm", "gpt", "startup", "tech", "software",
        "data", "cloud", "saas", "api", "blockchain", "crypto",
        "automation", "robot", "drone", "ar", "vr", "iot",
    ]
    words = re.findall(r"\b[a-záéíóúñ0-9]{3,}\b", text)
    for w in words:
        if w in tech_terms:
            tag_candidates.add(w)
        # Company/product names (capitalized in title)
        if w in ["openai", "anthropic", "google", "microsoft", "meta", "nvidia"]:
            tag_candidates.add(w)

    # Limit to 8 tags
    return ",".join(list(tag_candidates)[:8]) if tag_candidates else ""


def compute_relevance_score(
    title: str, summary: Optional[str], category: str, source: str
) -> int:
    """
    Compute relevance score 0-100 for tech news.
    Higher = more relevant for Oxono/tech audience.
    """
    score = 50  # baseline
    text = (title + " " + (summary or "")).lower()

    # Boost for AI/ML
    if category == TechNewsCategory.AI_ML:
        score += 25
    elif category == TechNewsCategory.RELEASE_UPDATE:
        score += 15
    elif category == TechNewsCategory.TOOL_DISCOVERY:
        score += 15
    elif category == TechNewsCategory.RESEARCH:
        score += 10

    # Boost for keywords
    high_value = ["inteligencia artificial", "ia ", " ai ", "machine learning", "llm", "gpt"]
    if any(kw in text for kw in high_value):
        score += 15

    # Cap
    return min(100, max(0, score))
