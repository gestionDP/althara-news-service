#!/usr/bin/env python3
"""
Script to run news ingestion from command line.

Useful for cron jobs or scheduled execution.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.adapters.news_adapter import build_althara_summary
from app.models.news import News
from sqlalchemy import select


async def ingest_and_adapt():
    """Executes ingestion and adaptation in a single function"""
    async with AsyncSessionLocal() as session:
        try:
            print("📥 Ingesting news from RSS...")
            results = await ingest_rss_sources(session)
            
            total_inserted = sum(results.values())
            print(f"✅ Inserted {total_inserted} new news items")
            
            for source, count in results.items():
                if count > 0:
                    print(f"   - {source}: {count} news items")
            
            print("\n🎨 Adapting news to Althara tone...")
            stmt = select(News).where(News.althara_summary.is_(None))
            result = await session.execute(stmt)
            pending_news = result.scalars().all()
            
            adapted_count = 0
            for news in pending_news:
                try:
                    althara_summary = build_althara_summary(
                        title=news.title,
                        raw_summary=news.raw_summary,
                        category=news.category
                    )
                    news.althara_summary = althara_summary
                    adapted_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error adapting news {news.id}: {e}")
                    continue
            
            if adapted_count > 0:
                await session.commit()
            
            print(f"✅ Adapted {adapted_count} news items to Althara tone")
            
            return {
                "ingested": total_inserted,
                "adapted": adapted_count,
                "success": True
            }
        
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    result = asyncio.run(ingest_and_adapt())
    sys.exit(0 if result.get("success") else 1)





