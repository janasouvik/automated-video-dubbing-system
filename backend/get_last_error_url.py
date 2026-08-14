import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT youtube_url FROM jobs ORDER BY created_at DESC LIMIT 1;"))
        row = result.first()
        if row:
            print("URL:", row[0])

asyncio.run(main())
