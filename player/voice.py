import asyncio
import discord
from discord.ext import commands

from alvesmusic import AlvesMusic
from utils import extract_audio, to_timecode, get_data, get_embed, get_base_embed

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, song: dict, message: discord.Message = None) -> None:
    from . import play_next

    ctx: commands.Context = song["context"]

    data: dict = get_data(bot, ctx.guild.id)
    data["player_state"] = 2

    # Loading embed

    embed = get_base_embed("⏳ Loading...")
    embed.description = "Loading [**{}**]({})".format(song["title"], song["url"])
    if song["duration"]:
        embed.description += " ({})".format(to_timecode(song["duration"]))
    if ctx.author:
        embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)
    if message:
        await message.edit(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    try:
        # Extracting the audio URL

        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        if not info.get("url") or not info.get("title") or not info.get("webpage_url"):
            raise Exception("Unable to extract audio data.")

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        # Connect or move to the author's voice channel if necessary

        author_voice: discord.VoiceClient = ctx.author.voice
        if author_voice:
            author_channel = author_voice.channel
            voice: discord.VoiceClient = ctx.voice_client
            if not voice:
                voice = await author_channel.connect(self_deaf=True)
            elif voice.channel != author_channel:
                await voice.move_to(author_channel)
                await voice.guild.change_voice_state(channel=author_channel, self_deaf=True)
        else:
            raise Exception("The user is no longer connected to the voice channel.")

        # Playing the track

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(bot, ctx), bot.loop))

        # Updating the currently playing song

        new_song = {
            "title": info["title"],
            "url": info["webpage_url"],
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
            "view_count": info.get("view_count"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "context": ctx
        }

        data["playing"] = new_song
        data["player_state"] = 1

        # Playback embed

        embed = get_embed(new_song, 2)
        if message:
            await message.edit(embed=embed)
        else:
            await ctx.send(embed=embed)
    except Exception as err:
        # Error while playing

        data["player_state"] = 0

        voice: discord.VoiceClient = ctx.voice_client
        if voice:
            await voice.disconnect()

        # Playback error embed

        embed = get_base_embed("❌ Error while playing audio")
        embed.description = str(err)
        if message:
            await message.edit(embed=embed)
        else:
            await ctx.send(embed=embed)
