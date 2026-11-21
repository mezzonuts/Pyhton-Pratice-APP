from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_engine, Base, get_async_session
from app.health import health_check
from app.routes.auth import router as auth_router
from app.api.missions.routes import router as missions_router
from app.ai.routes import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Database init warning: {e}")
    yield


app = FastAPI(title="PyForge API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(missions_router, prefix="/api")
app.include_router(ai_router)


@app.get("/health")
@app.get("/api/health")
async def health(session: AsyncSession = Depends(get_async_session)):
    return await health_check(session)
