import asyncio
import logging

import pyromod  # noqa: F401; preserves the original interactive bot.ask behavior
import pyrogram.utils
from pyrogram import Client, idle

from config import API_HASH, API_ID, BOT_TOKEN, STRING_SESSION
from plugins.cb_data import app as Client2
from integration import admin_session, commands  # noqa: F401; registers handlers
from integration.database import integration_db
from integration.source_monitor import SourceChannelMonitor

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999
logging.basicConfig(level=logging.INFO)

bot = Client(
    "Renamer",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root="plugins"),
)


async def main() -> None:
    monitor = SourceChannelMonitor(bot)
    await bot.start()
    if STRING_SESSION:
        await Client2.start()
    try:
        await monitor.start()
        await idle()
    finally:
        await monitor.stop()
        if STRING_SESSION and Client2.is_connected:
            await Client2.stop()
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
