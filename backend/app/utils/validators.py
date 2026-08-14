"""YouTube URL and other input validators."""
from __future__ import annotations

import re

_YOUTUBE_RE = re.compile(
    r"^(https?://)?(www\.|m\.)?"
    r"(youtube\.com/(watch\?.*v=[\w-]+|shorts/[\w-]+|embed/[\w-]+)|youtu\.be/[\w-]+)",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """Return True if the URL looks like a valid YouTube video URL."""
    return bool(_YOUTUBE_RE.match(url.strip()))
