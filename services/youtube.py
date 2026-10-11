from urllib.parse import urlparse
import yt_dlp

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtu.be"
}

def is_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        return parsed.scheme in {"http", "https"} and host in ALLOWED_HOSTS
    except Exception:
        return False

import os

def _base_options() -> dict:
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 2,
        "extractor_retries": 2,
        "extractor_args": {"youtube": {"player_client": ["web"]}}
    }
    if os.path.exists("cookies.txt"):
        options["cookiefile"] = "cookies.txt"
    return options

def get_video_info(url: str) -> dict:
    if not is_youtube_url(url):
        raise ValueError("Only YouTube URLs are accepted.")
    options = _base_options()
    options["skip_download"] = True
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info or info.get("_type") == "playlist":
        raise ValueError("A single video URL is required.")
    return info
