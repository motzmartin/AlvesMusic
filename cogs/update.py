import discord
from discord.ext import commands, tasks

from utils import get_base_embed, get_media_embed
from alvesmusic import AlvesMusic

class Update(commands.Cog):
    def __init__(self, bot: AlvesMusic):
        self.bot = bot

        self.update_loop.start()

    @tasks.loop(seconds=5)
    async def update_loop(self):
        for guild in self.bot.data:
            data = self.bot.data[guild]

            if data.playing_message:
                if data.is_playing():
                    embed = get_media_embed(data.playing, 4, data=data)
                else:
                    embed = get_base_embed("🔇 No Music Playing")

                    embed.description = "There is no music currently playing."
                    embed.set_footer(text="This embed is dynamic, add a song!")

                try:
                    await data.playing_message.edit(embed=embed)
                except discord.NotFound:
                    data.playing_message = None

    @update_loop.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot: AlvesMusic):
    await bot.add_cog(Update(bot))
