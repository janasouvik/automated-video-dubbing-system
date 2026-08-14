import asyncio
from pathlib import Path
from app.pipeline.downloader import download_video

async def test():
    await download_video("https://www.youtube.com/watch?v=jNQXAC9IVRw", Path("./test_dl"))

asyncio.run(test())
