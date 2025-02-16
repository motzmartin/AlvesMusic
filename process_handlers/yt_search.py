import discord
from discord.ext import commands

from utils import get_thumbnail_url, get_media_embed
from player import play_song
from alvesmusic import AlvesMusic

async def process_yt_search(bot: AlvesMusic,
                    ctx: commands.Context,
                    info: dict,
                    data: dict,
                    queue: list[dict],
                    message: discord.Message):
    first: dict = info["entries"][0]

    if not first.get("title") or not first.get("url"):
        raise Exception("Error occurred during extraction.")

    song = {
        "title": first["title"],
        "url": first["url"],
        "duration": first.get("duration"),
        "context": ctx
    }

    if data["player_state"] != 0:
        queue.append(song.copy())

        song["position"] = len(queue)
        song["channel"] = first.get("channel")
        song["channel_url"] = first.get("channel_url")
        song["view_count"] = first.get("view_count")
        song["thumbnail"] = get_thumbnail_url(first.get("id"))

        embed = get_media_embed(song, 0)

        await message.edit(embed=embed)
    else:
        await play_song(bot, song, message)
