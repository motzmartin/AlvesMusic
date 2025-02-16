import discord
from discord.ext import commands

from utils import get_media_embed, get_thumbnail_url
from player import play_song
from alvesmusic import AlvesMusic

async def process_yt(bot: AlvesMusic,
                    ctx: commands.Context,
                    info: dict,
                    data: dict,
                    queue: list[dict],
                    message: discord.Message):
    if not info.get("title") or not info.get("webpage_url"):
        raise Exception("Error occurred during extraction.")

    song = {
        "title": info["title"],
        "url": info["webpage_url"],
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
