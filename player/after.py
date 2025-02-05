import discord
from discord.ext import commands

from alvesmusic import AlvesMusic

async def play_next(bot: AlvesMusic, ctx: commands.Context):
    from . import play_song

    data: dict = bot.data[ctx.guild.id]

    # Check if the bot is still connected to the voice channel

    voice: discord.VoiceClient = ctx.voice_client
    if not voice:
        data["player_state"] = 0

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🚫 Playback Ended"
        embed.description = "The bot has left the voice channel."

        return await ctx.send(embed=embed)

    # Check if the queue is empty

    queue: list[dict] = data["queue"]
    if not queue:
        data["player_state"] = 0
        await ctx.voice_client.disconnect()

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🚫 Playback Ended"
        embed.description = "The queue is empty. Disconnecting from the voice channel."

        return await ctx.send(embed=embed)

    # Play the next track

    await play_song(bot, queue.pop(0))
