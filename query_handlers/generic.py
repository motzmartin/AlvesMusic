import discord
from discord.ext import commands

from utils import get_thumbnail_url, get_media_embed
from player import play_song
from alvesmusic import AlvesMusic

async def process_generic(bot: AlvesMusic, ctx: commands.Context, message: discord.Message, info: dict, is_search: bool = False):
    data = bot.get_data(ctx.guild.id)

    url = "url" if is_search else "webpage_url"

    if not info.get("title") or not info.get(url):
        raise Exception("Cannot retrieve title or URL. (1)")

    song = {
        "title": info["title"],
        "url": info[url],
        "duration": info.get("duration"),
        "context": ctx
    }

    if not data.is_ready():
        data.queue.append(song.copy())

        song["channel"] = info.get("channel")
        song["channel_url"] = info.get("channel_url")
        song["view_count"] = info.get("view_count")
        song["thumbnail"] = get_thumbnail_url(info.get("id"))
        song["position"] = len(data.queue)

        embed = get_media_embed(song, 0)

        await message.edit(embed=embed)
    else:
        await play_song(bot, song, message)
