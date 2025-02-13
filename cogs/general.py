import random
import discord
from discord.ext import commands

from utils import to_timecode, voice_check, get_data, get_embed, get_base_embed
from alvesmusic import AlvesMusic

class General(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        """
        Initialize the General cog.
        """

        self.bot = bot

    @commands.command()
    @voice_check()
    async def skip(self, ctx: commands.Context, number: int = 0):
        """
        Skips to the next song, or a specified number of songs from the queue.
        """

        # Retrieve the bot's voice client and the guild's music data
        voice: discord.VoiceClient = ctx.voice_client
        data: dict = get_data(self.bot, ctx.guild.id)

        # Check if music is currently playing
        if voice and data["player_state"] == 1:
            # Retrieve the guild's queue
            queue: list[dict] = data["queue"]

            # Check if a skip number is provided
            if number:
                # Validate that the number is within the queue length
                if number >= 1 and number <= len(queue):
                    removed = []

                    # Remove the specified number of songs from the queue
                    for _ in range(number):
                        removed.append(queue.pop(0))

                    removed_list = ""
                    removed_duration = 0

                    # Format removed songs for the embed message
                    for i in range(len(removed)):
                        song: dict = removed[i]

                        # Format song details
                        removed_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])

                        # Add duration if available
                        if song["duration"]:
                            removed_list += " ({})".format(to_timecode(song["duration"]))
                            removed_duration += song["duration"]

                        # Add song requester information if available
                        context: commands.Context = song["context"]
                        if context.author:
                            removed_list += " *{}*".format(context.author.global_name)

                        removed_list += "\n"

                    # Create a success embed
                    embed = get_base_embed("⏭️ Skipped")
                    embed.description = "Skipped **{}** song{} from the queue :\n\n{}".format(number, "s" if number > 1 else "", removed_list)

                    # Add total skipped duration if available
                    if removed_duration:
                        embed.add_field(name="Total Skipped Duration", value=to_timecode(removed_duration))

                    # Send the success embed
                    await ctx.send(embed=embed)
                else:
                    # Raise an error if the number is invalid
                    raise commands.BadArgument()

            # Stop the current song and move to the next one
            voice.stop()
        else:
            # Send an error message if no music is playing
            embed = get_base_embed("❌ Unable to Skip")
            embed.description = "There is no music currently playing."

            await ctx.send(embed=embed)

    @commands.command()
    async def playing(self, ctx: commands.Context):
        """
        Shows the currently playing song.
        """

        # Retrieve the guild's music data
        data: dict = get_data(self.bot, ctx.guild.id)

        # Check if music is currently playing
        if data["player_state"] == 1:
            # Create an embed for the currently playing song
            embed = get_embed(data["playing"], 3)
        else:
            # Create an embed indicating no music is playing
            embed = get_base_embed("🔇 No Music Playing")
            embed.description = "There is no music currently playing."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx: commands.Context, page: int = 1):
        """
        Displays the current queue, or a specific page.
        """

        # Retrieve the guild's queue
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]

        # Check if the queue is not empty
        if queue:
            # Calculate the total number of pages (20 songs per page)
            max_page = (len(queue) + 19) // 20

            # Validate the requested page number
            if page >= 1 and page <= max_page:
                songs_list = ""
                total_duration = 0

                # Iterate over the songs in the requested page range
                for i in range((page - 1) * 20, min(page * 20, len(queue))):
                    song: dict = queue[i]

                    # Format song details
                    songs_list += "**{}.** [**{}**]({})".format(i + 1, song["title"], song["url"])

                    # Add song duration if available
                    if song["duration"]:
                        songs_list += " ({})".format(to_timecode(song["duration"]))
                        total_duration += song["duration"]

                    # Add the requester’s name if available
                    context: commands.Context = song["context"]
                    if context.author:
                        songs_list += " *{}*".format(context.author.global_name)

                    songs_list += "\n"

                # Create an embed for the queue
                embed = get_base_embed("📜 Queue - Page {}/{} ({} track{})".format(page, max_page, len(queue), "s" if len(queue) > 1 else ""))
                embed.description = songs_list

                # Add total duration of the displayed songs if available
                if total_duration:
                    embed.add_field(name="Total Duration", value=to_timecode(total_duration))
            else:
                # Raise an error if the page number is invalid
                raise commands.BadArgument()
        else:
            # Create an embed indicating the queue is empty
            embed = get_base_embed("📭 Empty Queue")
            embed.description = "No music in the queue."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def remove(self, ctx: commands.Context, index: int):
        """
        Removes the song at the specified index from the queue.
        """

        # Retrieve the guild's queue
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]

        # Check if the queue is not empty
        if queue:
            # Validate the index is within the queue range
            if index and index >= 1 and index <= len(queue):
                removed = queue.pop(index - 1)

                # Create an embed confirming the removal
                embed = get_base_embed("🗑️ Song removed")
                embed.description = "The song [**{}**]({})".format(removed["title"], removed["url"])

                # Add the song duration if available
                if removed["duration"]:
                    embed.description += " ({})".format(to_timecode(removed["duration"]))

                embed.description += " has been removed from the queue."

                # Add song requester information if available
                context: commands.Context = removed["context"]
                if context.author:
                    embed.set_footer(text="Song requested by {}".format(context.author.global_name), icon_url=context.author.avatar.url)
            else:
                # Raise an error if the index is invalid
                raise commands.BadArgument()
        else:
            # Create an error embed if the queue is empty
            embed = get_base_embed("❌ Unable to Remove")
            embed.description = "The queue is empty, add some songs before using **!remove**."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def clear(self, ctx: commands.Context):
        """
        Clears the queue.
        """

        # Retrieve the guild's queue
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]

        # Check if the queue is not empty
        if queue:
            # Remove all songs from the queue
            queue.clear()

            # Create an embed confirming the queue has been cleared
            embed = get_base_embed("🗑️ Queue Cleared")
            embed.description = "All songs have been removed from the queue."
        else:
            # Create an embed if the queue is already empty
            embed = get_base_embed("📭 Queue Already Empty")
            embed.description = "There are no songs in the queue."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def shuffle(self, ctx: commands.Context):
        """
        Randomly shuffles the order of songs in the queue.
        """

        # Retrieve the guild's queue
        queue: list[dict] = get_data(self.bot, ctx.guild.id)["queue"]

        # Check if the queue is not empty
        if queue:
            # Shuffle the order of songs in the queue
            random.shuffle(queue)

            # Create an embed confirming the shuffle
            embed = get_base_embed("🔀 Queue Shuffled")
            embed.description = "The order of the songs has been randomly shuffled!"
        else:
            # Create an error embed if the queue is empty
            embed = get_base_embed("❌ Unable to Shuffle")
            embed.description = "The queue is empty, add some songs before using **!shuffle**."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def pause(self, ctx: commands.Context):
        """
        Pauses playback.
        """

        # Retrieve the bot's voice client
        voice: discord.VoiceClient = ctx.voice_client

        # Check if the bot is in a voice channel and is currently playing music
        if voice and voice.is_playing():
            # Pause playback
            voice.pause()

            # Create an embed confirming the pause action
            embed = get_base_embed("⏸️ Playback Paused")
            embed.description = "Use **!resume** to resume playback."
        else:
            # Create an error embed if no music is playing
            embed = get_base_embed("❌ Unable to Pause")
            embed.description = "There is no music currently playing."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def resume(self, ctx: commands.Context):
        """
        Resumes paused playback.
        """

        # Retrieve the bot's voice client
        voice: discord.VoiceClient = ctx.voice_client

        # Check if the bot is in a voice channel and the music is paused
        if voice and voice.is_paused():
            # Resume playback
            voice.resume()

            # Create an embed confirming the resume action
            embed = get_base_embed("▶️ Playback Resumed")
            embed.description = "The music resumes from where it was paused."
        else:
            # Create an error embed if no music is paused
            embed = get_base_embed("❌ Unable to Resume")
            embed.description = "No music is currently paused."

        # Send the embed message
        await ctx.send(embed=embed)

    @commands.command()
    @voice_check()
    async def stop(self, ctx: commands.Context):
        """
        Clears the queue and disconnects the bot.
        """

        # Invoke the clear command to remove all songs from the queue
        await ctx.invoke(self.clear)

        # Invoke the skip command to stop playback and disconnect
        await ctx.invoke(self.skip)

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """

    # Add the General cog to the bot
    await bot.add_cog(General(bot))
