import glob
import os
import tempfile
import yt_dlp

from config import DOWNLOAD_DIR
from services.youtube import is_youtube_url

def download_media(url: str, mode: str, quality: str, progress: dict):
    if not is_youtube_url(url):
        raise ValueError("Only YouTube URLs are accepted.")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="tg-ytdlp-", dir=DOWNLOAD_DIR)

    def hook(data):
        if data.get("status") == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            if total:
                progress["percent"] = min(
                    99.0, (data.get("downloaded_bytes", 0) / total) * 100
                )
        elif data.get("status") == "finished":
            progress["percent"] = 99.0
            progress["status"] = "processing"

    if mode == "audio":
        options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(workdir, "%(title).70s-%(id)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 2,
            "progress_hooks": [hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        height = int(quality)
        options = {
            "format": (
                f"best[height<={height}][ext=mp4]/"
                f"best[height<={height}]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best"
            ),
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(workdir, "%(title).70s-%(id)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 2,
            "progress_hooks": [hook],
        }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") or "youtube_media"

        candidates = [
            p for p in glob.glob(os.path.join(workdir, "*"))
            if os.path.isfile(p) and not p.endswith((".part", ".ytdl"))
        ]
        if not candidates:
            raise RuntimeError("Downloader produced no output file.")

        # Prefer the final media file with the largest size.
        file_path = max(candidates, key=os.path.getsize)
        progress["percent"] = 100.0
        progress["status"] = "done"
        return workdir, file_path, title
    except Exception:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
        raise
