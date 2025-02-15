import discord
from discord.ext import commands

from . import to_timecode

# Default embed color
COLOR = "#73BCFF"

def get_base_embed(title: str = None) -> discord.Embed:
    """
    Creates a base embed with a default color and an optional title.
    """

    # Initialize embed with default color
    embed = discord.Embed()
    embed.color = discord.Color.from_str(COLOR)

    # Set title if provided
    if title:
        embed.title = title

    return embed

def get_embed(media: dict, message_type: int) -> discord.Embed:
    """
    Generates an embed message with details about the media.

    message_type (int):
        0 - Added to queue (single song)
        1 - Added to queue (playlist)
        2 - Playing
        3 - Now playing / Paused
    """

    # Retrieve the song context
    context: commands.Context = media["context"]

    # Determine embed title based on message type
    if message_type == 0 or message_type == 1:
        embed = get_base_embed("📌 Added to queue")
    elif message_type == 2:
        embed = get_base_embed("🎶 Now Playing")
    elif message_type == 3:
        # Check if playback is paused
        voice: discord.VoiceClient = context.voice_client
        embed = get_base_embed("⏸️ Paused" if voice and voice.is_paused() else "🔊 Now Playing")

    # Create the clickable song/playlist title link
    link = "[**{}**]({})".format(media["title"], media["url"])

    # Set embed description based on message type
    if message_type == 0:
        embed.description = "The song {} has been added to the queue.".format(link)
    elif message_type == 1:
        embed.description = "The **{}** tracks from the playlist {} have been added to the queue.".format(media["count"], link)
    elif message_type == 2:
        embed.description = "Now playing {}".format(link)
    elif message_type == 3:
        embed.description = link

    # Add the channel name and link if available
    if media["channel"] and media["channel_url"]:
        embed.add_field(name="Channel", value="[{}]({})".format(media["channel"], media["channel_url"]))

    # Add view count if available
    if media["view_count"]:
        embed.add_field(name="Views", value="{:,}".format(media["view_count"]).replace(",", " "))

    # Add song duration if available
    if media["duration"]:
        embed.add_field(name="Total Duration" if message_type == 1 else "Duration", value=to_timecode(media["duration"]))

    # Add song duration if available
    if media["thumbnail"]:
        embed.set_thumbnail(url=media["thumbnail"])

    # Add footer with requester information if available
    if context.author:
        embed.set_footer(text="{} requested by {}".format("Tracks" if message_type == 1 else "Song", context.author.global_name), icon_url=context.author.avatar.url)

    return embed
