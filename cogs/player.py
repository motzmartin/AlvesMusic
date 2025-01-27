import asyncio
import discord
from discord.ext import commands
from ydl import extract, extract_audio
from utils import duration_str
from alvesmusic import AlvesMusic

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

class Player(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    async def play_next(self, ctx: commands.Context, search_message: discord.Message = None):
        # Définit playing à "waiting" pour éviter la lecture de deux musiques

        data: dict = self.bot.data[ctx.guild.id]
        data["playing"] = "waiting"

        # Vérifie si le bot est toujours connecté au salon vocal

        voice: discord.VoiceClient = ctx.voice_client
        if not voice:
            data["playing"] = None

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Erreur lors de la lecture"
            embed.description = "Le bot a quitté le salon vocal."

            if search_message:
                return await search_message.edit(embed=embed)

            return await ctx.send(embed=embed)

        # Vérifie si la file d'attente est vide

        queue: list[dict] = data["queue"]
        if not queue:
            data["playing"] = None
            await voice.disconnect()

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "🚫 Fin de la lecture"
            embed.description = "La file d'attente est vide. Déconnexion du salon vocal."

            return await ctx.send(embed=embed)

        # Récupération de l'audio de la musique

        playing = queue.pop(0)

        try:
            info = await self.bot.loop.run_in_executor(None, extract_audio, playing["url"])

            if not info.get("url"):
                raise ValueError("Impossible d'extraire l'URL audio.")
        except Exception as e:
            data["playing"] = None
            voice: discord.VoiceClient = ctx.voice_client
            if voice:
                await voice.disconnect()

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Erreur lors de l'extraction de l'audio"
            embed.description = "Raison : `{}`".format(e)

            if search_message:
                return await search_message.edit(embed=embed)

            return await ctx.send(embed=embed)

        playing["channel"] = info.get("channel")
        playing["channel_url"] = info.get("channel_url")
        playing["view_count"] = info.get("view_count")
        playing["thumbnail"] = info.get("thumbnail")

        data["playing"] = playing

        # Lecture de la musique

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        voice: discord.VoiceClient = ctx.voice_client
        if not voice:
            data["playing"] = None

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Erreur lors de la lecture"
            embed.description = "Le bot a quitté le salon vocal."

            if search_message:
                return await search_message.edit(embed=embed)

            return await ctx.send(embed=embed)

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

        # Envoi de l'embed de lecture

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🎶 Lecture de la musique"
        if info.get("title") and info.get("webpage_url"):
            embed.description = "Lecture de [**{}**]({}) en cours.".format(info["title"], info["webpage_url"])

        if info.get("channel") and info.get("channel_url"):
            embed.add_field(name="Chaîne", value="[{}]({})".format(info["channel"], info["channel_url"]))
        if info.get("view_count"):
            embed.add_field(name="Vues", value="{:,}".format(info["view_count"]).replace(",", " "))
        if info.get("duration"):
            embed.add_field(name="Durée", value=duration_str(info["duration"]))
        if info.get("thumbnail"):
            embed.set_thumbnail(url=info["thumbnail"])
        embed.set_footer(text="Demandée par {}".format(playing["author"]), icon_url=playing["avatar"])

        if search_message:
            await search_message.edit(embed=embed)
        else:
            await ctx.send(embed=embed)

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

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)
        except Exception as e:
            voice: discord.VoiceClient = ctx.voice_client
            if voice and not self.bot.data[ctx.guild.id]["playing"]:
                await voice.disconnect()

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Erreur lors de la recherche"
            embed.description = "Raison : `{}`".format(e)

            return await search_message.edit(embed=embed)

        queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]

        if "entries" in info:
            if not info["entries"]:
                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "❌ Aucun résultat"
                embed.description = "Aucun résultat trouvé pour **{}**.".format(query)

                return await search_message.edit(embed=embed)
            elif len(info["entries"]) == 1:
                first: dict = info["entries"][0]

                song = {
                    "url": first.get("url"),
                    "title": first.get("title"),
                    "duration": first.get("duration"),
                    "author": ctx.author.name,
                    "avatar": ctx.author.avatar.url
                }

                queue.append(song)

                if self.bot.data[ctx.guild.id]["playing"]:
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
                        embed.add_field(name="Durée", value=duration_str(first["duration"]))
                    if first.get("id"):
                        embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/{}/maxresdefault.webp".format(first["id"]))
                    embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                    await search_message.edit(embed=embed)
                else:
                    await self.play_next(ctx, search_message)
            else:
                entries: list[dict] = info["entries"]

                songs = []
                for entry in entries:
                    songs.append({
                        "url": entry.get("url"),
                        "title": entry.get("title"),
                        "duration": entry.get("duration"),
                        "author": ctx.author.name,
                        "avatar": ctx.author.avatar.url
                    })

                queue.extend(songs)

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "📌 Ajoutées à la file d'attente"
                if info.get("title") and info.get("webpage_url"):
                    embed.description = "Les **{}** titres de la playlist [**{}**]({}) ont été ajoutées à la file d'attente.".format(len(info["entries"]), info["title"], info["webpage_url"])

                if info.get("channel") and info.get("channel_url"):
                    embed.add_field(name="Chaîne", value="[{}]({})".format(info["channel"], info["channel_url"]))
                if info.get("view_count"):
                    embed.add_field(name="Vues", value="{:,}".format(info["view_count"]).replace(",", " "))
                embed.add_field(name="Durée totale", value=duration_str(sum(entry["duration"] for entry in entries if entry.get("duration"))))
                if entries[0].get("id"):
                    embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/{}/maxresdefault.webp".format(entries[0]["id"]))
                embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)

                if not self.bot.data[ctx.guild.id]["playing"]:
                    await self.play_next(ctx)
        else:
            song = {
                "url": info.get("webpage_url"),
                "title": info.get("title"),
                "duration": info.get("duration"),
                "author": ctx.author.name,
                "avatar": ctx.author.avatar.url
            }

            queue.append(song)

            if self.bot.data[ctx.guild.id]["playing"]:
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
                    embed.add_field(name="Durée", value=duration_str(info["duration"]))
                if info.get("thumbnail"):
                    embed.set_thumbnail(url=info["thumbnail"])
                embed.set_footer(text="Demandée par {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)
            else:
                await self.play_next(ctx, search_message)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Player(bot))
