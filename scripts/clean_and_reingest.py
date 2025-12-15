#!/usr/bin/env python3
"""
Script to clean all news and reingest from scratch.

⚠️ WARNING: This script deletes ALL news items from the database.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.adapters.news_adapter import build_althara_summary
from sqlalchemy import select, delete


async def clean_and_reingest():
    """Cleans all news and reingests from scratch"""
    async with AsyncSessionLocal() as session:
        try:
            print("📊 Checking existing news...")
            stmt = select(News)
            result = await session.execute(stmt)
            existing_news = result.scalars().all()
            total_existing = len(existing_news)
            
            if total_existing > 0:
                print(f"⚠️  Found {total_existing} news items in database")
                print("🗑️  Deleting all news items...")
                
                delete_stmt = delete(News)
                await session.execute(delete_stmt)
                await session.commit()
                
                print(f"✅ Deleted {total_existing} news items")
            else:
                print("ℹ️  No news items to delete")
            
            print("\n📥 Ingesting news from RSS with new categorization system...")
            results = await ingest_rss_sources(session)
            
            total_inserted = sum(results.values())
            print(f"\n✅ Inserted {total_inserted} new news items")
            
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
                "deleted": total_existing,
                "ingested": total_inserted,
                "adapted": adapted_count,
                "success": True
            }
        
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    print("=" * 60)
    print("⚠️  WARNING: This script will delete ALL news items")
    print("=" * 60)
    print()
    
    result = asyncio.run(clean_and_reingest())
    
    if result.get("success"):
        print("\n" + "=" * 60)
        print("✅ Process completed successfully")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Error during process")
        print("=" * 60)
    
    sys.exit(0 if result.get("success") else 1)


