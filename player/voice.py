import asyncio
import time
import discord
from discord.ext import commands

from utils import extract_audio, get_thumbnail_url, get_inline_details, get_base_embed, get_media_embed
from alvesmusic import AlvesMusic

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, song: dict, message: discord.Message = None):
    from . import play_next

    ctx: commands.Context = song["context"]

    data = bot.get_data(ctx.guild.id)
    data.player_state = 2

    embed = get_base_embed("⏳ Loading...")
    embed.description = "Loading {}".format(get_inline_details(song))

    if message:
        await message.edit(embed=embed)
    else:
        message = await ctx.send(embed=embed)

    try:
        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        if not info.get("title") or not info.get("webpage_url"):
            raise Exception("Cannot retrieve title or URL.")

        if not info.get("url"):
            raise Exception("Unable to extract audio data.")

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        voice: discord.VoiceClient = ctx.voice_client
        author_voice: discord.VoiceClient = ctx.author.voice

        if not voice:
            if author_voice:
                voice = await author_voice.channel.connect(self_deaf=True)
            else:
                raise Exception("Cannot join voice channel: user is not connected to any voice channel.")
        elif author_voice:
            author_channel = author_voice.channel

            if voice.channel != author_channel:
                await voice.move_to(author_channel)
                await voice.guild.change_voice_state(channel=author_channel, self_deaf=True)

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(bot, ctx), bot.loop))

        new_song = {
            "title": info["title"],
            "url": info["webpage_url"],
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
            "view_count": info.get("view_count"),
            "duration": info.get("duration"),
            "thumbnail": get_thumbnail_url(info.get("id")),
            "context": ctx
        }

        data.reset()

        data.player_state = 1
        data.playing = new_song
        data.started_at = time.time()

        embed = get_media_embed(new_song, 3)

        if message:
            await message.edit(embed=embed)
        else:
            await ctx.send(embed=embed)
    except Exception as err:
        data.reset()

        voice: discord.VoiceClient = ctx.voice_client
        if voice:
            await voice.disconnect()

        embed = get_base_embed("❌ Error while Playing Audio")
        embed.description = str(err)

        if message:
            await message.edit(embed=embed)
        else:
            await ctx.send(embed=embed)
