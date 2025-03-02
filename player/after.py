import discord
from discord.ext import commands

from utils import get_base_embed, get_media_embed, edit_playing_embed
from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context):
    from . import play_song

    player = bot.get_player(ctx.guild.id)

    player.update_playing_embed = False

    await edit_playing_embed(player, 3)

    voice: discord.VoiceClient = ctx.voice_client

    if not voice:
        player.reset()

        embed = get_base_embed("🔇 Playback Ended")
        embed.description = "The bot has left the voice channel."

        return await ctx.send(embed=embed)

    if not player.queue:
        player.reset()

        await voice.disconnect()

        embed = get_base_embed("🔇 Playback Ended")
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        return await ctx.send(embed=embed)

    await play_song(bot, player.queue.pop(0))
