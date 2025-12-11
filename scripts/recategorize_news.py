#!/usr/bin/env python3
"""
Script para recategorizar noticias existentes basándose en palabras clave.

Actualiza las categorías de las noticias ya almacenadas en la base de datos
usando el nuevo sistema de categorización automática.
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
from app.ingestion.rss_ingestor import _categorize_by_keywords
from sqlalchemy import select


async def recategorize_existing_news():
    """Recategoriza todas las noticias existentes basándose en palabras clave"""
    async with AsyncSessionLocal() as session:
        try:
            # Obtener todas las noticias
            print("📊 Obteniendo noticias existentes...")
            stmt = select(News)
            result = await session.execute(stmt)
            all_news = result.scalars().all()
            
            total = len(all_news)
            print(f"✅ Encontradas {total} noticias")
            
            if total == 0:
                print("ℹ️  No hay noticias para recategorizar")
                return {"updated": 0, "total": 0}
            
            # Recategorizar cada noticia
            updated_count = 0
            unchanged_count = 0
            
            print("\n🔄 Recategorizando noticias...")
            for news in all_news:
                # Detectar nueva categoría basándose en palabras clave
                new_category = _categorize_by_keywords(news.title, news.raw_summary)
                
                if new_category and new_category != news.category:
                    old_category = news.category
                    news.category = new_category
                    updated_count += 1
                    print(f"   ✓ {news.title[:60]}...")
                    print(f"     {old_category} → {new_category}")
                else:
                    unchanged_count += 1
            
            # Commit cambios
            if updated_count > 0:
                await session.commit()
                print(f"\n✅ Se actualizaron {updated_count} noticias")
                print(f"ℹ️  {unchanged_count} noticias mantuvieron su categoría")
            else:
                print(f"\nℹ️  No se necesitaron cambios. Todas las noticias ya tienen categorías correctas")
            
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

