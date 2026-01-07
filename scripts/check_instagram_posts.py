#!/usr/bin/env python3
"""
Script para verificar qué noticias tienen posts de Instagram generados.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from sqlalchemy import select, func


async def check_instagram_posts():
    """Verifica el estado de los posts de Instagram en las noticias"""
    async with AsyncSessionLocal() as session:
        # Contar total de noticias
        count_stmt = select(func.count()).select_from(News)
        count_result = await session.execute(count_stmt)
        total_news = count_result.scalar_one()
        
        # Contar noticias con posts
        with_post_stmt = select(func.count()).select_from(News).where(News.instagram_post.isnot(None))
        with_post_result = await session.execute(with_post_stmt)
        with_posts = with_post_result.scalar_one()
        
        # Contar noticias sin posts
        without_posts = total_news - with_posts
        
        print("=" * 80)
        print("📊 ESTADO DE POSTS DE INSTAGRAM")
        print("=" * 80)
        print()
        print(f"📰 Total de noticias: {total_news}")
        print(f"✅ Con post de Instagram: {with_posts}")
        print(f"❌ Sin post de Instagram: {without_posts}")
        print()
        
        if total_news == 0:
            print("⚠️  No hay noticias en la base de datos")
            return
        
        # Mostrar noticias sin posts
        if without_posts > 0:
            print("=" * 80)
            print(f"❌ NOTICIAS SIN POST DE INSTAGRAM ({without_posts}):")
            print("=" * 80)
            print()
            
            stmt = select(News).where(News.instagram_post.is_(None))
            result = await session.execute(stmt)
            news_without_posts = result.scalars().all()
            
            for i, news in enumerate(news_without_posts, 1):
                print(f"{i}. [{news.source}] {news.title[:70]}...")
                print(f"   ID: {news.id}")
                print(f"   Categoría: {news.category}")
                print()
        
        # Mostrar noticias con posts
        if with_posts > 0:
            print("=" * 80)
            print(f"✅ NOTICIAS CON POST DE INSTAGRAM ({with_posts}):")
            print("=" * 80)
            print()
            
            stmt = select(News).where(News.instagram_post.isnot(None)).limit(5)
            result = await session.execute(stmt)
            news_with_posts = result.scalars().all()
            
            for i, news in enumerate(news_with_posts, 1):
                print(f"{i}. [{news.source}] {news.title[:70]}...")
                print(f"   ID: {news.id}")
                print(f"   Longitud del post: {len(news.instagram_post)} caracteres")
                print()
                print("   📱 POST:")
                print("   " + "-" * 76)
                # Mostrar primeras líneas del post
                post_lines = news.instagram_post.split('\n')[:8]
                for line in post_lines:
                    print(f"   {line}")
                if len(news.instagram_post.split('\n')) > 8:
                    print("   ...")
                print("   " + "-" * 76)
                print()
        
        # Resumen
        print("=" * 80)
        print("📋 RESUMEN")
        print("=" * 80)
        print(f"   • Total: {total_news} noticias")
        print(f"   • Con post: {with_posts} ({with_posts/total_news*100:.1f}%)" if total_news > 0 else "   • Con post: 0")
        print(f"   • Sin post: {without_posts} ({without_posts/total_news*100:.1f}%)" if total_news > 0 else "   • Sin post: 0")
        print()
        
        if without_posts > 0:
            print("💡 Para generar posts para las noticias pendientes:")
            print("   POST /api/admin/adapt-pending")
            print("   O ejecuta: python scripts/test_instagram_posts.py")


if __name__ == "__main__":
    try:
        asyncio.run(check_instagram_posts())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

