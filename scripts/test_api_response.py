#!/usr/bin/env python3
"""
Script para probar que el endpoint devuelve correctamente el campo instagram_post.
Simula exactamente lo que hace el endpoint GET /api/news.
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
from app.schemas.news import NewsRead, PaginatedResponse
from sqlalchemy import select, func


async def test_api_response():
    """Simula la respuesta del endpoint GET /api/news"""
    async with AsyncSessionLocal() as session:
        # Simular exactamente lo que hace el endpoint
        query = select(News)
        count_query = select(func.count()).select_from(News)
        
        query = query.order_by(News.published_at.desc())
        query = query.limit(5)
        
        result = await session.execute(query)
        news_list = result.scalars().all()
        
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()
        
        # Serializar usando el schema (como lo hace FastAPI)
        serialized_items = []
        for news in news_list:
            news_read = NewsRead.model_validate(news)
            serialized_items.append(news_read.model_dump(mode='json'))
        
        response = PaginatedResponse[NewsRead](
            items=serialized_items,
            total=total,
            limit=5,
            offset=0,
            has_more=(0 + 5) < total
        )
        
        # Convertir a JSON (como lo hace FastAPI)
        json_response = response.model_dump(mode='json')
        
        print("=" * 80)
        print("🧪 PRUEBA DE RESPUESTA DEL ENDPOINT")
        print("=" * 80)
        print()
        
        # Verificar cada noticia
        for i, item in enumerate(json_response['items'], 1):
            print(f"📰 NOTICIA {i}:")
            print(f"   Título: {item['title'][:60]}...")
            print(f"   ID: {item['id']}")
            print(f"   ¿Tiene instagram_post?: {'instagram_post' in item}")
            print(f"   Valor de instagram_post: {item.get('instagram_post', 'NO ENCONTRADO')[:100] if item.get('instagram_post') else 'None/undefined'}")
            print()
        
        print("=" * 80)
        print("📋 ESTRUCTURA JSON COMPLETA (primer item):")
        print("=" * 80)
        if json_response['items']:
            first_item = json_response['items'][0]
            print(json.dumps(first_item, indent=2, ensure_ascii=False, default=str))
        
        print()
        print("=" * 80)
        print("✅ VERIFICACIÓN:")
        print("=" * 80)
        all_have_posts = all('instagram_post' in item and item['instagram_post'] for item in json_response['items'])
        print(f"   • Todas las noticias tienen instagram_post: {all_have_posts}")
        print(f"   • Total de noticias: {len(json_response['items'])}")
        print()
        
        if not all_have_posts:
            print("⚠️  ALGUNAS NOTICIAS NO TIENEN POST:")
            for item in json_response['items']:
                if not item.get('instagram_post'):
                    print(f"   - {item['title'][:60]}... (ID: {item['id']})")


if __name__ == "__main__":
    try:
        asyncio.run(test_api_response())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

