import asyncio
import discord
from discord.ext import commands

from utils import get_data, get_base_embed, get_inline_details, extract_audio, get_media_embed, get_thumbnail_url
from alvesmusic import AlvesMusic

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, song: dict, message: discord.Message = None):
    from . import play_next

    context: commands.Context = song["context"]

    data: dict = get_data(bot, context.guild.id)
    data["player_state"] = 2

    embed = get_base_embed("⏳ Loading...")
    embed.description = "Loading {}".format(get_inline_details(song))

    if message:
        await message.edit(embed=embed)
    else:
        message = await context.send(embed=embed)

    try:
        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        if not info.get("url") or not info.get("title") or not info.get("webpage_url"):
            raise Exception("Unable to extract audio data.")

        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        voice: discord.VoiceClient = context.voice_client
        author_voice: discord.VoiceClient = context.author.voice

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

        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(bot, context), bot.loop))

        new_song = {
            "title": info["title"],
            "url": info["webpage_url"],
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
            "view_count": info.get("view_count"),
            "duration": info.get("duration"),
            "thumbnail": get_thumbnail_url(info.get("id")),
            "context": context
        }
        data["playing"] = new_song

        data["player_state"] = 1

        embed = get_media_embed(new_song, 4)

        if message:
            await message.edit(embed=embed)
        else:
            await context.send(embed=embed)
    except Exception as err:
        data["player_state"] = 0

        voice: discord.VoiceClient = context.voice_client
        if voice:
            await voice.disconnect()

        embed = get_base_embed("❌ Error while Playing Audio")
        embed.description = str(err)

        if message:
            await message.edit(embed=embed)
        else:
            await context.send(embed=embed)
