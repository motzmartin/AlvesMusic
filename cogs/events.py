import discord
from discord.ext import commands

from utils import *
from alvesmusic import AlvesMusic

class Events(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        """
        Initialize the Events cog.
        """

        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Triggered when the bot successfully connects to Discord and is ready.
        """

        # Ensure the bot is fully ready before proceeding
        await self.bot.wait_until_ready()

        # Set the bot's activity status
        activity = discord.Game(name="!help")
        await self.bot.change_presence(activity=activity)

        # Print confirmation to the console
        print("Connected as {}.".format(self.bot.user))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Handle errors triggered by command execution.
        """

        # Create a base embed for the error message
        embed = get_base_embed("❌ An error occurred")

        # Flag to determine whether to raise the error
        raise_error = False

        # Handle specific command errors
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "This command requires an argument."
        elif isinstance(error, commands.BadArgument):
            embed.description = "The provided argument is not valid."
        elif isinstance(error, commands.CommandNotFound):
            embed.description = "This command does not exist. Try **!help** to see the list of commands."
        elif isinstance(error, commands.CheckFailure):
            embed.description = str(error)
        else:
            # Generic error message for unhandled cases
            embed.description = "Contact the administrator for help."
            raise_error = True

        # Send the embed message
        await ctx.send(embed=embed)

        # Raise the error because it is not a known error
        if raise_error:
            raise error

async def setup(bot: AlvesMusic):
    """
    Load the cog into the bot.
    """

    # Add the Events cog to the bot
    await bot.add_cog(Events(bot))
