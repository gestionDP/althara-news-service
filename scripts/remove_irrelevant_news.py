#!/usr/bin/env python3
"""
Script to remove news items not relevant to the real estate sector.

This script analyzes all news in the database and removes those that are not
relevant to the real estate sector using the same filtering logic as the ingestor.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.ingestion.rss_ingestor import _is_relevant_to_real_estate
from sqlalchemy import select, delete


async def remove_irrelevant_news(dry_run: bool = False):
    """
    Removes all news items that are not relevant to the real estate sector.
    
    Args:
        dry_run: If True, only shows what would be deleted without actually deleting
        
    Returns:
        Dictionary with results
    """
    async with AsyncSessionLocal() as session:
        stmt = select(News)
        result = await session.execute(stmt)
        all_news = result.scalars().all()
        
        print('=' * 80)
        print('🧹 LIMPIEZA DE NOTICIAS NO RELEVANTES PARA EL SECTOR INMOBILIARIO')
        print('=' * 80)
        print()
        print(f'📊 Analizando {len(all_news)} noticias en la base de datos...')
        print()
        
        if dry_run:
            print('⚠️  MODO DRY RUN: No se eliminarán noticias, solo se mostrarán resultados')
            print()
        
        irrelevant_news = []
        relevant_news = []
        
        for news in all_news:
            if not _is_relevant_to_real_estate(news.title, news.raw_summary):
                irrelevant_news.append(news)
            else:
                relevant_news.append(news)
        
        print(f'✅ Noticias relevantes: {len(relevant_news)}')
        print(f'❌ Noticias no relevantes: {len(irrelevant_news)}')
        print()
        
        if not irrelevant_news:
            print('✅ ¡Perfecto! No hay noticias irrelevantes que eliminar.')
            return {
                "success": True,
                "deleted": 0,
                "total_analyzed": len(all_news),
                "relevant": len(relevant_news),
                "irrelevant": 0
            }
        
        # Group by source
        by_source = defaultdict(list)
        by_category = defaultdict(list)
        
        for n in irrelevant_news:
            by_source[n.source].append(n)
            by_category[n.category].append(n)
        
        print('📋 DETALLE DE NOTICIAS A ELIMINAR:')
        print('-' * 80)
        print()
        
        # Show by source
        print('📰 Por fuente:')
        for source in sorted(by_source.keys()):
            news_list = by_source[source]
            print(f'   • {source}: {len(news_list)} noticias')
            for n in news_list[:5]:  # Show first 5
                print(f'     - {n.title[:65]}...')
            if len(news_list) > 5:
                print(f'     ... y {len(news_list) - 5} más')
        print()
        
        # Show by category
        print('📂 Por categoría:')
        for category in sorted(by_category.keys()):
            news_list = by_category[category]
            print(f'   • {category}: {len(news_list)} noticias')
        print()
        
        # Show some examples
        print('📝 Ejemplos de noticias a eliminar:')
        for i, n in enumerate(irrelevant_news[:10], 1):
            print(f'   {i}. [{n.source}] {n.title[:60]}...')
        if len(irrelevant_news) > 10:
            print(f'   ... y {len(irrelevant_news) - 10} más')
        print()
        
        print('=' * 80)
        
        if dry_run:
            print('⚠️  DRY RUN: No se eliminaron noticias')
            print(f'   Se eliminarían {len(irrelevant_news)} noticias si se ejecuta sin --dry-run')
        else:
            print('🗑️  Eliminando noticias...')
            ids_to_delete = [n.id for n in irrelevant_news]
            delete_stmt = delete(News).where(News.id.in_(ids_to_delete))
            await session.execute(delete_stmt)
            await session.commit()
            print(f'✅ Eliminadas {len(irrelevant_news)} noticias no relevantes')
        
        print()
        print('📊 RESUMEN FINAL:')
        print(f'   • Total analizadas: {len(all_news)}')
        print(f'   • Noticias relevantes: {len(relevant_news)}')
        print(f'   • Noticias eliminadas: {len(irrelevant_news)}')
        print()
        
        return {
            "success": True,
            "deleted": len(irrelevant_news) if not dry_run else 0,
            "total_analyzed": len(all_news),
            "relevant": len(relevant_news),
            "irrelevant": len(irrelevant_news),
            "by_source": {source: len(news_list) for source, news_list in by_source.items()},
            "by_category": {category: len(news_list) for category, news_list in by_category.items()}
        }


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        result = asyncio.run(remove_irrelevant_news(dry_run=dry_run))
        sys.exit(0 if result.get("success") else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
