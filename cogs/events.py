import discord
from discord.ext import commands

from utils import get_base_embed
from alvesmusic import AlvesMusic

class Events(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game(name="{}help".format(self.bot.command_prefix))
        await self.bot.change_presence(activity=activity)

        print("Connected as {}.".format(self.bot.user))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        embed = get_base_embed("🚫 Denied")

        raise_error = False

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "This command requires an argument."
        elif isinstance(error, commands.BadArgument):
            embed.description = "The provided argument is not valid."
        elif isinstance(error, commands.CommandNotFound):
            embed.description = "This command does not exist. Try **!help** to see the list of commands."
        elif isinstance(error, commands.CheckFailure):
            embed.description = str(error)
        else:
            embed.description = "Contact the administrator for help."
            raise_error = True

        await ctx.send(embed=embed)

        if raise_error:
            raise error

async def setup(bot: AlvesMusic):
    await bot.add_cog(Events(bot))
