#!/usr/bin/env python3
"""
Script para limpiar todas las noticias y reingestar desde cero.

⚠️ ADVERTENCIA: Este script elimina TODAS las noticias de la base de datos.
"""
import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.adapters.news_adapter import build_althara_summary
from sqlalchemy import select, delete


async def clean_and_reingest():
    """Limpia todas las noticias y reingesta desde cero"""
    async with AsyncSessionLocal() as session:
        try:
            # 1. Contar noticias existentes
            print("📊 Verificando noticias existentes...")
            stmt = select(News)
            result = await session.execute(stmt)
            existing_news = result.scalars().all()
            total_existing = len(existing_news)
            
            if total_existing > 0:
                print(f"⚠️  Se encontraron {total_existing} noticias en la base de datos")
                print("🗑️  Eliminando todas las noticias...")
                
                # Eliminar todas las noticias
                delete_stmt = delete(News)
                await session.execute(delete_stmt)
                await session.commit()
                
                print(f"✅ Se eliminaron {total_existing} noticias")
            else:
                print("ℹ️  No hay noticias para eliminar")
            
            # 2. Reingestar noticias desde todas las fuentes RSS
            print("\n📥 Ingestando noticias desde RSS con nuevo sistema de categorización...")
            results = await ingest_rss_sources(session)
            
            total_inserted = sum(results.values())
            print(f"\n✅ Se insertaron {total_inserted} noticias nuevas")
            
            for source, count in results.items():
                if count > 0:
                    print(f"   - {source}: {count} noticias")
            
            # 3. Adaptar noticias al tono Althara
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
    print("⚠️  ADVERTENCIA: Este script eliminará TODAS las noticias")
    print("=" * 60)
    print()
    
    result = asyncio.run(clean_and_reingest())
    
    if result.get("success"):
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Error durante el proceso")
        print("=" * 60)
    
    sys.exit(0 if result.get("success") else 1)
