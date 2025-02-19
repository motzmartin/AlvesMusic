import discord
from discord.ext import commands

from utils import GuildData

class AlvesMusic(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)

        self.data: dict[int, GuildData] = {}
        self.help_command = None

    def get_data(self, guild_id: int) -> GuildData:
        if not guild_id in self.data:
            self.data[guild_id] = GuildData()

        return self.data[guild_id]

    async def setup_hook(self):
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.play")
        await self.load_extension("cogs.help")
