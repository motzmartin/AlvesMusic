import discord
from discord.ext import commands
from alvesmusic import AlvesMusic

class Help(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        embed = discord.Embed()
        embed.title = "💡 Commandes disponibles :"
        embed.color = discord.Color.from_str("#73BCFF")
        embed.add_field(name="**!play <recherche|url>**", value="Joue une musique/playlist ou l'ajoute à la file d'attente.", inline=False)
        embed.add_field(name="**!queue [page]**", value="Affiche la file d'attente actuelle.", inline=False)
        embed.add_field(name="**!playing**", value="Affiche la musique actuellement en lecture.", inline=False)
        embed.add_field(name="**!clear**", value="Vide la file d'attente.", inline=False)
        embed.add_field(name="**!shuffle**", value="Mélange aléatoirement l'ordre des chansons dans la file d'attente.", inline=False)
        embed.add_field(name="**!skip**", value="Passe à la musique suivante.", inline=False)
        embed.add_field(name="**!reset**", value="Tente une réinitialisation du bot.", inline=False)
        embed.add_field(name="**!pause**", value="Met la lecture en pause.", inline=False)
        embed.add_field(name="**!resume**", value="Reprend la lecture mise en pause.", inline=False)

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Help(bot))
