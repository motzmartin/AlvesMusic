import discord
from discord.ext import commands

from utils import get_base_embed
from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context):
    from . import play_song

    voice: discord.VoiceClient = ctx.voice_client
    data = bot.get_data(ctx.guild.id)

    if not voice:
        data.reset()

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The bot has left the voice channel."

        return await ctx.send(embed=embed)

    if not data.queue:
        data.reset()

        await voice.disconnect()

        embed = get_base_embed("🚫 Playback Ended")
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        return await ctx.send(embed=embed)

    await play_song(bot, data.queue.pop(0))
