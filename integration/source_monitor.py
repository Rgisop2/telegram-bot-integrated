import asyncio
import logging
from typing import Optional

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.errors import FloodWait

from config import API_HASH, API_ID, MAX_RETRY_ATTEMPTS, PROCESSING_WORKERS
from integration.database import integration_db
from integration.processor import process_source_message

logger = logging.getLogger(__name__)


class SourceChannelMonitor:
    def __init__(self, bot: Client):
        self.bot = bot
        self.user: Optional[Client] = None
        self._lock = asyncio.Semaphore(PROCESSING_WORKERS)

    async def start(self) -> None:
        session = await integration_db.get_admin_session()
        if not session:
            logger.warning("No persisted admin session; source monitoring is disabled until /login is completed")
            return
        self.user = Client("integration_admin", api_id=API_ID, api_hash=API_HASH, session_string=session)
        await self.user.start()
        self.user.add_handler(
            MessageHandler(
                self._on_message, filters.channel & (filters.document | filters.video | filters.audio)
            )
        )
        logger.info("Source-channel monitor started with the persisted admin session")

    async def stop(self) -> None:
        if self.user and self.user.is_connected:
            await self.user.stop()
        self.user = None

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    async def _on_message(self, _client: Client, message) -> None:
        settings = await integration_db.get_settings()
        source_id = settings.get("source_channel_id")
        output_id = settings.get("output_channel_id")
        if not source_id or not output_id or message.chat.id != source_id:
            return
        if not await integration_db.claim_message(source_id, message.id):
            logger.info("Skipping duplicate source message %s/%s", source_id, message.id)
            return
        async with self._lock:
            try:
                sent = None
                for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
                    try:
                        sent = await process_source_message(self.user, self.user, message, source_id, output_id)
                        break
                    except FloodWait as exc:
                        await asyncio.sleep(exc.value)
                    except Exception:
                        if attempt >= MAX_RETRY_ATTEMPTS:
                            raise
                        await asyncio.sleep(min(2 ** attempt, 30))
                await integration_db.update_processing(source_id, message.id, "completed", sent.id if sent else None)
            except Exception as exc:
                logger.exception("Source message %s failed", message.id)
                await integration_db.update_processing(source_id, message.id, "failed", error=str(exc))
