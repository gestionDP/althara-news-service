from fastapi import FastAPI
from app.database import engine, Base
from app.routers import news

app = FastAPI(title="Althara News Service", version="1.0.0")

# Incluir routers
app.include_router(news.router, prefix="/api", tags=["news"])

@app.on_event("startup")
async def startup():
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

