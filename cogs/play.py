from discord.ext import commands

from alvesmusic import AlvesMusic
from utils import extract, voice_check, get_data, get_embed, get_base_embed, get_thumbnail_url
from player import play_song

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def play(self, ctx: commands.Context, *, query: str):
        """
        Plays a song/playlist or adds it to the queue.
        """
        # Sending the search embed

        embed = get_base_embed("🔍 Searching")
        embed.description = "Searching for **{}**, this may take a moment.".format(query)
        message = await ctx.send(embed=embed)

        # Searching for the track(s)

        data: dict = get_data(self.bot, ctx.guild.id)
        queue: list[dict] = data["queue"]

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)

            if "entries" in info:
                # No, one, or multiple results

                if not info["entries"]:
                    # No results, raising an error
                    # Example: !play unyoxhgikwdbplecfjqa

                    raise Exception("No results found for **{}**.".format(query))
                elif len(info["entries"]) == 1:
                    # A single result (often from a search)
                    # Example: !play calogero 1987

                    first: dict = info["entries"][0]

                    if not first.get("title") or not first.get("url"):
                        raise Exception("Unable to extract the video title or URL.")

                    song = {
                        "title": first["title"],
                        "url": first["url"],
                        "duration": first.get("duration"),
                        "context": ctx
                    }

                    if data["player_state"] != 0:
                        queue.append(song.copy())

                        song["channel"] = first.get("channel")
                        song["channel_url"] = first.get("channel_url")
                        song["view_count"] = first.get("view_count")
                        song["thumbnail"] = get_thumbnail_url(first.get("id"))

                        embed = get_embed(song, 0)
                        await message.edit(embed=embed)
                    else:
                        await play_song(self.bot, song, message)
                else:
                    # Multiple results (from a YouTube playlist/mix)
                    # Example: !play https://www.youtube.com/playlist?list=PLdSUTU0oamrwC0PY7uUc0EJMKlWCiku43

                    if not info.get("title") or not info.get("webpage_url"):
                        raise Exception("Unable to extract the video title or URL.")

                    entries: list[dict] = info["entries"]

                    songs = []
                    total_duration = 0
                    for entry in entries:
                        if not entry.get("title") or not entry.get("url"):
                            raise Exception("Unable to extract the video title or URL.")

                        song = {
                            "title": entry["title"],
                            "url": entry["url"],
                            "duration": entry.get("duration"),
                            "context": ctx
                        }

                        if song["duration"]:
                            total_duration += song["duration"]

                        songs.append(song)

                    queue.extend(songs)

                    playlist = {
                        "title": info["title"],
                        "url": info["webpage_url"],
                        "count": len(entries),
                        "channel": info.get("channel"),
                        "channel_url": info.get("channel_url"),
                        "view_count": info.get("view_count"),
                        "duration": total_duration,
                        "thumbnail": get_thumbnail_url(entries[0].get("id")),
                        "context": ctx
                    }

                    embed = get_embed(playlist, 1)
                    await message.edit(embed=embed)

                    if data["player_state"] == 0:
                        queue.remove(songs[0])
                        await play_song(self.bot, songs[0])
            else:
                # A single result (from a YouTube URL)
                # Example: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp

                if not info.get("title") or not info.get("webpage_url"):
                    raise Exception("Unable to extract the video title or URL.")

                song = {
                    "title": info["title"],
                    "url": info["webpage_url"],
                    "duration": info.get("duration"),
                    "context": ctx
                }

                if data["player_state"] != 0:
                    queue.append(song.copy())

                    song["channel"] = info.get("channel")
                    song["channel_url"] = info.get("channel_url")
                    song["view_count"] = info.get("view_count")
                    song["thumbnail"] = info.get("thumbnail")

                    embed = get_embed(song, 0)
                    await message.edit(embed=embed)
                else:
                    await play_song(self.bot, song, message)
        except Exception as err:
            # Error during search

            embed = get_base_embed("❌ Error during search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """
    await bot.add_cog(Play(bot))
