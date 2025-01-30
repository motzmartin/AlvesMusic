import time
from yt_dlp import YoutubeDL

def duration_str(duration: int):
    if duration < 3600:
        return time.strftime("%M:%S", time.gmtime(duration))

    elif duration < 3600 * 24:
        return time.strftime("%H:%M:%S", time.gmtime(duration))

    return time.strftime("%d:%H:%M:%S", time.gmtime(duration))

def extract_audio(url: str):
    ydl_options = {
        "format": "bestaudio[ext=opus]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(url, download=False)

def extract(query: str):
    ydl_options = {
        "extract_flat": "in_playlist",
        "default_search": "auto",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)
