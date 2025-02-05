import random
import discord
from discord.ext import commands

from utils import timecode
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
        max_page = 1 if not queue else (len(queue) + 19) // 20

        if page >= 1 and page <= max_page:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")

            if queue:
                queue_list = ""
                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]
                    if song["title"] and song["url"]:
                        queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(timecode(song["duration"]))
                    queue_list += " *{}*\n".format(song["author"])

                embed.title = "📜 File d'attente - Page {}/{} ({} titre".format(page, max_page, len(queue))
                if len(queue) > 1:
                    embed.title += "s"
                embed.title += ")"
                embed.description = queue_list
                embed.add_field(name="Durée totale", value=timecode(sum(song["duration"] for song in queue if song["duration"])))
            else:
                embed.title = "📭 File d'attente vide"
                embed.description = "Aucune musique en attente."

            await ctx.send(embed=embed)
        else:
            raise commands.BadArgument()

    @commands.command()
    async def playing(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        voice: discord.VoiceClient = ctx.voice_client
        data: dict = self.bot.data[ctx.guild.id]
        if voice and data["player_state"] == 1:
            song: dict = data["playing"]

            if voice.is_paused():
                embed.title = "⏸️ En pause"
            else:
                embed.title = "🔊 En train de jouer"
            if song["title"] and song["url"]:
                embed.description = "[**{}**]({})".format(song["title"], song["url"])
            if song["channel"] and song["channel_url"]:
                embed.add_field(name="Chaîne", value="[{}]({})".format(song["channel"], song["channel_url"]))
            if song["view_count"]:
                embed.add_field(name="Vues", value="{:,}".format(song["view_count"]).replace(",", " "))
            if song["duration"]:
                embed.add_field(name="Durée", value=timecode(song["duration"]))
            if song["thumbnail"]:
                embed.set_thumbnail(url=song["thumbnail"])
            embed.set_footer(text="Demandée par {}".format(song["author"]), icon_url=song["avatar"])
        else:
            embed.title = "🔇 Aucune musique en cours"
            embed.description = "Aucune musique en cours de lecture."

        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
            if queue:
                queue.clear()

                embed.title = "🗑️ File d'attente vidée"
                embed.description = "Toutes les musiques ont été supprimées de la file d'attente."
            else:
                embed.title = "📭 File d'attente déjà vide"
                embed.description = "Il n'y a aucune musique en attente."
        else:
            embed.title = "❌ Impossible de vider la file d'attente"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

        await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
            if queue:
                random.shuffle(queue)

                embed.title = "🔀 File d'attente mélangée"
                embed.description = "L'ordre des chansons a été aléatoirement modifié !"
            else:
                embed.title = "❌ Impossible de mélanger"
                embed.description = "La file d'attente est vide, ajoutez des chansons avant d'utiliser **!shuffle**."
        else:
            embed.title = "❌ Impossible de mélanger"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            data: dict = self.bot.data[ctx.guild.id]
            if voice and data["player_state"] == 1:
                voice.stop()

                embed.title = "⏭️ Musique suivante"
                embed.description = "Lecture de la prochaine musique..."
            else:
                embed.title = "❌ Impossible de passer à la musique suivante"
                embed.description = "Aucune musique en cours de lecture."
        else:
            embed.title = "❌ Impossible de passer à la musique suivante"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

        await ctx.send(embed=embed)

    @commands.command()
    async def reset(self, ctx: commands.Context):
        if ctx.author.voice:
            await ctx.invoke(self.clear)
            await ctx.invoke(self.skip)
        else:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Impossible de de réinitialiser le bot"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

            await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            if voice and voice.is_playing():
                voice.pause()

                embed.title = "⏸️ Lecture mise en pause"
                embed.description = "Utilisez **!resume** pour reprendre la lecture."
            else:
                embed.title = "❌ Impossible de mettre en pause"
                embed.description = "Aucune musique en cours de lecture."
        else:
            embed.title = "❌ Impossible de mettre en pause"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

        await ctx.send(embed=embed)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            if voice and voice.is_paused():
                voice.resume()

                embed.title = "▶️ Lecture reprise"
                embed.description = "La musique reprend là où elle s'était arrêtée."
            else:
                embed.title = "❌ Impossible de reprendre"
                embed.description = "Aucune musique n'est actuellement en pause."
        else:
            embed.title = "❌ Impossible de reprendre"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(General(bot))
