import discord
from discord.ext import commands

from . import to_timecode

COLOR = "#73BCFF"

def get_base_embed(title: str = None) -> discord.Embed:
    embed = discord.Embed()
    embed.color = discord.Color.from_str(COLOR)

    if title:
        embed.title = title

    return embed

def get_inline_details(song: dict, index: int = None, include_author: bool = True) -> str:
    line = ""

    if index is not None:
        line += "**{}.** ".format(index)

    title: str = song["title"]
    title = title.replace("[", "(").replace("]", ")")

    if len(title) > 30:
        title = title[:30] + "..."

    line += "[**{}**]({})".format(title, song["url"])

    if song["duration"]:
        line += " ({})".format(to_timecode(song["duration"]))

    if include_author:
        context: commands.Context = song["context"]
        if context.author:
            line += " {}".format(context.author.mention)

    return line

def get_media_embed(media: dict, message_type: int) -> discord.Embed:
    """
    message_type (int):
        0 - Added to queue (single song)
        2 - Added to queue (playlist)
        3 - Pending
        4 - Playing
        5 - Now playing / Paused
    """

    context: commands.Context = media["context"]

    if message_type == 0:
        embed = get_base_embed("📌 Added to queue")
    elif message_type == 2:
        embed = get_base_embed("💿 Tracks added to queue")
    elif message_type == 3:
        embed = get_base_embed("🕐 Pending...")
    elif message_type == 4:
        embed = get_base_embed("🎶 Now Playing")
    elif message_type == 5:
        voice: discord.VoiceClient = context.voice_client
        embed = get_base_embed("⏸️ Paused" if voice and voice.is_paused() else "🔊 Now Playing")

    title: str = media["title"]
    title = title.replace("[", "(").replace("]", ")")

    link = "[**{}**]({})".format(title, media["url"])

    if message_type == 0:
        embed.description = "The song {} has been added to the queue at **{}.**".format(link, media["position"])
    elif message_type == 2:
        embed.description = "The **{}** remaining tracks from the playlist {} have been added to the queue.\n\n{}".format(media["count"], link, media["preview"])
    elif message_type == 3:
        embed.description = "The remaining tracks in the playlist {} are still pending... Please be patient.".format(link)
    elif message_type == 4:
        embed.description = "Now playing {}".format(link)
    elif message_type == 5:
        embed.description = link

    if media["channel"] and media["channel_url"]:
        embed.add_field(name="Channel", value="[**{}**]({})".format(media["channel"], media["channel_url"]))

    if media["view_count"]:
        embed.add_field(name="Views", value="{:,}".format(media["view_count"]).replace(",", " "))

    if media["duration"]:
        embed.add_field(name="Total Duration" if message_type == 2 else "Duration", value=to_timecode(media["duration"]))

    if media["thumbnail"]:
        embed.set_thumbnail(url=media["thumbnail"])

    if context.author:
        embed.set_footer(text="Requested by {}".format(context.author.global_name), icon_url=context.author.avatar.url)

    return embed
