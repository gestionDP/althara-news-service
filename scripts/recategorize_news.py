#!/usr/bin/env python3
"""
Script to recategorize existing news based on keywords.

Updates categories of news items already stored in the database
using the new automatic categorization system.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import _categorize_by_keywords
from sqlalchemy import select


async def recategorize_existing_news():
    """Recategorizes all existing news based on keywords"""
    async with AsyncSessionLocal() as session:
        try:
            print("📊 Getting existing news...")
            stmt = select(News)
            result = await session.execute(stmt)
            all_news = result.scalars().all()
            
            total = len(all_news)
            print(f"✅ Found {total} news items")
            
            if total == 0:
                print("ℹ️  No news items to recategorize")
                return {"updated": 0, "total": 0}
            
            updated_count = 0
            unchanged_count = 0
            
            print("\n🔄 Recategorizing news...")
            for news in all_news:
                new_category = _categorize_by_keywords(news.title, news.raw_summary)
                
                if new_category and new_category != news.category:
                    old_category = news.category
                    news.category = new_category
                    updated_count += 1
                    print(f"   ✓ {news.title[:60]}...")
                    print(f"     {old_category} → {new_category}")
                else:
                    unchanged_count += 1
            
            if updated_count > 0:
                await session.commit()
                print(f"\n✅ Updated {updated_count} news items")
                print(f"ℹ️  {unchanged_count} news items kept their category")
            else:
                print(f"\nℹ️  No changes needed. All news items already have correct categories")
            
            return {
                "updated": updated_count,
                "unchanged": unchanged_count,
                "total": total,
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
    result = asyncio.run(recategorize_existing_news())
    sys.exit(0 if result.get("success") else 1)


