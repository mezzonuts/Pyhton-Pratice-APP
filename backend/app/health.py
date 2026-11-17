from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone

from .database import get_async_session, Base

app = FastAPI()

redis_client = Redis(host="redis", port=6379, db=0)


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_async_session)):
    db_ok = False
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        db_ok = True
    except Exception:
        pass

    redis_ok = False
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    timestamp = datetime.now(timezone.utc).isoformat()
    status = "ok" if db_ok and redis_ok else "error"
    return {"status": status, "timestamp": timestamp}