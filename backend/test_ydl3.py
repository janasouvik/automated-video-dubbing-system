import asyncio
from pathlib import Path
from app.pipeline.downloader import download_video

async def test():
    job_dir = Path("./test_job")
    job_dir.mkdir(exist_ok=True)
    try:
        await download_video("https://www.youtube.com/watch?v=EBauExtt7YU", job_dir)
        print("SUCCESS")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
