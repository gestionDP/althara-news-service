#!/usr/bin/env python3
"""
Script para ejecutar la ingestión de noticias desde la línea de comandos.

Útil para cron jobs o ejecución programada.
"""
import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.adapters.news_adapter import build_althara_summary
from app.models.news import News
from sqlalchemy import select


async def ingest_and_adapt():
    """Ejecuta ingestión y adaptación en una sola función"""
    async with AsyncSessionLocal() as session:
        try:
            # 1. Ingestar noticias
            print("📥 Ingestando noticias desde RSS...")
            results = await ingest_rss_sources(session)
            
            total_inserted = sum(results.values())
            print(f"✅ Se insertaron {total_inserted} noticias nuevas")
            
            for source, count in results.items():
                if count > 0:
                    print(f"   - {source}: {count} noticias")
            
            # 2. Adaptar noticias pendientes
            print("\n🎨 Adaptando noticias al tono Althara...")
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
                    print(f"   ⚠️  Error adaptando noticia {news.id}: {e}")
                    continue
            
            if adapted_count > 0:
                await session.commit()
            
            print(f"✅ Se adaptaron {adapted_count} noticias al tono Althara")
            
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

