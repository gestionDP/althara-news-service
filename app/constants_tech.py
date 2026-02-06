"""
Oxono Tech News - sources + guardrails.
Goal: IA + dev tools + releases + infra + security.
"""

from typing import TypedDict


class TechNewsCategory:
    RELEASE_UPDATE = "RELEASE_UPDATE"
    TOOL_DISCOVERY = "TOOL_DISCOVERY"
    RESEARCH = "RESEARCH"
    AI_ML = "AI_ML"
    STARTUPS = "STARTUPS"
    BIG_TECH = "BIG_TECH"
    SECURITY = "SECURITY"
    POLICY_ETHICS = "POLICY_ETHICS"
    OTHER_TECH = "OTHER_TECH"


TECH_CATEGORY_LABELS = {
    TechNewsCategory.RELEASE_UPDATE: "Release/Update",
    TechNewsCategory.TOOL_DISCOVERY: "Tool/Discovery",
    TechNewsCategory.RESEARCH: "Research",
    TechNewsCategory.AI_ML: "AI/ML",
    TechNewsCategory.STARTUPS: "Startups",
    TechNewsCategory.BIG_TECH: "Big Tech",
    TechNewsCategory.SECURITY: "Security",
    TechNewsCategory.POLICY_ETHICS: "Policy/Ethics",
    TechNewsCategory.OTHER_TECH: "Other Tech",
}


class RSSSourceConfig(TypedDict):
    name: str
    url: str
    source: str
    default_category: str


TECH_RSS_SOURCES: list[RSSSourceConfig] = [
    # Más pro / menos consumer
    {
        "name": "WIRED ES - Top",
        "url": "https://es.wired.com/feed/rss",
        "source": "WIRED ES",
        "default_category": TechNewsCategory.BIG_TECH,
    },
    {
        "name": "WIRED ES - Seguridad",
        "url": "https://es.wired.com/feed/seguridad/rss",
        "source": "WIRED ES",
        "default_category": TechNewsCategory.SECURITY,
    },
    {
        "name": "Microsiervos",
        "url": "https://www.microsiervos.com/index.xml",
        "source": "Microsiervos",
        "default_category": TechNewsCategory.RESEARCH,
    },
    # Genbeta puede traer ruido => lo controlas por filtros
    {
        "name": "Genbeta",
        "url": "https://www.genbeta.com/index.xml",
        "source": "Genbeta",
        "default_category": TechNewsCategory.TOOL_DISCOVERY,
    },
    # Newsletter dev (RSS Beehiiv)
    {
        "name": "mouredev.log()",
        "url": "https://rss.beehiiv.com/feeds/a7YmYsM8hJ.xml",
        "source": "mouredev.log()",
        "default_category": TechNewsCategory.TOOL_DISCOVERY,
    },
]


# ----------------------------
# Guardrails de relevancia
# ----------------------------

DENY_KEYWORDS = [
    "tdt", "rtve", "televisión", "television", "canal", "series", "streaming",
    "netflix", "hbo", "prime video", "disney", "fútbol", "futbol",
    "chollo", "oferta", "rebaja", "precio", "review", "análisis de", "analisis de",
    "mejor móvil", "mejor movil", "mejor tv", "smart tv",
]

ALLOW_KEYWORDS = [
    # IA
    "ia", "ai", "llm", "agent", "agentes", "rag", "embedding", "vector",
    "inference", "fine-tuning", "multimodal", "openai", "anthropic", "mistral",
    "deepmind", "nvidia", "cuda",
    # Dev
    "vercel", "next.js", "nextjs", "react", "node", "bun", "deno", "typescript",
    "python", "fastapi", "docker", "kubernetes", "sdk", "api", "github", "npm", "pypi",
    "changelog", "release", "v1.", "v2.", "v3.",
    # Security
    "cve", "vulnerability", "vulnerabilidad", "patch", "exploit", "zero-day", "zeroday",
]

# Si quieres “modo estricto”: debe contener AL MENOS 1 allow keyword
STRICT_REQUIRE_ALLOW = True

# Score mínimo para insertar
MIN_SCORE = 2
