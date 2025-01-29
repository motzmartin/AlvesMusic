import os
from dotenv import load_dotenv
from alvesmusic import AlvesMusic

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Le token Discord n'est pas défini dans le fichier \".env\"")

bot = AlvesMusic()

bot.run(TOKEN)
