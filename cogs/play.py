from discord.ext import commands

from utils import *
from player import *
from alvesmusic import AlvesMusic

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        """
        Initialize the Play cog.
        """

        self.bot = bot

    @commands.command()
    @voice_check()
    async def play(self, ctx: commands.Context, *, query: str):
        """
        Plays a song/playlist or adds it to the queue.
        """

        # Send the search embed
        embed = get_base_embed("🔍 Searching")
        embed.description = "Searching for **{}**, this may take a moment.".format(query)

        message = await ctx.send(embed=embed) 

        # Retrieve the guild's music data and queue
        data: dict = get_data(self.bot, ctx.guild.id)
        queue: list[dict] = data["queue"]

        try:
            # Extract track(s) from the search query
            info = await self.bot.loop.run_in_executor(None, extract, query)

            if "entries" in info:
                # Handle cases where multiple or no results are returned

                if not info["entries"]:
                    # No results found
                    # Example: !play unyoxhgikwdbplecfjqa

                    raise Exception("No results found for **{}**.".format(query))
                elif len(info["entries"]) == 1:
                    # A single result (often from a search)
                    # Example: !play calogero 1987

                    first: dict = info["entries"][0]

                    # Ensure essential data is available
                    if not first.get("title") or not first.get("url"):
                        raise Exception("Unable to extract the video title or URL.")

                    # Create song dictionary
                    song = {
                        "title": first["title"],
                        "url": first["url"],
                        "duration": first.get("duration"),
                        "context": ctx
                    }

                    if data["player_state"] != 0:
                        # Add the song to the queue if music is already playing
                        queue.append(song.copy())

                        # Add additional song details for the embed
                        song["channel"] = first.get("channel")
                        song["channel_url"] = first.get("channel_url")
                        song["view_count"] = first.get("view_count")
                        song["thumbnail"] = get_thumbnail_url(first.get("id"))

                        embed = get_media_embed(song, 0)

                        await message.edit(embed=embed)
                    else:
                        # Play the song immediately if no music is currently playing
                        await play_song(self.bot, song, message)
                else:
                    # Multiple results (from a YouTube playlist/mix)
                    # Example: !play https://www.youtube.com/playlist?list=PLdSUTU0oamrwC0PY7uUc0EJMKlWCiku43

                    # Ensure essential data is available
                    if not info.get("title") or not info.get("webpage_url"):
                        raise Exception("Unable to extract the video title or URL.")

                    entries: list[dict] = info["entries"]

                    preview = ""
                    songs = []

                    # Process all entries in the playlist
                    for i in range(len(entries)):
                        if not entries[i].get("title") or not entries[i].get("url"):
                            raise Exception("Unable to extract the video title or URL.")

                        song = {
                            "title": entries[i]["title"],
                            "url": entries[i]["url"],
                            "duration": entries[i].get("duration"),
                            "context": ctx
                        }

                        if i < 3:
                            preview += "{}\n".format(get_inline_details(song, author=False))

                        songs.append(song)

                    if len(songs) > 3:
                        preview += "**... ({} more)**".format(len(songs) - 3)

                    # Add all songs to the queue
                    queue.extend(songs)

                    # Create playlist metadata for the embed
                    playlist = {
                        "title": info["title"],
                        "url": info["webpage_url"],
                        "count": len(songs),
                        "preview": preview,
                        "channel": info.get("channel"),
                        "channel_url": info.get("channel_url"),
                        "view_count": info.get("view_count"),
                        "duration": sum(s["duration"] for s in songs if s["duration"]),
                        "thumbnail": get_thumbnail_url(entries[0].get("id")),
                        "context": ctx
                    }

                    embed = get_media_embed(playlist, 1)

                    await message.edit(embed=embed)

                    # Start playback if nothing is currently playing
                    if data["player_state"] == 0:
                        queue.remove(songs[0])

                        await play_song(self.bot, songs[0])
            else:
                # A single result (from a YouTube URL)
                # Example: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp

                # Ensure essential data is available
                if not info.get("title") or not info.get("webpage_url"):
                    raise Exception("Unable to extract the video title or URL.")

                # Create song dictionary
                song = {
                    "title": info["title"],
                    "url": info["webpage_url"],
                    "duration": info.get("duration"),
                    "context": ctx
                }

                if data["player_state"] != 0:
                    # Add the song to the queue if music is already playing
                    queue.append(song.copy())

                    # Add additional song details for the embed
                    song["channel"] = info.get("channel")
                    song["channel_url"] = info.get("channel_url")
                    song["view_count"] = info.get("view_count")
                    song["thumbnail"] = info.get("thumbnail")

                    embed = get_media_embed(song, 0)

                    await message.edit(embed=embed)
                else:
                    # Play the song immediately if no music is currently playing
                    await play_song(self.bot, song, message)
        except Exception as err:
            # Handle errors during the search process
            embed = get_base_embed("❌ Error during search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """

    # Add the Play cog to the bot
    await bot.add_cog(Play(bot))
