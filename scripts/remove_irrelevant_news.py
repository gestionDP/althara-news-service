#!/usr/bin/env python3
"""
Script to remove news items not relevant to the real estate sector.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import _is_relevant_to_real_estate
from sqlalchemy import select, delete


async def remove_irrelevant_news():
    """Removes all news items that are not relevant to the real estate sector"""
    async with AsyncSessionLocal() as session:
        stmt = select(News)
        result = await session.execute(stmt)
        all_news = result.scalars().all()
        
        print(f'📊 Analyzing {len(all_news)} news items...')
        print()
        
        irrelevant_news = []
        for news in all_news:
            if not _is_relevant_to_real_estate(news.title, news.raw_summary):
                irrelevant_news.append(news)
        
        if not irrelevant_news:
            print('✅ No irrelevant news items to remove')
            return {"success": True, "deleted": 0}
        
        print(f'❌ Found {len(irrelevant_news)} irrelevant news items')
        print()
        print('📋 News items to be deleted:')
        print('-' * 80)
        
        by_source = {}
        for n in irrelevant_news:
            if n.source not in by_source:
                by_source[n.source] = []
            by_source[n.source].append(n)
        
        for source, news_list in sorted(by_source.items()):
            print(f'\n📰 {source} ({len(news_list)} news items):')
            for n in news_list:
                print(f'   - {n.title[:70]}...')
        
        print()
        print('=' * 80)
        print('🗑️  Deleting news items...')
        
        ids_to_delete = [n.id for n in irrelevant_news]
        delete_stmt = delete(News).where(News.id.in_(ids_to_delete))
        result = await session.execute(delete_stmt)
        await session.commit()
        
        print(f'✅ Deleted {len(irrelevant_news)} irrelevant news items')
        print()
        print('📊 Summary by source:')
        for source, news_list in sorted(by_source.items()):
            print(f'   - {source}: {len(news_list)} deleted')
        
        return {
            "success": True,
            "deleted": len(irrelevant_news),
            "by_source": {source: len(news_list) for source, news_list in by_source.items()}
        }


if __name__ == "__main__":
    result = asyncio.run(remove_irrelevant_news())
    sys.exit(0 if result.get("success") else 1)
