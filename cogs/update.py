import discord
from discord.ext import commands, tasks

from utils import get_playing_embed
from alvesmusic import AlvesMusic

class Update(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

        self.update_loop.start()

    @tasks.loop(seconds=5)
    async def update_loop(self):
        for guild in self.bot.data:
            player = self.bot.data[guild]

            if player.update_playing_message and player.playing_message:
                embed = get_playing_embed(player)

                try:
                    await player.playing_message.edit(embed=embed)
                except discord.NotFound:
                    player.playing_message = None

    @update_loop.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot: AlvesMusic):
    await bot.add_cog(Update(bot))
