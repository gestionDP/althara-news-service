#!/usr/bin/env python3
"""
Script para verificar el estado del contenido estructurado en las noticias.
"""
import asyncio
import sys
import json
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from sqlalchemy import select, func


async def check_structured_content():
    """Verifica cuántas noticias tienen contenido estructurado"""
    async with AsyncSessionLocal() as session:
        # Contar total de noticias
        total_stmt = select(func.count()).select_from(News)
        total_result = await session.execute(total_stmt)
        total = total_result.scalar_one()
        
        # Contar noticias con contenido estructurado
        structured_stmt = select(func.count()).select_from(News).where(
            News.althara_content.isnot(None)
        )
        structured_result = await session.execute(structured_stmt)
        structured_count = structured_result.scalar_one()
        
        # Contar noticias sin contenido estructurado
        without_structured = total - structured_count
        
        print("=" * 80)
        print("📊 ESTADO DEL CONTENIDO ESTRUCTURADO")
        print("=" * 80)
        print(f"Total de noticias: {total}")
        print(f"✅ Con contenido estructurado: {structured_count}")
        print(f"❌ Sin contenido estructurado: {without_structured}")
        print()
        
        if structured_count > 0:
            # Mostrar ejemplo de noticia con contenido estructurado
            print("📰 EJEMPLO DE NOTICIA CON CONTENIDO ESTRUCTURADO:")
            print("-" * 80)
            
            example_stmt = select(News).where(
                News.althara_content.isnot(None)
            ).limit(1)
            example_result = await session.execute(example_stmt)
            example_news = example_result.scalar_one_or_none()
            
            if example_news:
                print(f"Título: {example_news.title[:60]}...")
                print(f"Categoría: {example_news.category}")
                print(f"Fuente: {example_news.source}")
                print()
                print("Estructura web:")
                if example_news.althara_content and 'web' in example_news.althara_content:
                    web = example_news.althara_content['web']
                    print(f"  - Título: {web.get('title', 'N/A')[:60]}...")
                    print(f"  - Deck: {web.get('deck', 'N/A')[:60]}...")
                    print(f"  - Hecho: {web.get('hecho', 'N/A')[:60]}...")
                    print(f"  - Implicaciones: {len(web.get('implicaciones', []))} items")
                    print(f"  - Señales: {len(web.get('senales_a_vigilar', []))} items")
                print()
                print("Estructura Instagram:")
                if example_news.althara_content and 'instagram' in example_news.althara_content:
                    instagram = example_news.althara_content['instagram']
                    print(f"  - Hook: {instagram.get('hook', 'N/A')[:60]}...")
                    print(f"  - Slides: {len(instagram.get('carousel_slides', []))} slides")
                    print(f"  - Caption: {len(instagram.get('caption', ''))} caracteres")
                    print(f"  - CTA: {instagram.get('cta', 'N/A')}")
                print()
        
        if without_structured > 0:
            print("⚠️  NOTICIAS SIN CONTENIDO ESTRUCTURADO:")
            print("-" * 80)
            
            without_stmt = select(News).where(
                News.althara_content.is_(None)
            ).limit(5)
            without_result = await session.execute(without_stmt)
            without_news = without_result.scalars().all()
            
            for i, news in enumerate(without_news, 1):
                print(f"{i}. {news.title[:70]}...")
                print(f"   Categoría: {news.category} | Fuente: {news.source}")
                print()
            
            if without_structured > 5:
                print(f"... y {without_structured - 5} más")
            print()
            print("💡 Para generar contenido estructurado, ejecuta:")
            print("   POST /api/admin/adapt-pending")
            print("   o")
            print("   python3 scripts/ingest_news.py")
        
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_structured_content())

