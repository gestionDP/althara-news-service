#!/usr/bin/env python3
"""
Script para regenerar contenido estructurado para TODAS las noticias (forzar actualización).
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.adapters.news_adapter import build_all_content_structured
from sqlalchemy import select


async def regenerate_all_structured():
    """Regenera contenido estructurado para todas las noticias"""
    async with AsyncSessionLocal() as session:
        # Obtener todas las noticias
        stmt = select(News)
        result = await session.execute(stmt)
        all_news = result.scalars().all()
        
        if not all_news:
            print("❌ No hay noticias en la base de datos")
            return
        
        print(f"🔄 Regenerando contenido estructurado para {len(all_news)} noticias...")
        print()
        
        regenerated_count = 0
        errors = 0
        
        for i, news in enumerate(all_news, 1):
            try:
                print(f"[{i}/{len(all_news)}] Regenerando: {news.title[:60]}...")
                
                # Regenerar contenido estructurado
                althara_summary, instagram_post, structured_content = build_all_content_structured(
                    title=news.title,
                    raw_summary=news.raw_summary,
                    category=news.category,
                    source=news.source,
                    url=news.url,
                    published_at=news.published_at
                )
                
                # Actualizar todo
                news.althara_summary = althara_summary
                news.instagram_post = instagram_post
                news.althara_content = structured_content
                
                regenerated_count += 1
                print(f"  ✅ Regenerado: {structured_content['web']['title'][:50]}...")
                
            except Exception as e:
                errors += 1
                print(f"  ❌ Error: {e}")
                continue
        
        # Guardar cambios
        if regenerated_count > 0:
            await session.commit()
            print()
            print("=" * 80)
            print(f"✅ Completado: {regenerated_count} noticias regeneradas")
            if errors > 0:
                print(f"⚠️  Errores: {errors}")
            print("=" * 80)
        else:
            print("⚠️  No se regeneró contenido para ninguna noticia")


if __name__ == "__main__":
    asyncio.run(regenerate_all_structured())

