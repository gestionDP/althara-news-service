#!/usr/bin/env python3
"""
Script para generar contenido estructurado para todas las noticias pendientes.
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


async def generate_structured_for_all():
    """Genera contenido estructurado para todas las noticias que no lo tengan"""
    async with AsyncSessionLocal() as session:
        # Buscar noticias sin contenido estructurado
        stmt = select(News).where(
            News.althara_content.is_(None)
        )
        result = await session.execute(stmt)
        pending_news = result.scalars().all()
        
        if not pending_news:
            print("✅ Todas las noticias ya tienen contenido estructurado")
            return
        
        print(f"📝 Generando contenido estructurado para {len(pending_news)} noticias...")
        print()
        
        adapted_count = 0
        errors = 0
        
        for i, news in enumerate(pending_news, 1):
            try:
                print(f"[{i}/{len(pending_news)}] Procesando: {news.title[:60]}...")
                
                # Generar contenido estructurado
                althara_summary, instagram_post, structured_content = build_all_content_structured(
                    title=news.title,
                    raw_summary=news.raw_summary,
                    category=news.category,
                    source=news.source,
                    url=news.url,
                    published_at=news.published_at
                )
                
                # Guardar todo
                if not news.althara_summary:
                    news.althara_summary = althara_summary
                if not news.instagram_post:
                    news.instagram_post = instagram_post
                news.althara_content = structured_content
                
                adapted_count += 1
                print(f"  ✅ Generado: {structured_content['web']['title'][:50]}...")
                
            except Exception as e:
                errors += 1
                print(f"  ❌ Error: {e}")
                continue
        
        # Guardar cambios
        if adapted_count > 0:
            await session.commit()
            print()
            print("=" * 80)
            print(f"✅ Completado: {adapted_count} noticias adaptadas")
            if errors > 0:
                print(f"⚠️  Errores: {errors}")
            print("=" * 80)
        else:
            print("⚠️  No se generó contenido para ninguna noticia")


if __name__ == "__main__":
    asyncio.run(generate_structured_for_all())

