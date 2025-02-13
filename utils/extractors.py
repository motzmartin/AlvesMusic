from yt_dlp import YoutubeDL

def extract_audio(url: str) -> dict:
    """
    Extract audio information from a given URL without downloading it.
    """

    # Define extraction options for best available audio format
    ydl_options = {
        "format": "bestaudio[ext=opus]/bestaudio/best", # Prioritize Opus format
        "cookiefile": "cookies.txt", # Use cookies to bypass YouTube restrictions
        "quiet": True # Suppress console output
    }

    # Extract metadata without downloading the file
    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(url, download=False)

def extract(query: str) -> dict:
    """
    Extract video information from a search query (or an URL) without downloading it.
    """

    # Define extraction options for search, URL or playlist retrieval
    ydl_options = {
        "extract_flat": "in_playlist", # Avoid downloading videos when fetching playlist details
        "default_search": "auto", # Automatically determine the search platform
        "cookiefile": "cookies.txt", # Use cookies to bypass YouTube restrictions
        "quiet": True # Suppress console output
    }

    # Extract metadata without downloading the file
    with YoutubeDL(ydl_options) as ydl:
        return ydl.extract_info(query, download=False)

def get_thumbnail_url(video_id: str) -> str:
    """
    Generate a YouTube thumbnail URL from a video ID.
    """

    # Ensure the video ID is valid before generating the thumbnail URL
    if video_id:
        return "https://i.ytimg.com/vi/{}/mqdefault.jpg".format(video_id)
    else:
        return None
