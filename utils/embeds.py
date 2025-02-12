import discord
from discord.ext import commands
from millify import millify

from . import to_timecode

COLOR = "#73BCFF"

def get_base_embed(title: str = None) -> discord.Embed:
    """
    Creates a base embed with a default color and an optional title.
    """
    embed = discord.Embed()
    embed.color = discord.Color.from_str(COLOR)

    if title:
        embed.title = title

    return embed

def get_embed(media: dict, message_type: int) -> discord.Embed:
    """
    Generates an embed message with details about the media.

    message_type (int):
        0 - added
        1 - added (playlist)
        2 - playing
        3 - now playing
    """

    context: commands.Context = media["context"]

    if message_type == 0 or message_type == 1:
        embed = get_base_embed("📌 Added to queue")
    elif message_type == 2:
        embed = get_base_embed("🎶 Now Playing")
    elif message_type == 3:
        voice: discord.VoiceClient = context.voice_client
        embed = get_base_embed("⏸️ Paused" if voice and voice.is_paused() else "🔊 Now Playing")

    link = "[**{}**]({})".format(media["title"], media["url"])

    if message_type == 0:
        embed.description = "The song {} has been added to the queue.".format(link)
    elif message_type == 1:
        embed.description = "The **{}** tracks from the playlist {} have been added to the queue.".format(media["count"], link)
    elif message_type == 2:
        embed.description = "Now playing {}".format(link)
    elif message_type == 3:
        embed.description = link

    if media["channel"] and media["channel_url"]:
        embed.add_field(name="Channel", value="[{}]({})".format(media["channel"], media["channel_url"]))

    if media["view_count"]:
        embed.add_field(name="Views", value=millify(media["view_count"]))

    if media["duration"]:
        embed.add_field(name="Total Duration" if message_type == 1 else "Duration", value=to_timecode(media["duration"]))

    if media["thumbnail"]:
        embed.set_thumbnail(url=media["thumbnail"])

    if context.author:
        embed.set_footer(text="Requested by {}".format(context.author.name), icon_url=context.author.avatar.url)

    return embed
