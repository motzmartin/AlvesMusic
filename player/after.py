import discord
from discord.ext import commands

from alvesmusic import AlvesMusic

async def next_song(bot: AlvesMusic, ctx: commands.Context):
    from . import play_song

    data: dict = bot.data[ctx.guild.id]

    # Vérifie si le bot est toujours connecté au salon vocal

    voice: discord.VoiceClient = ctx.voice_client
    if not voice:
        data["player_state"] = 0

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🚫 Fin de la lecture"
        embed.description = "Le bot a quitté le salon vocal."

        return await ctx.send(embed=embed)

    # Vérifie si la file d'attente est vide

    queue: list[dict] = data["queue"]
    if not queue:
        data["player_state"] = 0
        await ctx.voice_client.disconnect()

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🚫 Fin de la lecture"
        embed.description = "La file d'attente est vide. Déconnexion du salon vocal."

        return await ctx.send(embed=embed)

    # Joue le prochain titre

    await play_song(bot, ctx, queue.pop(0))
