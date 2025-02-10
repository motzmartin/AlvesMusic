import discord
from discord.ext import commands

from utils import get_data, get_base_embed
from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context) -> None:
    from . import play_song

    data: dict = get_data(bot, ctx.guild.id)

    # Check if the bot is still connected to the voice channel

    voice: discord.VoiceClient = ctx.voice_client
    if not voice:
        data["player_state"] = 0

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The bot has left the voice channel."

        await ctx.send(embed=embed)
        return

    # Check if the queue is empty

    queue: list[dict] = data["queue"]
    if not queue:
        data["player_state"] = 0

        await voice.disconnect()

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        await ctx.send(embed=embed)
        return

    # Play the next track

    await play_song(bot, queue.pop(0))
