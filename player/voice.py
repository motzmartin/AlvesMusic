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

async def play_song(bot: AlvesMusic, song: dict, message: discord.Message = None):
    from . import play_next

    ctx: commands.Context = song["context"]

    data: dict = get_data(bot, ctx.guild.id)
    data["player_state"] = 2

    # Loading embed

    embed = discord.Embed()
    embed.color = discord.Color.from_str("#73BCFF")
    embed.title = "⏳ Loading..."
    embed.description = "Loading [**{}**]({}) ({})".format(song["title"], song["url"], to_timecode(song["duration"]))
    embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

    if message:
        await message.edit(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    try:
        # Extracting the audio URL

        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])
        if not info.get("url"):
            raise Exception("Unable to extract the audio URL.")

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        # Connect or move to the author's voice channel if necessary

        voice: discord.VoiceClient = ctx.voice_client
        author_channel: discord.VoiceChannel = ctx.author.voice.channel
        if not voice:
            voice = await author_channel.connect()
        elif voice.channel != author_channel:
            await voice.move_to(author_channel)

        # Playing the track

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

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
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

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "❌ Error while playing audio"
        embed.description = str(err)

    # Sending the informative embed

    if message:
        await message.edit(embed=embed)
    else:
        await ctx.send(embed=embed)
