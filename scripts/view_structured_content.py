#!/usr/bin/env python3
"""
Script para ver el contenido estructurado de una noticia específica.
Uso: python3 scripts/view_structured_content.py [id o número]
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
from sqlalchemy import select


async def view_structured_content(news_id_or_number=None):
    """Muestra el contenido estructurado de una noticia"""
    async with AsyncSessionLocal() as session:
        if news_id_or_number:
            # Si es un número, buscar por índice
            if news_id_or_number.isdigit():
                stmt = select(News).offset(int(news_id_or_number) - 1).limit(1)
            else:
                # Si es un UUID, buscar por ID
                from uuid import UUID
                try:
                    uuid_obj = UUID(news_id_or_number)
                    stmt = select(News).where(News.id == uuid_obj)
                except ValueError:
                    print(f"❌ ID inválido: {news_id_or_number}")
                    return
        else:
            # Mostrar la primera noticia con contenido estructurado
            stmt = select(News).where(
                News.althara_content.isnot(None)
            ).limit(1)
        
        result = await session.execute(stmt)
        news = result.scalar_one_or_none()
        
        if not news:
            print("❌ No se encontró la noticia")
            return
        
        if not news.althara_content:
            print(f"⚠️  La noticia '{news.title[:60]}...' no tiene contenido estructurado")
            print("   Ejecuta: python3 scripts/generate_structured_for_all.py")
            return
        
        print("=" * 80)
        print(f"📰 NOTICIA: {news.title}")
        print("=" * 80)
        print(f"ID: {news.id}")
        print(f"Categoría: {news.category}")
        print(f"Fuente: {news.source}")
        print(f"URL: {news.url}")
        print()
        
        content = news.althara_content
        
        print("📄 CONTENIDO WEB:")
        print("-" * 80)
        print(f"Título: {content['web']['title']}")
        print()
        print(f"Deck: {content['web']['deck']}")
        print()
        print(f"Hecho:")
        print(f"  {content['web']['hecho']}")
        print()
        print(f"Lectura Althara:")
        print(f"  {content['web']['lectura']}")
        print()
        print("Implicaciones:")
        for i, impl in enumerate(content['web']['implicaciones'], 1):
            print(f"  {i}. {impl}")
        print()
        print("Señales a Vigilar:")
        for i, senal in enumerate(content['web']['senales_a_vigilar'], 1):
            print(f"  {i}. {senal}")
        print()
        print(f"Disclaimer:")
        print(f"  {content['web']['disclaimer']}")
        print()
        
        print("📱 CONTENIDO INSTAGRAM:")
        print("-" * 80)
        print(f"Hook: {content['instagram']['hook']}")
        print()
        print("Carrusel Slides:")
        for i, slide in enumerate(content['instagram']['carousel_slides'], 1):
            print(f"  Slide {i}: {slide}")
        print()
        print("Caption:")
        print(f"  {content['instagram']['caption']}")
        print()
        print(f"CTA: {content['instagram']['cta']}")
        print()
        
        print("🔍 QA:")
        print("-" * 80)
        print("Facts usados:")
        for fact in content['qa']['facts_used']:
            print(f"  - {fact}")
        if content['qa']['unknown_or_missing']:
            print()
            print("Datos faltantes/no verificados:")
            for missing in content['qa']['unknown_or_missing']:
                print(f"  - {missing}")
        print()
        
        print("📊 METADATA:")
        print("-" * 80)
        print(f"Versión: {content.get('version', 'N/A')}")
        if 'metadata' in content:
            print(f"Categoría: {content['metadata'].get('category', 'N/A')}")
            print(f"Generado: {content['metadata'].get('generated_at', 'N/A')}")
            print(f"Seed: {content['metadata'].get('seed', 'N/A')}")
        print()
        
        # Opción para ver JSON completo
        print("💾 ¿Ver JSON completo? (s/n): ", end="")
        try:
            response = input().strip().lower()
            if response == 's':
                print()
                print("=" * 80)
                print("JSON COMPLETO:")
                print("=" * 80)
                print(json.dumps(content, indent=2, ensure_ascii=False))
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    news_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(view_structured_content(news_id))

