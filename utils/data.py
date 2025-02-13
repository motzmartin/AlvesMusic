from alvesmusic import AlvesMusic

def get_data(bot: AlvesMusic, guild_id: int) -> dict:
    """
    Retrieves or initializes the guild's music data.
    """

    # Check if the guild's data exists; if not, initialize it
    if not guild_id in bot.data:
        bot.data[guild_id] = {
            "queue": [], # List to store the music queue
            "player_state": 0, # 0 = idle, 1 = playing, 2 = loading
            "playing": { # Information about the currently playing song
                "title": None,
                "url": None,
                "channel": None,
                "channel_url": None,
                "view_count": None,
                "duration": None,
                "thumbnail": None,
                "context": None # Stores the command context (who requested it, etc.)
            }
        }

    # Return the guild's music data
    return bot.data[guild_id]
