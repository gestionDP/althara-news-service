from fastapi import FastAPI
from app.database import engine, Base
from app.routers import news, admin

app = FastAPI(title="Althara News Service", version="1.0.0")

app.include_router(news.router, prefix="/api")
app.include_router(admin.router)

@app.on_event("startup")
async def startup():
    if engine is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    if engine is not None:
        await engine.dispose()

