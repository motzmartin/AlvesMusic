import os
from dotenv import load_dotenv

from alvesmusic import AlvesMusic

# Load environment variables from the .env file
load_dotenv()

# Retrieve the bot token from the environment variables
TOKEN = os.getenv("BOT_TOKEN")

# Ensure the bot token is defined
if not TOKEN:
    raise ValueError("The Discord token is not defined in the \".env\" file.")

# Initialize the bot instance
bot = AlvesMusic()

# Run the bot with the specified token
bot.run(TOKEN)
