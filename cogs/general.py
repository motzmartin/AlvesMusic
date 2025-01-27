import random
import discord
from discord.ext import commands
from utils import duration_str
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
        max_page = (len(queue) + 19) // 20

        if queue:
            if page >= 1 and page <= max_page:
                queue_list = ""
                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]
                    if song["title"] and song["url"]:
                        queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(duration_str(song["duration"]))
                    queue_list += " *{}*\n".format(song["author"])

                embed.title = "📜 File d'attente - Page {}/{} ({} titre".format(page, max_page, len(queue))
                if len(queue) > 1:
                    embed.title += "s"
                embed.title += ")"
                embed.description = queue_list

                embed.add_field(name="Durée totale", value=duration_str(sum(song["duration"] for song in queue if song["duration"])))
            else:
                raise commands.BadArgument()
        else:
            embed.title = "📭 File d'attente vide"
            embed.description = "Aucune musique en attente."

        await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        playing: dict | str = self.bot.data[ctx.guild.id]["playing"]
        if playing and playing != "waiting":
            embed.title = "🔊 En train de jouer"
            if playing["title"] and playing["url"]:
                embed.description = "[**{}**]({})".format(playing["title"], playing["url"])

            if playing["channel"] and playing["channel_url"]:
                embed.add_field(name="Chaîne", value="[{}]({})".format(playing["channel"], playing["channel_url"]))
            if playing["view_count"]:
                embed.add_field(name="Vues", value="{:,}".format(playing["view_count"]).replace(",", " "))
            if playing["duration"]:
                embed.add_field(name="Durée", value=duration_str(playing["duration"]))
            if playing["thumbnail"]:
                embed.set_thumbnail(url=playing["thumbnail"])
            embed.set_footer(text="Demandée par {}".format(playing["author"]), icon_url=playing["avatar"])
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
            playing: dict | str = self.bot.data[ctx.guild.id]["playing"]
            if voice and playing and playing != "waiting":
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
    async def stop(self, ctx: commands.Context):
        if ctx.author.voice:
            await ctx.invoke(self.clear)
            await ctx.invoke(self.skip)
        else:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Impossible de d'arrêter le bot"
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
