from discord.ext import commands

from utils import voice_check, get_base_embed, get_data, extract
from process_handlers import process_yt_search, process_yt_tab, process_yt
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

        data: dict = get_data(self.bot, ctx.guild.id)
        queue: list[dict] = data["queue"]

        try:
            info = await self.bot.loop.run_in_executor(None, extract, query)

            if not info.get("extractor"):
                raise Exception("Error occurred during extraction.")

            if info["extractor"] == "youtube:search":
                if info.get("entries"):
                    await process_yt_search(self.bot, ctx, info, data, queue, message)
                else:
                    raise Exception("No results found for **{}**.".format(query))

            elif info["extractor"] == "youtube:tab":
                await process_yt_tab(self.bot, ctx, info, data, queue, message)

            elif info["extractor"] == "youtube":
                await process_yt(self.bot, ctx, info, data, queue, message)

        except Exception as err:
            embed = get_base_embed("❌ Error during Search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
