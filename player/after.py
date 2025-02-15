import discord
from discord.ext import commands

from utils import get_data, get_base_embed
from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context):
    from . import play_song

    voice: discord.VoiceClient = ctx.voice_client
    data: dict = get_data(bot, ctx.guild.id)

    if not voice:
        data["player_state"] = 0

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The bot has left the voice channel."

        return await ctx.send(embed=embed)

    queue: list[dict] = data["queue"]

    if not queue:
        data["player_state"] = 0

        await voice.disconnect()

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        return await ctx.send(embed=embed)

    await play_song(bot, queue.pop(0))
