import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, status, current_stage_message, error_message, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"))
        for row in result:
            print("ID:", row[0], "Status:", row[1], "Error:", row[3], "Time:", row[4])

asyncio.run(main())
