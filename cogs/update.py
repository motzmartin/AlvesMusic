from discord.ext import commands, tasks

from utils import edit_playing_embed
from alvesmusic import AlvesMusic

class Update(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

        self.update_loop.start()

    @tasks.loop(seconds=5)
    async def update_loop(self):
        for guild in self.bot.data:
            player = self.bot.data[guild]

            if player.update_playing_embed:
                await edit_playing_embed(player, 4)

    @update_loop.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot: AlvesMusic):
    await bot.add_cog(Update(bot))
