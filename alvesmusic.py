from discord.ext import commands

from utils import GuildData

class AlvesMusic(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data: dict[int, GuildData] = {}
        self.help_command = None

    def get_data(self, guild_id: int):
        if not guild_id in self.data:
            self.data[guild_id] = GuildData()

        return self.data[guild_id]

    async def setup_hook(self):
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.play")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.update")
