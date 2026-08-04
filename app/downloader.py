import os
import tempfile

import yt_dlp

# Covers Instagram Reels/TikTok/YouTube Shorts and most other short-form links.
MAX_DOWNLOAD_SECONDS = int(os.getenv("MAX_DOWNLOAD_SECONDS", "1800"))
MAX_DOWNLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "500")) * 1024 * 1024


def download_from_url(url: str) -> tuple[str, str]:
    """Download the media at a social/video link. Returns (file_path, tmp_dir) — caller removes tmp_dir."""
    tmp_dir = tempfile.mkdtemp(prefix="stt_dl_")
    ydl_opts = {
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_DOWNLOAD_BYTES,
        "retries": 2,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = info.get("duration")
        if duration and duration > MAX_DOWNLOAD_SECONDS:
            raise ValueError(f"Video is {int(duration)}s long; limit is {MAX_DOWNLOAD_SECONDS}s")
        ydl.download([url])
        file_path = ydl.prepare_filename(info)
    return file_path, tmp_dir
