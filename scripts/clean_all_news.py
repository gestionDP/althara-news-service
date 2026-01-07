#!/usr/bin/env python3
"""
Script para eliminar todas las noticias de la base de datos.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from sqlalchemy import select, delete, func


async def clean_all_news():
    """Elimina todas las noticias de la base de datos"""
    async with AsyncSessionLocal() as session:
        # Contar noticias antes de eliminar
        count_stmt = select(func.count()).select_from(News)
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar_one()
        
        if total_count == 0:
            print("✅ La base de datos ya está vacía")
            return {"deleted": 0, "success": True}
        
        print("=" * 80)
        print("🗑️  ELIMINANDO TODAS LAS NOTICIAS")
        print("=" * 80)
        print(f"📊 Noticias encontradas: {total_count}")
        print()
        print("⚠️  Esta operación es IRREVERSIBLE")
        print()
        
        # Eliminar todas las noticias
        delete_stmt = delete(News)
        await session.execute(delete_stmt)
        await session.commit()
        
        print(f"✅ Eliminadas {total_count} noticias")
        print()
        print("=" * 80)
        print("✅ Base de datos limpia y lista para nueva ingesta")
        print("=" * 80)
        
        return {
            "deleted": total_count,
            "success": True
        }


if __name__ == "__main__":
    try:
        result = asyncio.run(clean_all_news())
        sys.exit(0 if result.get("success") else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

