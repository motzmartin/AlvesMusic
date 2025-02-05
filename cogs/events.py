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

        activity = discord.Game(name="(*de la) musique.")
        await self.bot.change_presence(activity=activity)

        print("Connecté en tant que {}.".format(self.bot.user))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        embed = discord.Embed()
        embed.color = discord.Color.from_str("#73BCFF")
        embed.title = "❌ Une erreur est survenue"

        raise_error = False

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Cette commande nécessite un argument."
        elif isinstance(error, commands.BadArgument):
            embed.description = "L'argument fourni n'est pas valide."
        elif isinstance(error, commands.CommandNotFound):
            embed.description = "Cette commande n'existe pas. Essayez **!help** pour voir la liste des commandes."
        else:
            embed.description = "Une erreur inconnue est survenue."
            raise_error = True

        await ctx.send(embed=embed)

        if raise_error:
            raise error

async def setup(bot: AlvesMusic):
    await bot.add_cog(Events(bot))
