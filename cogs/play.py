import discord
from discord.ext import commands
from millify import millify

from alvesmusic import AlvesMusic
from utils import extract, to_timecode, voice_check, get_data
from player import play_song

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def play(self, ctx: commands.Context, *, query: str):
        # Sending the search embed

        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "🔍 Searching"
        embed.description = "Searching for **{}**, this may take a moment.".format(query)

        search_message = await ctx.send(embed=embed)

        # Searching for the track(s)

        data: dict = get_data(self.bot, ctx.guild.id)

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)
        except Exception as err:
            # Error during search

            voice: discord.VoiceClient = ctx.voice_client
            if voice and data["player_state"] == 0:
                await voice.disconnect()

            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Error during search"
            embed.description = str(err)

            return await search_message.edit(embed=embed)

        queue: list[dict] = data["queue"]

        if "entries" in info:
            # No, one, or multiple results

            if not info["entries"]:
                # No results, sending the informational embed
                # Example: !play unyoxhgikwdbplecfjqa

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "❌ No results"
                embed.description = "No results found for **{}**.".format(query)

                await search_message.edit(embed=embed)
            elif len(info["entries"]) == 1:
                # A single result (often from a search)
                # Example: !play calogero 1987

                first: dict = info["entries"][0]

                song = {
                    "title": first.get("title"),
                    "url": first.get("url"),
                    "duration": first.get("duration"),
                    "context": ctx
                }

                if data["player_state"] != 0:
                    # Adding to the queue

                    queue.append(song)

                    # Sending the informational embed

                    embed = discord.Embed()
                    embed.color = discord.Color.from_str("#73BCFF")
                    embed.title = "📌 Added to queue"
                    if first.get("title") and first.get("url"):
                        embed.description = "The song [**{}**]({}) has been added to the queue.".format(first["title"], first["url"])
                    if first.get("channel") and first.get("channel_url"):
                        embed.add_field(name="Channel", value="[{}]({})".format(first["channel"], first["channel_url"]))
                    if first.get("view_count"):
                        embed.add_field(name="Views", value=millify(first["view_count"]))
                    if first.get("duration"):
                        embed.add_field(name="Duration", value=to_timecode(first["duration"]))
                    if first.get("id"):
                        embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/{}/maxresdefault.webp".format(first["id"]))
                    embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                    await search_message.edit(embed=embed)
                else:
                    # Playing the track

                    await play_song(self.bot, song, search_message)
            else:
                # Multiple results (from a YouTube playlist/mix)
                # Example: !play https://www.youtube.com/playlist?list=PLdSUTU0oamrwC0PY7uUc0EJMKlWCiku43

                entries: list[dict] = info["entries"]

                # Adding the tracks

                songs = []
                for entry in entries:
                    songs.append({
                        "title": entry.get("title"),
                        "url": entry.get("url"),
                        "duration": entry.get("duration"),
                        "context": ctx
                    })

                queue.extend(songs)

                # Sending the informational embed

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "📌 Added to queue"
                if info.get("title") and info.get("webpage_url"):
                    embed.description = "The **{}** tracks from the playlist [**{}**]({}) have been added to the queue.".format(len(info["entries"]), info["title"], info["webpage_url"])
                if info.get("channel") and info.get("channel_url"):
                    embed.add_field(name="Channel", value="[{}]({})".format(info["channel"], info["channel_url"]))
                if info.get("view_count"):
                    embed.add_field(name="Views", value=millify(info["view_count"]))
                embed.add_field(name="Total Duration", value=to_timecode(sum(entry["duration"] for entry in entries if entry.get("duration"))))
                if entries[0].get("id"):
                    embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/{}/maxresdefault.webp".format(entries[0]["id"]))
                embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)

                # Play the first track if no song is currently playing

                if data["player_state"] == 0:
                    queue.remove(songs[0])
                    await play_song(self.bot, songs[0])
        else:
            # A single result (from a YouTube URL)
            # Example: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp

            song = {
                "title": info.get("title"),
                "url": info.get("webpage_url"),
                "duration": info.get("duration"),
                "context": ctx
            }

            if data["player_state"] != 0:
                # Adding to the queue

                queue.append(song)

                # Sending the informational embed

                embed = discord.Embed()
                embed.color = discord.Color.from_str("#73BCFF")
                embed.title = "📌 Added to queue"
                if info.get("title") and info.get("webpage_url"):
                    embed.description = "The song [**{}**]({}) has been added to the queue.".format(info["title"], info["webpage_url"])
                if info.get("channel") and info.get("channel_url"):
                    embed.add_field(name="Channel", value="[{}]({})".format(info["channel"], info["channel_url"]))
                if info.get("view_count"):
                    embed.add_field(name="Views", value=millify(info["view_count"]))
                if info.get("duration"):
                    embed.add_field(name="Duration", value=to_timecode(info["duration"]))
                if info.get("thumbnail"):
                    embed.set_thumbnail(url=info["thumbnail"])
                embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)

                await search_message.edit(embed=embed)
            else:
                # Playing the track

                await play_song(self.bot, song, search_message)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
