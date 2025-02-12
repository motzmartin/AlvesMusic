from yt_dlp import YoutubeDL

def extract_audio(url: str) -> dict:
    """
    Extract audio information from a given URL without downloading it.
    """
    ydl_options = {
        "format": "bestaudio[ext=opus]/bestaudio/best",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(url, download=False)

def extract(query: str) -> dict:
    """
    Extract video information from a search query (or an URL) without downloading it.
    """
    ydl_options = {
        "extract_flat": "in_playlist",
        "default_search": "auto",
        "cookiefile": "cookies.txt",
        "quiet": True
    }

    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)

def get_thumbnail_url(video_id: str) -> str:
    """
    Generate a YouTube thumbnail URL from a video ID.
    """
    if video_id:
        return "https://i.ytimg.com/vi/{}/mqdefault.jpg".format(video_id)
    else:
        return None
