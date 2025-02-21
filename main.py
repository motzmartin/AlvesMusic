import os
import asyncio
import logging
import logging.handlers
from dotenv import load_dotenv

from alvesmusic import AlvesMusic

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("The Discord token is not defined in the \".env\" file.")

async def main():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename="logs/discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,
        backupCount=5
    )

    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", datefmt, style="{")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    async with AlvesMusic() as bot:
        await bot.start(TOKEN)

asyncio.run(main())
