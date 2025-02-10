from yt_dlp import YoutubeDL

def extract_audio(url: str) -> dict:
    ydl_options = {
        "format": "bestaudio[ext=opus]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(url, download=False)

def extract(query: str) -> dict:
    ydl_options = {
        "extract_flat": "in_playlist",
        "default_search": "auto",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)

def get_thumbnail_url(id: str) -> str | None:
    if id:
        return "https://i.ytimg.com/vi/{}/mqdefault.jpg".format(id)
    else:
        return None
