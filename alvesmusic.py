import discord
from discord.ext import commands

class AlvesMusic(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.data = {}
        self.help_command = None

    async def setup_hook(self):
        """
        Asynchronously loads bot extensions (cogs) during startup.
        """
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.play")
        await self.load_extension("cogs.help")
