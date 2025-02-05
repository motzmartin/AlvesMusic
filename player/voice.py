import asyncio
import discord
from discord.ext import commands

from alvesmusic import AlvesMusic
from utils import extract_audio, timecode

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, ctx: commands.Context, song: dict, search_message: discord.Message = None):
    from . import next_song

    data: dict = bot.data[ctx.guild.id]

    embed = discord.Embed()
    embed.color = discord.Color.from_str("#73BCFF")

    try:
        # Extraction de l'URL audio

        data["player_state"] = 2

        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        if not info.get("url"):
            raise Exception("Impossible d'extraire l'URL audio.")

        # Lecture du titre

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        voice: discord.VoiceClient = ctx.voice_client
        if not voice:
            raise Exception("Le bot a quitté le salon vocal.")

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(next_song(bot, ctx), bot.loop))

        # Mise à jour de la chanson en cours de lecture

        song["channel"] = info.get("channel")
        song["channel_url"] = info.get("channel_url")
        song["view_count"] = info.get("view_count")
        song["thumbnail"] = info.get("thumbnail")

        data["playing"] = song
        data["player_state"] = 1

        # Embed de lecture

        embed.title = "🎶 Lecture de la musique"
        if info.get("title") and info.get("webpage_url"):
            embed.description = "Lecture de [**{}**]({}) en cours.".format(info["title"], info["webpage_url"])
        if info.get("channel") and info.get("channel_url"):
            embed.add_field(name="Chaîne", value="[{}]({})".format(info["channel"], info["channel_url"]))
        if info.get("view_count"):
            embed.add_field(name="Vues", value="{:,}".format(info["view_count"]).replace(",", " "))
        if info.get("duration"):
            embed.add_field(name="Durée", value=timecode(info["duration"]))
        if info.get("thumbnail"):
            embed.set_thumbnail(url=info["thumbnail"])
        embed.set_footer(text="Demandée par {}".format(song["author"]), icon_url=song["avatar"])
    except Exception as err:
        # Erreur lors de la lecture

        data["player_state"] = 0

        voice: discord.VoiceClient = ctx.voice_client
        if voice:
            await voice.disconnect()

        # Embed d'erreur de lecture

        embed.title = "❌ Erreur lors de la lecture de l'audio"
        embed.description = "`{}`".format(err)

    # Envoi de l'embed informatif

    if search_message:
        await search_message.edit(embed=embed)
    else:
        await ctx.send(embed=embed)
