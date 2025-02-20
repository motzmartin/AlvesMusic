import os
import asyncio
from dotenv import load_dotenv

from alvesmusic import AlvesMusic

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("The Discord token is not defined in the \".env\" file.")

async def main():
    async with AlvesMusic() as bot:
        await bot.start(TOKEN)

asyncio.run(main())
