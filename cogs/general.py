import random
import discord
from discord.ext import commands

from utils import to_timecode, voice_check, get_data, get_embed, get_base_embed
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def skip(self, ctx: commands.Context):
        """
        Skips to the next song.
        """
        voice: discord.VoiceClient = ctx.voice_client
        data: dict = get_data(self.bot, ctx.guild.id)
        if voice and data["player_state"] == 1:
            voice.stop()
        else:
            embed = get_base_embed("❌ Unable to Skip")
            embed.description = "There is no music currently playing."

            await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        """
        Shows the currently playing song.
        """
        data: dict = get_data(self.bot, ctx.guild.id)
        if data["player_state"] == 1:
            embed = get_embed(data["playing"], 3)
        else:
            embed = get_base_embed("🔇 No Music Playing")
            embed.description = "There is no music currently playing."

        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        """
        Displays the current queue.
        """
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            max_page = (len(queue) + 19) // 20

            if page >= 1 and page <= max_page:
                queue_list = ""
                total_duration = 0
                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]

                    queue_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])
                    if song["duration"]:
                        queue_list += " ({})".format(to_timecode(song["duration"]))
                        total_duration += song["duration"]
                    context: commands.Context = song["context"]
                    if context.author:
                        queue_list += " - *{}*\n".format(context.author.name)

                embed = get_base_embed("📜 Queue - Page {}/{} ({} track{})".format(page, max_page, len(queue), "s" if len(queue) > 1 else ""))
                embed.description = queue_list

                if total_duration:
                    embed.add_field(name="Total Duration", value=to_timecode(total_duration))
            else:
                raise commands.BadArgument()
        else:
            embed = get_base_embed("📭 Empty Queue")
            embed.description = "No music in the queue."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def remove(self, ctx: commands.Context, index: int = 0):
        """
        Removes the song at the specified index from the queue.
        """
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]
        if queue:
            if index >= 1 and index <= len(queue):
                removed = queue.pop(index - 1)

                embed = get_base_embed("🗑️ Song removed")
                embed.description = "The song [**{}**]({})".format(removed["title"], removed["url"])
                if removed["duration"]:
                    embed.description += " ({})".format(to_timecode(removed["duration"]))
                embed.description += " has been removed from the queue."

                embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)
            else:
                raise commands.BadArgument()
        else:
            embed = get_base_embed("❌ Unable to Remove")
            embed.description = "The queue is empty, add some songs before using **!remove**."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def clear(self, ctx: commands.Context):
        """
        Clears the queue.
        """
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
        """
        Randomly shuffles the order of songs in the queue.
        """
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
    async def pause(self, ctx: commands.Context):
        """
        Pauses playback.
        """
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
        """
        Resumes paused playback.
        """
        voice: discord.VoiceClient = ctx.voice_client
        if voice and voice.is_paused():
            voice.resume()

            embed = get_base_embed("▶️ Playback Resumed")
            embed.description = "The music resumes from where it was paused."
        else:
            embed = get_base_embed("❌ Unable to Resume")
            embed.description = "No music is currently paused."

        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def stop(self, ctx: commands.Context):
        """
        Clears the queue and disconnects the bot.
        """
        await ctx.invoke(self.clear)
        await ctx.invoke(self.skip)

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """
    await bot.add_cog(General(bot))
