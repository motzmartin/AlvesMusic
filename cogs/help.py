from discord.ext import commands

from utils import get_base_embed
from alvesmusic import AlvesMusic

class Help(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        """
        Initialize the Help cog.
        """

        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """
        Send the help menu (embed).
        """

        # Create an embed for the help menu
        embed = get_base_embed("💡 Available Commands")

        # Add commands related to playback
        embed.add_field(name="**!play <search|url>**", value="Plays a song/playlist or adds it to the queue.", inline=False)
        embed.add_field(name="**!skip [number]**", value="Skips to the next song, or a specified number of songs from the queue.", inline=False)
        embed.add_field(name="**!playing**", value="Shows the currently playing song.", inline=False)

        # Add commands related to queue management
        embed.add_field(name="**!queue [page]**", value="Displays the current queue, or a specific page.", inline=False)
        embed.add_field(name="**!remove <index>**", value="Removes the song at the specified index from the queue.", inline=False)
        embed.add_field(name="**!clear**", value="Clears the queue.", inline=False)
        embed.add_field(name="**!shuffle**", value="Randomly shuffles the order of songs in the queue.", inline=False)

        # Add playback control commands
        embed.add_field(name="**!pause**", value="Pauses playback.", inline=False)
        embed.add_field(name="**!resume**", value="Resumes paused playback.", inline=False)
        embed.add_field(name="**!stop**", value="Clears the queue and disconnects the bot.", inline=False)

        # Add footer with GitHub source link
        embed.set_footer(text="🔗 Source code available on GitHub: https://github.com/motzmartin/AlvesMusic")

        # Send the embed message
        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """

    # Add the Help cog to the bot
    await bot.add_cog(Help(bot))
