import discord
from discord.ext import commands

from utils import extract_remaining, get_thumbnail_url, get_inline_details, get_media_embed
from player import play_song
from alvesmusic import AlvesMusic

async def process_playlist(bot: AlvesMusic, ctx: commands.Context, message: discord.Message, info: dict):
    player = bot.get_player(ctx.guild.id)

    if not info.get("title") or not info.get("webpage_url"):
        raise Exception("Cannot retrieve title or URL. (2)")

    first: dict = info["entries"][0]

    if not first.get("title") or not first.get("url"):
        raise Exception("Cannot retrieve title or URL. (3)")

    pending = {
        "title": info["title"],
        "url": info["webpage_url"],
        "channel": info.get("channel"),
        "channel_url": info.get("channel_url"),
        "view_count": info.get("view_count"),
        "duration": 0,
        "thumbnail": get_thumbnail_url(first.get("id")),
        "context": ctx
    }

    embed = get_media_embed(pending, 2)

    await message.edit(embed=embed)

    song = {
        "title": first["title"],
        "url": first["url"],
        "duration": first.get("duration"),
        "context": ctx
    }

    if not player.is_ready():
        player.queue.append(song.copy())

        song["channel"] = first.get("channel")
        song["channel_url"] = first.get("channel_url")
        song["view_count"] = first.get("view_count")
        song["thumbnail"] = get_thumbnail_url(first.get("id"))
        song["position"] = len(player.queue)

        embed = get_media_embed(song, 0)

        await ctx.send(embed=embed)
    else:
        await play_song(bot, song)

    info = await bot.loop.run_in_executor(None, extract_remaining, info["webpage_url"])

    if not info.get("entries"):
        return await message.delete()

    if not info.get("title") or not info.get("webpage_url"):
        raise Exception("Cannot retrieve title or URL. (4)")

    entries: list[dict] = info["entries"]

    preview = ""
    total_duration = 0

    songs: list[dict] = []

    for i in range(len(entries)):
        if not entries[i].get("title") or not entries[i].get("url"):
            raise Exception("Cannot retrieve title or URL. (5)")

        song = {
            "title": entries[i]["title"],
            "url": entries[i]["url"],
            "duration": entries[i].get("duration"),
            "context": ctx
        }

        if i < 5:
            preview += "{}\n".format(get_inline_details(song, index=(i + 2), include_author=False))

        if song["duration"]:
            total_duration += song["duration"]

        songs.append(song)

    if len(songs) > 5:
        preview += "**... ({} more)**".format(len(songs) - 5)

    player.queue.extend(songs)

    playlist = {
        "title": info["title"],
        "url": info["webpage_url"],
        "channel": info.get("channel"),
        "channel_url": info.get("channel_url"),
        "view_count": info.get("view_count"),
        "duration": total_duration,
        "thumbnail": get_thumbnail_url(entries[0].get("id")),
        "context": ctx,
        "count": len(songs),
        "preview": preview
    }

    embed = get_media_embed(playlist, 1)

    await message.edit(embed=embed)
