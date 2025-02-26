from discord.ext import commands

from utils import get_base_embed
from alvesmusic import AlvesMusic

class Help(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        embed = get_base_embed("💡 Available Commands")

        embed.add_field(name="**!play <search|url>**", value="Plays a song/playlist or adds it to the queue.", inline=False)
        embed.add_field(name="**!skip [number]**", value="Skips the current song, or all songs up to the specified one if a number is provided.", inline=False)

        embed.add_field(name="**!queue [page]**", value="Displays the current queue, or a specific page.", inline=False)
        embed.add_field(name="**!remove <index>**", value="Removes the song at the specified index from the queue.", inline=False)
        embed.add_field(name="**!clear**", value="Clears the queue.", inline=False)
        embed.add_field(name="**!shuffle**", value="Randomly shuffles the order of songs in the queue.", inline=False)

        embed.add_field(name="**!pause**", value="Pauses playback.", inline=False)
        embed.add_field(name="**!resume**", value="Resumes paused playback.", inline=False)
        embed.add_field(name="**!stop**", value="Clears the queue and disconnects the bot.", inline=False)

        embed.set_footer(text="🔗 Source code available on GitHub: https://github.com/motzmartin/AlvesMusic")

        await ctx.send(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Help(bot))
