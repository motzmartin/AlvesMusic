import discord
from discord.ext import commands

from alvesmusic import AlvesMusic

class Events(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            self.bot.data[guild.id] = {
                "queue": [],
                "player_state": 0,
                "playing": {}
            }

        activity = discord.Game(name="!help")
        await self.bot.change_presence(activity=activity)

        print("Connected as {}.".format(self.bot.user))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "❌ An error occurred"

        raise_error = False

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "This command requires an argument."
        elif isinstance(error, commands.BadArgument):
            embed.description = "The provided argument is not valid."
        elif isinstance(error, commands.CommandNotFound):
            embed.description = "This command does not exist. Try **!help** to see the list of commands."
        else:
            embed.description = "An unknown error occurred."
            raise_error = True

        await ctx.send(embed=embed)

        if raise_error:
            raise error

async def setup(bot: AlvesMusic):
    await bot.add_cog(Events(bot))
