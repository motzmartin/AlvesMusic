import discord
from discord.ext import commands

from utils import *
from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context):
    """
    Play the next song in the queue if available.
    """

    # Import play_song to handle the next track
    from . import play_song

    # Retrieve the bot's voice client and the guild's music data
    data: dict = get_data(bot, ctx.guild.id)
    voice: discord.VoiceClient = ctx.voice_client

    # Check if the bot is still connected to the voice channel
    if not voice:
        # Update player state to idle
        data["player_state"] = 0

        # Create an embed indicating playback has ended
        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The bot has left the voice channel."

        # Send the embed message and exit the function
        return await ctx.send(embed=embed)

    # Retrieve the guild's queue
    queue: list[dict] = data["queue"]

    # Check if the queue is empty
    if not queue:
        # Update player state to idle
        data["player_state"] = 0

        # Disconnect the bot from the voice channel
        await voice.disconnect()

        # Create an embed indicating playback has ended
        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        # Send the embed message and exit the function
        return await ctx.send(embed=embed)

    # Play the next track from the queue
    await play_song(bot, queue.pop(0))
