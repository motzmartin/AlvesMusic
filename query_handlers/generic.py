import discord
from discord.ext import commands

from utils import get_thumbnail_url, get_media_embed
from player import play_song
from alvesmusic import AlvesMusic

async def process_generic(bot: AlvesMusic,
                    ctx: commands.Context,
                    message: discord.Message,
                    data: dict,
                    queue: list[dict],
                    info: dict,
                    is_search: bool = False):
    if is_search:
        info = info["entries"][0]
        url = "url"
    else:
        url = "webpage_url"

    if not info.get("title") or not info.get(url):
        raise Exception("Error occurred during extraction. (2)")

    song = {
        "title": info["title"],
        "url": info[url],
        "duration": info.get("duration"),
        "context": ctx
    }

    if data["player_state"] != 0:
        queue.append(song.copy())

        song["position"] = len(queue)
        song["channel"] = info.get("channel")
        song["channel_url"] = info.get("channel_url")
        song["view_count"] = info.get("view_count")
        song["thumbnail"] = get_thumbnail_url(info.get("id"))

        embed = get_media_embed(song, 0)

        await message.edit(embed=embed)
    else:
        await play_song(bot, song, message)
