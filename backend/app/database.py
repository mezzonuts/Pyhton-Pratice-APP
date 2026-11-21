import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


default_db = (
    "sqlite+aiosqlite:////tmp/test.db"
    if os.getenv("VERCEL")
    else "sqlite+aiosqlite:///./test.db"
)
DATABASE_URL = os.getenv("DATABASE_URL", default_db)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)
engine = async_engine

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
