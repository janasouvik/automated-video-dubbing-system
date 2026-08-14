import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, status, current_stage_message, error_message FROM jobs ORDER BY created_at DESC LIMIT 1;"))
        row = result.first()
        if row:
            print("ID:", row[0])
            print("Status:", row[1])
            print("Message:", row[2])
            print("Error:", row[3])
        else:
            print("No jobs found")

asyncio.run(main())
