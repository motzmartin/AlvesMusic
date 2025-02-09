import random
import discord
from discord.ext import commands
from millify import millify

from utils import to_timecode, voice_check, get_data
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            max_page = (len(queue) + 19) // 20

            if page >= 1 and page <= max_page:
                queue_list = ""

                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]
                    context: commands.Context = song["context"]

                    if song["title"] and song["url"]:
                        queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(to_timecode(song["duration"]))
                    queue_list += " *{}*\n".format(context.author.name)

                embed.title = "📜 Queue - Page {}/{} ({} track{})".format(page, max_page, len(queue), "s" if len(queue) > 1 else "")
                embed.description = queue_list
                embed.add_field(name="Total Duration", value=to_timecode(sum(song["duration"] for song in queue if song["duration"])))
            else:
                raise commands.BadArgument()
        else:
            embed.title = "📭 Empty Queue"
            embed.description = "No music in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        voice: discord.VoiceClient = ctx.voice_client
        data: dict = get_data(self.bot, ctx.guild.id)
        if voice and data["player_state"] == 1:
            song: dict = data["playing"]
            context: commands.Context = song["context"]

            embed.title = "⏸️ Paused" if voice.is_paused() else "🔊 Now Playing"
            if song["title"] and song["url"]:
                embed.description = "[**{}**]({})".format(song["title"], song["url"])
            if song["channel"] and song["channel_url"]:
                embed.add_field(name="Channel", value="[{}]({})".format(song["channel"], song["channel_url"]))
            if song["view_count"]:
                embed.add_field(name="Views", value=millify(song["view_count"]))
            if song["duration"]:
                embed.add_field(name="Duration", value=to_timecode(song["duration"]))
            if song["thumbnail"]:
                embed.set_thumbnail(url=song["thumbnail"])
            embed.set_footer(text="Requested by {}".format(context.author.name), icon_url=context.author.avatar.url)
        else:
            embed.title = "🔇 No Music Playing"
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def clear(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            queue.clear()

            embed.title = "🗑️ Queue Cleared"
            embed.description = "All songs have been removed from the queue."
        else:
            embed.title = "📭 Queue Already Empty"
            embed.description = "There are no songs in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def shuffle(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            random.shuffle(queue)

            embed.title = "🔀 Queue Shuffled"
            embed.description = "The order of the songs has been randomly shuffled!"
        else:
            embed.title = "❌ Unable to Shuffle"
            embed.description = "The queue is empty, add some songs before using **!shuffle**."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def skip(self, ctx: commands.Context):
        voice: discord.VoiceClient = ctx.voice_client
        data: dict = get_data(self.bot, ctx.guild.id)
        if voice and data["player_state"] == 1:
            voice.stop()
        else:
            embed = discord.Embed()
            embed.color = discord.Color.from_str("#73BCFF")
            embed.title = "❌ Unable to Skip"
            embed.description = "There is no music currently playing."

            await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def stop(self, ctx: commands.Context):
        await ctx.invoke(self.clear)
        await ctx.invoke(self.skip)

    @commands.command()
    @voice_check()
    async def pause(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        voice: discord.VoiceClient = ctx.voice_client
        if voice and voice.is_playing():
            voice.pause()

            embed.title = "⏸️ Playback Paused"
            embed.description = "Use **!resume** to resume playback."
        else:
            embed.title = "❌ Unable to Pause"
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def resume(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")

        voice: discord.VoiceClient = ctx.voice_client
        if voice and voice.is_paused():
            voice.resume()

            embed.title = "▶️ Playback Resumed"
            embed.description = "The music resumes from where it was paused."
        else:
            embed.title = "❌ Unable to Resume"
            embed.description = "No music is currently paused."

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(General(bot))
