from alvesmusic import AlvesMusic

def get_data(bot: AlvesMusic, guild_id: int) -> dict:
    if not guild_id in bot.data:
        bot.data[guild_id] = {
            "queue": [],
            "player_state": 0,
            "playing": {
                "title": None,
                "url": None,
                "channel": None,
                "channel_url": None,
                "view_count": None,
                "duration": None,
                "thumbnail": None,
                "context": None
            }
        }

    return bot.data[guild_id]
