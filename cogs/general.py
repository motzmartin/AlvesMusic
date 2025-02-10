import random
import discord
from discord.ext import commands

from utils import to_timecode, voice_check, get_data, get_embed, get_base_embed
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            max_page = (len(queue) + 19) // 20

            if page >= 1 and page <= max_page:
                queue_list = ""

                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]

                    queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(to_timecode(song["duration"]))
                    context: commands.Context = song["context"]
                    if context.author:
                        queue_list += " *{}*\n".format(context.author.name)

                embed = get_base_embed("📜 Queue - Page {}/{} ({} track{})".format(page, max_page, len(queue), "s" if len(queue) > 1 else ""))
                embed.description = queue_list

                embed.add_field(name="Total Duration", value=to_timecode(sum(song["duration"] for song in queue if song["duration"])))
            else:
                raise commands.BadArgument()
        else:
            embed = get_base_embed("📭 Empty Queue")
            embed.description = "No music in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        voice: discord.VoiceClient = ctx.voice_client
        data: dict = get_data(self.bot, ctx.guild.id)
        if voice and data["player_state"] == 1:
            embed = get_embed(data["playing"], 3, paused=voice.is_paused())
        else:
            embed = get_base_embed("🔇 No Music Playing")
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def clear(self, ctx: commands.Context):
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            queue.clear()

            embed = get_base_embed("🗑️ Queue Cleared")
            embed.description = "All songs have been removed from the queue."
        else:
            embed = get_base_embed("📭 Queue Already Empty")
            embed.description = "There are no songs in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def shuffle(self, ctx: commands.Context):
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            random.shuffle(queue)

            embed = get_base_embed("🔀 Queue Shuffled")
            embed.description = "The order of the songs has been randomly shuffled!"
        else:
            embed = get_base_embed("❌ Unable to Shuffle")
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
            embed = get_base_embed("❌ Unable to Skip")
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
        voice: discord.VoiceClient = ctx.voice_client
        if voice and voice.is_playing():
            voice.pause()

            embed = get_base_embed("⏸️ Playback Paused")
            embed.description = "Use **!resume** to resume playback."
        else:
            embed = get_base_embed("❌ Unable to Pause")
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def resume(self, ctx: commands.Context):
        voice: discord.VoiceClient = ctx.voice_client
        if voice and voice.is_paused():
            voice.resume()

            embed = get_base_embed("▶️ Playback Resumed")
            embed.description = "The music resumes from where it was paused."
        else:
            embed = get_base_embed("❌ Unable to Resume")
            embed.description = "No music is currently paused."

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(General(bot))
