#!/usr/bin/env python3
"""
Script to debug news ingestion and see why no news is being inserted.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import ingest_rss_sources, _is_relevant_to_real_estate, RSS_SOURCES
from sqlalchemy import select, func
import feedparser
import httpx


async def debug_ingestion():
    """Debug ingestion to see what's happening"""
    async with AsyncSessionLocal() as session:
        # Count existing news
        stmt = select(func.count(News.id))
        result = await session.execute(stmt)
        existing_count = result.scalar_one()
        print(f"📊 Current news in database: {existing_count}")
        
        print("\n" + "="*80)
        print("🔍 DEBUGGING RSS INGESTION")
        print("="*80)
        
        # Test each RSS source
        for source_config in RSS_SOURCES[:3]:  # Test first 3 sources
            source_name = source_config["name"]
            feed_url = source_config["url"]
            
            print(f"\n📰 Testing source: {source_name}")
            print(f"   URL: {feed_url}")
            
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    response = await client.get(
                        feed_url,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                    )
                    response.raise_for_status()
                    feed = feedparser.parse(response.text)
                
                if not hasattr(feed, 'entries') or not feed.entries:
                    print(f"   ⚠️  No entries found in feed")
                    continue
                
                total_entries = len(feed.entries)
                print(f"   📥 Found {total_entries} entries in feed")
                
                relevant_count = 0
                rejected_count = 0
                rejected_titles = []
                
                for i, entry in enumerate(feed.entries[:10]):  # Check first 10
                    title = getattr(entry, 'title', 'Sin título')
                    link = getattr(entry, 'link', '')
                    
                    if not title or not link:
                        continue
                    
                    # Check if already exists
                    stmt = select(News).where(News.url == link)
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    if existing:
                        print(f"   ⏭️  [{i+1}] ALREADY EXISTS: {title[:60]}...")
                        continue
                    
                    temp_summary = None
                    if hasattr(entry, 'summary') and entry.summary:
                        temp_summary = entry.summary
                    elif hasattr(entry, 'description') and entry.description:
                        temp_summary = entry.description
                    
                    # Check relevance with temp_summary
                    is_relevant_temp = _is_relevant_to_real_estate(title, temp_summary if temp_summary and len(temp_summary) > 100 else None)
                    
                    if is_relevant_temp:
                        relevant_count += 1
                        print(f"   ✅ [{i+1}] RELEVANT (first filter): {title[:60]}...")
                    else:
                        rejected_count += 1
                        rejected_titles.append(title)
                        print(f"   ❌ [{i+1}] REJECTED (first filter): {title[:60]}...")
                        if temp_summary:
                            print(f"        Summary length: {len(temp_summary)} chars")
                
                print(f"\n   📊 Summary for {source_name}:")
                print(f"      - Total entries checked: {min(10, total_entries)}")
                print(f"      - Relevant: {relevant_count}")
                print(f"      - Rejected: {rejected_count}")
                
                if rejected_count > 0 and relevant_count == 0:
                    print(f"\n   ⚠️  All entries were rejected! Sample rejected titles:")
                    for title in rejected_titles[:3]:
                        print(f"      • {title}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "="*80)
        print("🧪 Testing actual ingestion...")
        print("="*80)
        
        results = await ingest_rss_sources(session, max_items_per_source=5)
        
        total_inserted = sum(results.values())
        print(f"\n✅ Ingestion completed:")
        print(f"   Total inserted: {total_inserted}")
        
        for source, count in results.items():
            if count > 0:
                print(f"   - {source}: {count} news items")
            else:
                print(f"   - {source}: 0 news items (all rejected or already exist)")
        
        # Count news after ingestion
        stmt = select(func.count(News.id))
        result = await session.execute(stmt)
        final_count = result.scalar_one()
        print(f"\n📊 News in database after ingestion: {final_count}")
        print(f"   New news added: {final_count - existing_count}")


if __name__ == "__main__":
    asyncio.run(debug_ingestion())

