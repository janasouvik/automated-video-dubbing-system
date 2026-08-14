import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT id, status, current_stage_message, error_message, youtube_url, created_at 
            FROM jobs ORDER BY created_at DESC LIMIT 5
        """))
        print("=== LAST 5 JOBS ===")
        for row in result:
            print(f"\nID: {row[0]}")
            print(f"  Status:  {row[1]}")
            print(f"  Stage:   {row[2]}")
            print(f"  Error:   {row[3]}")
            print(f"  URL:     {row[4]}")
            print(f"  Time:    {row[5]}")

asyncio.run(main())
