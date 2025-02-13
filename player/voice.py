import asyncio
import discord
from discord.ext import commands

from alvesmusic import AlvesMusic
from utils import extract_audio, to_timecode, get_data, get_embed, get_base_embed

# FFMPEG options for better audio stream handling
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

async def play_song(bot: AlvesMusic, song: dict, message: discord.Message = None):
    """
    Extracts audio information from a URL and plays the audio in the voice channel.
    """

    # Import play_next to handle the next track after playback
    from . import play_next

    # Retrieve the song context
    context: commands.Context = song["context"]

    # Retrieve the guild's music data and set player state to "loading"
    data: dict = get_data(bot, context.guild.id)
    data["player_state"] = 2

    # Create a loading embed
    embed = get_base_embed("⏳ Loading...")
    embed.description = "Loading [**{}**]({})".format(song["title"], song["url"])

    # Add song duration if available
    if song["duration"]:
        embed.description += " ({})".format(to_timecode(song["duration"]))

    # Add requester information if available
    if context.author:
        embed.set_footer(text="Song requested by {}".format(context.author.global_name), icon_url=context.author.avatar.url)

    # Send or update the message with the loading embed
    if message:
        await message.edit(embed=embed)
    else:
        message = await context.send(embed=embed)

    try:
        # Extract the audio URL from the provided song link
        info = await bot.loop.run_in_executor(None, extract_audio, song["url"])

        # Validate extracted audio data
        if not info.get("url") or not info.get("title") or not info.get("webpage_url"):
            raise Exception("Unable to extract audio data.")

        # Create the FFMPEG audio source
        source = discord.FFmpegOpusAudio(info["url"], **FFMPEG_OPTIONS)

        # Retrieve the author's voice state
        author_voice: discord.VoiceClient = context.author.voice

        # Check if the author is connected to a voice channel
        if author_voice:
            voice: discord.VoiceClient = context.voice_client
            author_channel = author_voice.channel

            # Connect to the author's voice channel if the bot is not connected
            if not voice:
                voice = await author_channel.connect(self_deaf=True)
            # Move the bot to the correct channel if needed
            elif voice.channel != author_channel:
                await voice.move_to(author_channel)
                await voice.guild.change_voice_state(channel=author_channel, self_deaf=True)
        else:
            # Raise an exception if the user is no longer in a voice channel
            raise Exception("The user is no longer connected to the voice channel.")

        # Start playing the track and schedule the next song when playback ends
        voice.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(bot, context), bot.loop))

        # Update the currently playing song data
        new_song = {
            "title": info["title"],
            "url": info["webpage_url"],
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
            "view_count": info.get("view_count"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "context": context
        }
        data["playing"] = new_song

        # Set player state to "playing"
        data["player_state"] = 1

        # Create an embed for playback information
        embed = get_embed(new_song, 2)

        # Send or update the message with the playback embed
        if message:
            await message.edit(embed=embed)
        else:
            await context.send(embed=embed)
    except Exception as err:
        # Handle playback errors

        # Reset player state to idle
        data["player_state"] = 0

        # Disconnect the bot if an error occurs
        voice: discord.VoiceClient = context.voice_client
        if voice:
            await voice.disconnect()

        # Create an error embed
        embed = get_base_embed("❌ Error while playing audio")
        embed.description = str(err)

        # Send or update the message with the error embed
        if message:
            await message.edit(embed=embed)
        else:
            await context.send(embed=embed)
