import random
import time
import discord
from discord.ext import commands

from utils import to_timecode, voice_check, get_inline_details, get_base_embed, get_media_embed
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def skip(self, ctx: commands.Context, number: int = 1):
        data = self.bot.get_data(ctx.guild.id)

        if data.is_playing():
            if number != 1:
                if number > 1 and number <= len(data.queue):
                    skipped_duration = 0

                    embed = get_base_embed("⏭️ Skipped")
                    embed.description = "Skipped the **current song** and the next **{}** song{} in the queue.\n\n**Currently playing**\n".format(number - 1, "s" if number > 2 else "")

                    embed.description += "{}\n\n**Queue**\n".format(get_inline_details(data.playing))

                    for i in range(number - 1):
                        song = data.queue.pop(0)

                        if i < 10:
                            embed.description += "{}\n".format(get_inline_details(song, index=(i + 1)))

                        if song["duration"]:
                            skipped_duration += song["duration"]

                    if number > 11:
                        embed.description += "**... ({} more)**".format(number - 11)

                    if skipped_duration:
                        embed.add_field(name="Total Skipped Duration", value=to_timecode(skipped_duration))

                    await ctx.send(embed=embed)
                else:
                    raise commands.BadArgument()
            else:
                embed = get_base_embed("⏭️ Skipped")
                embed.description = "Skipped {}".format(get_inline_details(data.playing))

                await ctx.send(embed=embed)

            voice: discord.VoiceClient = ctx.voice_client

            if voice:
                voice.stop()
        else:
            embed = get_base_embed("❌ Unable to Skip")
            embed.description = "There is no music currently playing."

            await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        data = self.bot.get_data(ctx.guild.id)

        if data.is_playing():
            embed = get_media_embed(data.playing, 4, data=data)
        else:
            embed = get_base_embed("🔇 No Music Playing")

            embed.description = "There is no music currently playing."
            embed.set_footer(text="This embed is dynamic, add a song!")

        data.playing_message = await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        data = self.bot.get_data(ctx.guild.id)

        if data.queue:
            max_page = (len(data.queue) + 9) // 10

            if page > 0 and page <= max_page:
                embed = get_base_embed("📜 Current Queue")
                embed.description = ""

                for i in range((page - 1) * 10, min(page * 10, len(data.queue))):
                    embed.description += "{}\n".format(get_inline_details(data.queue[i], index=(i + 1)))

                remaining = len(data.queue) - page * 10

                if remaining > 0:
                    embed.description += "**... ({} more)**".format(remaining)

                total_duration = sum(song["duration"] for song in data.queue if song["duration"])

                if total_duration:
                    embed.add_field(name="Total Duration", value=to_timecode(total_duration))

                embed.set_footer(text="Page {}/{} ({} track{})".format(page, max_page, len(data.queue), "s" if len(data.queue) > 1 else ""))
            else:
                raise commands.BadArgument()
        else:
            embed = get_base_embed("📭 Empty Queue")
            embed.description = "No music in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def remove(self, ctx: commands.Context, index: int):
        data = self.bot.get_data(ctx.guild.id)

        if data.queue:
            if index and index > 0 and index <= len(data.queue):
                removed = data.queue.pop(index - 1)

                embed = get_base_embed("🗑️ Song Removed")
                embed.description = "One song has been removed from the queue.\n\n{}".format(get_inline_details(removed, index=index))
            else:
                raise commands.BadArgument()
        else:
            embed = get_base_embed("❌ Unable to Remove")
            embed.description = "The queue is empty, add some songs before using **!remove**."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def clear(self, ctx: commands.Context):
        data = self.bot.get_data(ctx.guild.id)

        if data.queue:
            data.queue.clear()

            embed = get_base_embed("🗑️ Queue Cleared")
            embed.description = "All songs have been removed from the queue."
        else:
            embed = get_base_embed("📭 Queue Already Empty")
            embed.description = "There are no songs in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def shuffle(self, ctx: commands.Context):
        data = self.bot.get_data(ctx.guild.id)

        if data.queue:
            random.shuffle(data.queue)

            embed = get_base_embed("🔀 Queue Shuffled")
            embed.description = "The order of the songs has been randomly shuffled!"
        else:
            embed = get_base_embed("❌ Unable to Shuffle")
            embed.description = "The queue is empty, add some songs before using **!shuffle**."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def pause(self, ctx: commands.Context):
        data = self.bot.get_data(ctx.guild.id)
        voice: discord.VoiceClient = ctx.voice_client

        if voice and voice.is_playing():
            voice.pause()

            data.is_paused = True
            data.paused_at = time.time()

            embed = get_base_embed("⏸️ Playback Paused")
            embed.description = "Use **!resume** to resume playback."
        else:
            embed = get_base_embed("❌ Unable to Pause")
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def resume(self, ctx: commands.Context):
        data = self.bot.get_data(ctx.guild.id)
        voice: discord.VoiceClient = ctx.voice_client

        if voice and voice.is_paused():
            voice.resume()

            data.is_paused = False
            data.paused_time += time.time() - data.paused_at

            embed = get_base_embed("▶️ Playback Resumed")
            embed.description = "The music resumes from where it was paused."
        else:
            embed = get_base_embed("❌ Unable to Resume")
            embed.description = "No music is currently paused."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def stop(self, ctx: commands.Context):
        await ctx.invoke(self.clear)
        await ctx.invoke(self.skip)

async def setup(bot: AlvesMusic):
    await bot.add_cog(General(bot))
