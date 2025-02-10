import discord
from discord.ext import commands
from millify import millify

from . import to_timecode

COLOR = "#73BCFF"

def get_base_embed(title: str = None) -> discord.Embed:
    embed = discord.Embed()
    embed.color = discord.Color.from_str(COLOR)

    if title:
        embed.title = title

    return embed

def get_embed(song: dict, message_type: int, entries_length: int = 1, paused: bool = False) -> discord.Embed:
    """
    message_type (int):
        0 - added
        1 - added (playlist)
        2 - playing
        3 - now playing
    """

    if message_type == 0 or message_type == 1:
        embed = get_base_embed("📌 Added to queue")
    elif message_type == 2:
        embed = get_base_embed("🎶 Now Playing")
    elif message_type == 3:
        embed = get_base_embed("⏸️ Paused" if paused else "🔊 Now Playing")

    link = "[**{}**]({})".format(song["title"], song["url"])

    if message_type == 0:
        embed.description = "The song {} has been added to the queue.".format(link)
    elif message_type == 1:
        embed.description = "The **{}** tracks from the playlist {} have been added to the queue.".format(entries_length, link)
    elif message_type == 2:
        embed.description = "Now playing {}".format(link)
    elif message_type == 3:
        embed.description = link

    if song["channel"] and song["channel_url"]:
        embed.add_field(name="Channel", value="[{}]({})".format(song["channel"], song["channel_url"]))

    if song["view_count"]:
        embed.add_field(name="Views", value=millify(song["view_count"]))

    if song["duration"]:
        embed.add_field(name="Total Duration" if message_type == 1 else "Duration", value=to_timecode(song["duration"]))

    if song["thumbnail"]:
        embed.set_thumbnail(url=song["thumbnail"])

    context: commands.Context = song["context"]
    if context.author:
        embed.set_footer(text="Requested by {}".format(context.author.name), icon_url=context.author.avatar.url)

    return embed
