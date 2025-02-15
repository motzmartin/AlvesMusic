import os
from dotenv import load_dotenv

from alvesmusic import AlvesMusic

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("The Discord token is not defined in the \".env\" file.")

bot = AlvesMusic()

bot.run(TOKEN)
