from discord.ext import commands

from utils import voice_check, get_base_embed, get_data, extract_query
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

        data: dict = get_data(self.bot, ctx.guild.id)
        queue: list[dict] = data["queue"]

        try:
            info = await self.bot.loop.run_in_executor(None, extract_query, query)

            if not info.get("extractor"):
                raise Exception("Error occurred during extraction. (1)")

            if info["extractor"] == "youtube:search":
                if info.get("entries"):
                    await process_generic(self.bot, ctx, message, data, queue, info, is_search=True)
                else:
                    raise Exception("No results found for **{}**.".format(query))

            elif info["extractor"] == "youtube:tab":
                await process_playlist(self.bot, ctx, message, data, queue, info)

            elif info["extractor"] == "youtube":
                await process_generic(self.bot, ctx, message, data, queue, info)

        except Exception as err:
            embed = get_base_embed("❌ Error during Search")
            embed.description = str(err)

            await message.edit(embed=embed)

async def setup(bot: AlvesMusic):
    await bot.add_cog(Play(bot))
