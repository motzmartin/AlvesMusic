import asyncio
import discord
from discord.ext import commands
from millify import millify

from alvesmusic import AlvesMusic
from utils import extract_audio, to_timecode, get_data

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, song: dict, search_message: discord.Message = None):
    from . import play_next

    ctx: commands.Context = song["context"]

    data: dict = get_data(bot, ctx.guild.id)
    data["player_state"] = 2

    embed = discord.Embed()
    embed.color = discord.Color.from_str("#73BCFF")

    try:
        # Extracting the audio URL

        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        if not info.get("url"):
            raise Exception("Unable to extract the audio URL.")

        # Playing the track

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        voice: discord.VoiceClient = ctx.voice_client
        if not voice:
            raise Exception("The bot has left the voice channel.")

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(bot, ctx), bot.loop))

        # Updating the currently playing song

        data["playing"] = {
            "title": info.get("title"),
            "url": info.get("webpage_url"),
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
            "view_count": info.get("view_count"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "context": ctx
        }
        data["player_state"] = 1

        # Playback embed

        embed.title = "🎶 Now Playing"
        if info.get("title") and info.get("webpage_url"):
            embed.description = "Now playing [**{}**]({})".format(info["title"], info["webpage_url"])
        if info.get("channel") and info.get("channel_url"):
            embed.add_field(name="Channel", value="[{}]({})".format(info["channel"], info["channel_url"]))
        if info.get("view_count"):
            embed.add_field(name="Views", value=millify(info["view_count"]))
        if info.get("duration"):
            embed.add_field(name="Duration", value=to_timecode(info["duration"]))
        if info.get("thumbnail"):
            embed.set_thumbnail(url=info["thumbnail"])
        embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)
    except Exception as err:
        # Error while playing

        data["player_state"] = 0

        voice: discord.VoiceClient = ctx.voice_client
        if voice:
            await voice.disconnect()

        # Playback error embed

        embed.title = "❌ Error while playing audio"
        embed.description = "`{}`".format(err)

    # Sending the informative embed

    if search_message:
        await search_message.edit(embed=embed)
    else:
        await ctx.send(embed=embed)
