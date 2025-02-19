from discord.ext import commands

from utils import extract_query, voice_check, get_base_embed
from query_handlers import process_generic, process_playlist
from alvesmusic import AlvesMusic

class Play(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

    @commands.command()
    @voice_check()
    async def play(self, ctx: commands.Context, *, query: str):
        embed = get_base_embed("🔍 Searching")
        embed.description = "Searching for **{}**, this may take a moment.".format(query)

        message = await ctx.send(embed=embed) 

        try:
            info = await self.bot.loop.run_in_executor(None, extract_query, query)

            if not info.get("extractor"):
                raise Exception("Cannot retrieve extractor.")

            if info["extractor"] in ["youtube:search", "youtube:tab"] and not info.get("entries"):
                raise Exception("No results found for **{}**.".format(query))

            match info["extractor"]:
                case "youtube:search":
                    await process_generic(self.bot, ctx, message, info["entries"][0], is_search=True)
                case "youtube:tab":
                    await process_playlist(self.bot, ctx, message, info)
                case "youtube":
                    await process_generic(self.bot, ctx, message, info)

        except Exception as err:
            embed = get_base_embed("❌ Error during Search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
