from yt_dlp import YoutubeDL

def extract_audio(url: str):
    with YoutubeDL({
        "format": "bestaudio[ext=opus]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "quiet": True
    }) as ydl:
        return ydl.extract_info(url, download=False)

def extract(query: str):
    with YoutubeDL({
        "extract_flat": "in_playlist",
        "default_search": "auto",
        "cookiefile": "cookies.txt",
        "quiet": True
    }) as ydl:
        return ydl.extract_info(query, download=False)
