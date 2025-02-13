import discord
from discord.ext import commands

class AlvesMusic(commands.Bot):
    def __init__(self):
        """
        Initializes the AlvesMusic bot with default settings.
        """

        # Define bot intents (required for reading messages)
        intents = discord.Intents.default()
        intents.message_content = True # Allows the bot to read message content

        # Initialize the bot with command prefix "!" and specified intents
        super().__init__(command_prefix="!", intents=intents)

        self.data = {} # Dictionary to store guild-specific music data
        self.help_command = None # Disable the default help command

    async def setup_hook(self):
        """
        Asynchronously loads bot extensions (cogs) during startup.
        """

        # Load bot cogs (extensions) for handling different functionalities
        await self.load_extension("cogs.events") # Handles bot events
        await self.load_extension("cogs.general") # Handles general commands
        await self.load_extension("cogs.play") # Handles music playback
        await self.load_extension("cogs.help") # Custom help command
