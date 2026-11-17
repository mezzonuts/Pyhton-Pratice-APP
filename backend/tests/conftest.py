import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from backend.app.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db_async"


@pytest.fixture(scope="session")
def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    asyncio.get_event_loop().run_until_complete(engine.dispose())


@pytest.fixture(scope="session")
async def async_session_factory(async_engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker, None]:
    factory = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    yield factory
    await factory.close()


@pytest.fixture(scope="function")
async def db_session(async_session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session