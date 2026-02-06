"""
Tech RSS ingestor for Oxono domain.
Ingests from tech feeds and saves to news with domain='tech'.
"""
import feedparser
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict

from app.models.news import News
from app.constants_tech import (
    TECH_RSS_SOURCES,
    DENY_KEYWORDS,
    ALLOW_KEYWORDS,
    STRICT_REQUIRE_ALLOW,
    MIN_SCORE,
)
from app.tech.classifier import infer_category, extract_tags, compute_relevance_score
from app.utils.html_utils import strip_html_tags
from app.utils.rss_utils import parse_published_date
from app.utils.guardrails import passes_guardrails


async def ingest_tech_rss_sources(
    session: AsyncSession, max_items_per_source: int = 5
) -> Dict[str, int]:
    """
    Ingest tech news from configured RSS sources.
    Saves with domain='tech'.
    Returns source_name -> count inserted.
    """
    results: Dict[str, int] = {}

    for source_config in TECH_RSS_SOURCES:
        source_name = source_config["name"]
        feed_url = source_config["url"]
        source_label = source_config["source"]
        default_category = source_config["default_category"]

        inserted_count = 0

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    feed_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; NewsStudio/1.0; +https://example.com)"
                    },
                )
                response.raise_for_status()
                feed = feedparser.parse(response.text)

            if not getattr(feed, "entries", []):
                results[source_name] = 0
                continue

            processed = 0
            for entry in feed.entries:
                if processed >= max_items_per_source:
                    break

                title = getattr(entry, "title", "Untitled")
                link = getattr(entry, "link", "")
                if not title or not link:
                    continue

                temp_summary = None
                if hasattr(entry, "summary") and entry.summary:
                    temp_summary = strip_html_tags(entry.summary)
                elif hasattr(entry, "description") and entry.description:
                    temp_summary = strip_html_tags(entry.description)

                if not passes_guardrails(
                    title, DENY_KEYWORDS, ALLOW_KEYWORDS, STRICT_REQUIRE_ALLOW,
                    summary=temp_summary, url=link,
                ):
                    continue

                # Dedupe by URL
                stmt = select(News).where(News.url == link)
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    continue

                published_at = parse_published_date(entry)
                category = infer_category(title, temp_summary)
                tags = extract_tags(title, temp_summary)
                relevance_score = compute_relevance_score(
                    title, temp_summary, category, source_label
                )

                if relevance_score < MIN_SCORE:
                    continue

                processed += 1

                new_news = News(
                    title=title,
                    source=source_label,
                    url=link,
                    published_at=published_at,
                    category=category,
                    raw_summary=temp_summary,
                    domain="tech",
                    relevance_score=relevance_score,
                    tags=tags,
                    used_in_social=False,
                )
                session.add(new_news)
                inserted_count += 1

        except Exception:
            inserted_count = 0

        results[source_name] = inserted_count

    if any(results.values()):
        await session.commit()

    return results
