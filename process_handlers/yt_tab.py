import discord
from discord.ext import commands

from utils import get_inline_details, get_thumbnail_url, get_media_embed, extract_remaining
from player import play_song
from alvesmusic import AlvesMusic

async def process_yt_tab(bot: AlvesMusic,
                    ctx: commands.Context,
                    info: dict,
                    data: dict,
                    queue: list[dict],
                    message: discord.Message):
    if not info.get("entries") or not info.get("title") or not info.get("webpage_url"):
        raise Exception("Error occurred during extraction.")

    first: dict = info["entries"][0]

    if not first.get("title") or not first.get("url"):
        raise Exception("Error occurred during extraction.")

    pending = {
        "title": info["title"],
        "url": info["webpage_url"],
        "channel": info.get("channel"),
        "channel_url": info.get("channel_url"),
        "view_count": info.get("view_count"),
        "duration": None,
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

    if data["player_state"] != 0:
        queue.append(song)

        song["position"] = len(queue)
        song["channel"] = first.get("channel")
        song["channel_url"] = first.get("channel_url")
        song["view_count"] = first.get("view_count")
        song["thumbnail"] = get_thumbnail_url(first.get("id"))

        embed = get_media_embed(song, 0)

        await ctx.send(embed=embed)
    else:
        await play_song(bot, song)

    remaining_info = await bot.loop.run_in_executor(None, extract_remaining, info["webpage_url"])

    if not remaining_info.get("entries"):
        return await message.delete()

    if not remaining_info.get("title") or not remaining_info.get("webpage_url"):
        raise Exception("Error occurred during extraction.")

    entries: list[dict] = remaining_info["entries"]

    songs = []
    total_duration = 0
    preview = ""

    for i in range(len(entries)):
        if not entries[i].get("title") or not entries[i].get("url"):
            raise Exception("Error occurred during extraction.")

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

    queue.extend(songs)

    playlist = {
        "title": remaining_info["title"],
        "url": remaining_info["webpage_url"],
        "count": len(songs),
        "preview": preview,
        "channel": remaining_info.get("channel"),
        "channel_url": remaining_info.get("channel_url"),
        "view_count": remaining_info.get("view_count"),
        "duration": total_duration,
        "thumbnail": get_thumbnail_url(entries[0].get("id")),
        "context": ctx
    }

    embed = get_media_embed(playlist, 1)

    await message.edit(embed=embed)
