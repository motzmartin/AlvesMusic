from yt_dlp import YoutubeDL

def extract_audio(url: str):
    ydl_options = {
        "format": "bestaudio[ext=opus]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(url, download=False)

def extract_query(query: str):
    ydl_options = {
        "extract_flat": "in_playlist",
        "playlist_items": "1",
        "default_search": "auto",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)

def extract_remaining(playlist_url: str):
    ydl_options = {
        "extract_flat": True,
        "playlist_items": "2-",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(playlist_url, download=False)

def get_thumbnail_url(video_id: str):
    return "https://i.ytimg.com/vi/{}/mqdefault.jpg".format(video_id) if video_id else ""
