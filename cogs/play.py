import discord
from discord.ext import commands

from alvesmusic import AlvesMusic
from utils import extract, timecode
from player import play_song

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        # Vérifie si l'utilisateur est dans un salon vocal

        if not ctx.author.voice:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Impossible de lire la musique"
            embed.description = "Tu dois être dans un salon vocal pour utiliser cette commande."

            return await ctx.send(embed=embed)

        # Se connecte ou change de salon si nécessaire

        voice: discord.VoiceClient = ctx.voice_client
        author_channel = ctx.author.voice.channel
        if voice:
            if voice.channel != author_channel:
                await voice.move_to(author_channel)
        else:
            await author_channel.connect()

        # Envoi de l'embed de recherche

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🔍 Recherche en cours"
        embed.description = "Recherche de **{}** en cours, cela peut prendre un instant.".format(query)

        search_message = await ctx.send(embed=embed)

        # Recherche du ou des titres

        data: dict = self.bot.data[ctx.guild.id]

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)
        except Exception as err:
            # Erreur lors de la recherche

            voice: discord.VoiceClient = ctx.voice_client
            if voice and data["player_state"] == 0:
                await voice.disconnect()

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Erreur lors de la recherche"
            embed.description = "`{}`".format(err)

            return await search_message.edit(embed=embed)

        queue: list[dict] = data["queue"]

        if "entries" in info:
            # Aucun, un ou plusieurs résultat(s)

            if not info["entries"]:
                # Aucun résultat, envoi de l'embed informatif
                # Exemple : !play unyoxhgikwdbplecfjqa

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "❌ Aucun résultat"
                embed.description = "Aucun résultat trouvé pour **{}**.".format(query)

                await search_message.edit(embed=embed)
            elif len(info["entries"]) == 1:
                # Un seul résultat (souvent issu d'une recherche)
                # Exemple : !play calogero 1987

                first: dict = info["entries"][0]

                song = {
                    "url": first.get("url"),
                    "title": first.get("title"),
                    "duration": first.get("duration"),
                    "author": ctx.author.name,
                    "avatar": ctx.author.avatar.url
                }

                if data["player_state"] != 0:
                    # Ajout à la file d'attente

                    queue.append(song)

                    # Envoi de l'embed informatif

                    embed = discord.Embed()
                    embed.color = discord.Color.from_str("#73BCFF")
                    embed.title = "📌 Ajoutée à la file d'attente"
                    if first.get("title") and first.get("url"):
                        embed.description = "La musique [**{}**]({}) a été ajoutée à la file d'attente.".format(first["title"], first["url"])
                    if first.get("channel") and first.get("channel_url"):
                        embed.add_field(name="Chaîne", value="[{}]({})".format(first["channel"], first["channel_url"]))
                    if first.get("view_count"):
                        embed.add_field(name="Vues", value="{:,}".format(first["view_count"]).replace(",", " "))
                    if first.get("duration"):
                        embed.add_field(name="Durée", value=timecode(first["duration"]))
                    if first.get("id"):
                        embed.set_thumbnail(url="https://i.ytimg.com/vi/{}/hqdefault.jpg".format(first["id"]))
                    embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                    await search_message.edit(embed=embed)
                else:
                    # Lecture du titre

                    await play_song(self.bot, ctx, song, search_message)
            else:
                # Plusieurs résultats (issus d'une playlist/mix YouTube)
                # Exemple : !play https://www.youtube.com/playlist?list=PLdSUTU0oamrwC0PY7uUc0EJMKlWCiku43

                entries: list[dict] = info["entries"]

                # Ajout des titres

                for entry in entries:
                    queue.append({
                        "url": entry.get("url"),
                        "title": entry.get("title"),
                        "duration": entry.get("duration"),
                        "author": ctx.author.name,
                        "avatar": ctx.author.avatar.url
                    })

                # Envoi de l'embed informatif

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "📌 Ajoutées à la file d'attente"
                if info.get("title") and info.get("webpage_url"):
                    embed.description = "Les **{}** titres de la playlist [**{}**]({}) ont été ajoutées à la file d'attente.".format(len(info["entries"]), info["title"], info["webpage_url"])
                if info.get("channel") and info.get("channel_url"):
                    embed.add_field(name="Chaîne", value="[{}]({})".format(info["channel"], info["channel_url"]))
                if info.get("view_count"):
                    embed.add_field(name="Vues", value="{:,}".format(info["view_count"]).replace(",", " "))
                embed.add_field(name="Durée totale", value=timecode(sum(entry["duration"] for entry in entries if entry.get("duration"))))
                if entries[0].get("id"):
                    embed.set_thumbnail(url="https://i.ytimg.com/vi/{}/hqdefault.jpg".format(entries[0]["id"]))
                embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)

                # Lecture du premier titre s'il n'y a aucune chanson en cours

                if data["player_state"] == 0:
                    await play_song(self.bot, ctx, queue.pop(0))
        else:
            # Un seul résultat (issu d'une URL YouTube)
            # Exemple : !play https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp

            song = {
                "url": info.get("webpage_url"),
                "title": info.get("title"),
                "duration": info.get("duration"),
                "author": ctx.author.name,
                "avatar": ctx.author.avatar.url
            }

            if data["player_state"] != 0:
                # Ajout à la file d'attente

                queue.append(song)

                # Envoi de l'embed informatif

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "📌 Ajoutée à la file d'attente"
                if info.get("title") and info.get("webpage_url"):
                    embed.description = "La musique [**{}**]({}) a été ajoutée à la file d'attente.".format(info["title"], info["webpage_url"])
                if info.get("channel") and info.get("channel_url"):
                    embed.add_field(name="Chaîne", value="[{}]({})".format(info["channel"], info["channel_url"]))
                if info.get("view_count"):
                    embed.add_field(name="Vues", value="{:,}".format(info["view_count"]).replace(",", " "))
                if info.get("duration"):
                    embed.add_field(name="Durée", value=timecode(info["duration"]))
                if info.get("thumbnail"):
                    embed.set_thumbnail(url=info["thumbnail"])
                embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)
            else:
                # Lecture du titre

                await play_song(self.bot, ctx, song, search_message)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
