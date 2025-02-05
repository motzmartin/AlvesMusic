import random
import discord
from discord.ext import commands
from millify import millify

from utils import timecode
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
        max_page = 1 if not queue else (len(queue) + 19) // 20

        if page >= 1 and page <= max_page:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")

            if queue:
                queue_list = ""
                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]
                    if song["title"] and song["url"]:
                        queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(timecode(song["duration"]))
                    queue_list += " *{}*\n".format(song["author"])

                embed.title = "📜 Queue - Page {}/{} ({} track".format(page, max_page, len(queue))
                if len(queue) > 1:
                    embed.title += "s"
                embed.title += ")"
                embed.description = queue_list
                embed.add_field(name="Total Duration", value=timecode(sum(song["duration"] for song in queue if song["duration"])))
            else:
                embed.title = "📭 Empty Queue"
                embed.description = "No music in the queue."

            await ctx.send(embed=embed)
        else:
            raise commands.BadArgument()

    @commands.command()
    async def playing(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        voice: discord.VoiceClient = ctx.voice_client
        data: dict = self.bot.data[ctx.guild.id]
        if voice and data["player_state"] == 1:
            song: dict = data["playing"]

            if voice.is_paused():
                embed.title = "⏸️ Paused"
            else:
                embed.title = "🔊 Now Playing"
            if song["title"] and song["url"]:
                embed.description = "[**{}**]({})".format(song["title"], song["url"])
            if song["channel"] and song["channel_url"]:
                embed.add_field(name="Channel", value="[{}]({})".format(song["channel"], song["channel_url"]))
            if song["view_count"]:
                embed.add_field(name="Views", value=millify(song["view_count"]))
            if song["duration"]:
                embed.add_field(name="Duration", value=timecode(song["duration"]))
            if song["thumbnail"]:
                embed.set_thumbnail(url=song["thumbnail"])
            embed.set_footer(text="Requested by {}".format(song["author"]), icon_url=song["avatar"])
        else:
            embed.title = "🔇 No Music Playing"
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
            if queue:
                queue.clear()

                embed.title = "🗑️ Queue Cleared"
                embed.description = "All songs have been removed from the queue."
            else:
                embed.title = "📭 Queue Already Empty"
                embed.description = "There are no songs in the queue."
        else:
            embed.title = "❌ Unable to Clear Queue"
            embed.description = "You must be in a voice channel to use this command."

        await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            queue: list[dict] = self.bot.data[ctx.guild.id]["queue"]
            if queue:
                random.shuffle(queue)

                embed.title = "🔀 Queue Shuffled"
                embed.description = "The order of the songs has been randomly shuffled!"
            else:
                embed.title = "❌ Unable to Shuffle"
                embed.description = "The queue is empty, add some songs before using **!shuffle**."
        else:
            embed.title = "❌ Unable to Shuffle"
            embed.description = "You must be in a voice channel to use this command."

        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            data: dict = self.bot.data[ctx.guild.id]
            if voice and data["player_state"] == 1:
                voice.stop()

                embed.title = "⏭️ Skipping Song"
                embed.description = "Playing the next song..."
            else:
                embed.title = "❌ Unable to Skip"
                embed.description = "There is no music currently playing."
        else:
            embed.title = "❌ Unable to Skip"
            embed.description = "You must be in a voice channel to use this command."

        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx: commands.Context):
        if ctx.author.voice:
            await ctx.invoke(self.clear)
            await ctx.invoke(self.skip)
        else:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Unable to Stop the Bot"
            embed.description = "You must be in a voice channel to use this command."

            await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            if voice and voice.is_playing():
                voice.pause()

                embed.title = "⏸️ Playback Paused"
                embed.description = "Use **!resume** to resume playback."
            else:
                embed.title = "❌ Unable to Pause"
                embed.description = "There is no music currently playing."
        else:
            embed.title = "❌ Unable to Pause"
            embed.description = "You must be in a voice channel to use this command."

        await ctx.send(embed=embed)

    @commands.command()
    async def resume(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        if ctx.author.voice:
            voice: discord.VoiceClient = ctx.voice_client
            if voice and voice.is_paused():
                voice.resume()

                embed.title = "▶️ Playback Resumed"
                embed.description = "The music resumes from where it was paused."
            else:
                embed.title = "❌ Unable to Resume"
                embed.description = "No music is currently paused."
        else:
            embed.title = "❌ Unable to Resume"
            embed.description = "You must be in a voice channel to use this command."

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(General(bot))
