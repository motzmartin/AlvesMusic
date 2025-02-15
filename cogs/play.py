from discord.ext import commands

from utils import voice_check, get_base_embed, get_data, extract, get_thumbnail_url, get_media_embed, get_inline_details
from player import play_song
from alvesmusic import AlvesMusic

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def play(self, ctx: commands.Context, *, query: str):
        embed = get_base_embed("🔍 Searching")
        embed.description = "Searching for **{}**, this may take a moment.".format(query)

        message = await ctx.send(embed=embed) 

        data: dict = get_data(self.bot, ctx.guild.id)
        queue: list[dict] = data["queue"]

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)

            if "entries" in info:
                if not info["entries"]:
                    # !play unyoxhgikwdbplecfjqa

                    raise Exception("No results found for **{}**.".format(query))
                elif len(info["entries"]) == 1:
                    # !play calogero 1987

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

                        embed = get_media_embed(song, 0)

                        await message.edit(embed=embed)
                    else:
                        await play_song(self.bot, song, message)
                else:
                    # !play https://www.youtube.com/playlist?list=PLdSUTU0oamrwC0PY7uUc0EJMKlWCiku43

                    if not info.get("title") or not info.get("webpage_url"):
                        raise Exception("Unable to extract the video title or URL.")

                    entries: list[dict] = info["entries"]

                    preview = ""
                    total_duration = 0
                    songs = []

                    for i in range(len(entries)):
                        if not entries[i].get("title") or not entries[i].get("url"):
                            raise Exception("Unable to extract the video title or URL.")

                        song = {
                            "title": entries[i]["title"],
                            "url": entries[i]["url"],
                            "duration": entries[i].get("duration"),
                            "context": ctx
                        }

                        if i < 5:
                            preview += "{}\n".format(get_inline_details(song, index=(i + 1), include_author=False))

                        if song["duration"]:
                            total_duration += song["duration"]

                        songs.append(song)

                    if len(songs) > 5:
                        preview += "**... ({} more)**".format(len(songs) - 5)

                    queue.extend(songs)

                    playlist = {
                        "title": info["title"],
                        "url": info["webpage_url"],
                        "count": len(songs),
                        "preview": preview,
                        "channel": info.get("channel"),
                        "channel_url": info.get("channel_url"),
                        "view_count": info.get("view_count"),
                        "duration": total_duration,
                        "thumbnail": get_thumbnail_url(entries[0].get("id")),
                        "context": ctx
                    }

                    embed = get_media_embed(playlist, 1)

                    await message.edit(embed=embed)

                    if data["player_state"] == 0:
                        queue.remove(songs[0])

                        await play_song(self.bot, songs[0])
            else:
                # !play https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp

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

                    embed = get_media_embed(song, 0)

                    await message.edit(embed=embed)
                else:
                    await play_song(self.bot, song, message)
        except Exception as err:
            embed = get_base_embed("❌ Error during Search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
