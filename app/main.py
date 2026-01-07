from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import news, admin
from app.middleware import RateLimitMiddleware

app = FastAPI(title="Althara News Service", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

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

