from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from config import DATABASE_NAME, DATABASE_URL


class IntegrationDatabase:
    """MongoDB storage for the automatic source-channel workflow.

    The original Rename-Bot user collection remains owned by helper/database.py.
    These collections are additive and keep integration state isolated.
    """

    def __init__(self):
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL (or DB_URI) is required")
        self.client = AsyncIOMotorClient(DATABASE_URL)
        self.db = self.client[DATABASE_NAME]
        self.settings = self.db.integration_settings
        self.thumbnails = self.db.source_thumbnails
        self.processed = self.db.processed_messages
        self.admin_sessions = self.db.admin_session

    async def get_settings(self) -> dict:
        doc = await self.settings.find_one({"_id": "workflow"})
        return doc or {"_id": "workflow", "source_channel_id": None, "output_channel_id": None, "username": ""}

    async def set_channels(self, source_channel_id: int, output_channel_id: int) -> None:
        await self.settings.update_one(
            {"_id": "workflow"},
            {"$set": {"source_channel_id": source_channel_id, "output_channel_id": output_channel_id}},
            upsert=True,
        )

    async def set_username(self, username: str) -> None:
        await self.settings.update_one(
            {"_id": "workflow"}, {"$set": {"username": username}}, upsert=True
        )

    async def get_username(self) -> str:
        return (await self.get_settings()).get("username", "")

    async def set_thumbnail(self, source_channel_id: int, file_id: str) -> None:
        await self.thumbnails.update_one(
            {"source_channel_id": source_channel_id},
            {"$set": {"file_id": file_id, "updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

    async def get_thumbnail(self, source_channel_id: int) -> Optional[str]:
        doc = await self.thumbnails.find_one({"source_channel_id": source_channel_id})
        return doc.get("file_id") if doc else None

    async def set_admin_session(self, session: Optional[str]) -> None:
        await self.admin_sessions.update_one(
            {"_id": "admin"}, {"$set": {"session": session}}, upsert=True
        )

    async def get_admin_session(self) -> Optional[str]:
        doc = await self.admin_sessions.find_one({"_id": "admin"})
        return doc.get("session") if doc else None

    async def claim_message(self, source_channel_id: int, source_message_id: int) -> bool:
        """Atomically claim a message; returns False if already claimed/processed."""
        result = await self.processed.update_one(
            {"source_channel_id": source_channel_id, "source_message_id": source_message_id},
            {"$setOnInsert": {
                "source_channel_id": source_channel_id,
                "source_message_id": source_message_id,
                "status": "processing",
                "output_message_id": None,
                "created_at": datetime.now(timezone.utc),
            }},
            upsert=True,
        )
        return result.upserted_id is not None

    async def update_processing(self, source_channel_id: int, source_message_id: int, status: str, output_message_id: Optional[int] = None, error: Optional[str] = None) -> None:
        update = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if output_message_id is not None:
            update["output_message_id"] = output_message_id
        if error:
            update["error"] = error[-4000:]
        await self.processed.update_one(
            {"source_channel_id": source_channel_id, "source_message_id": source_message_id},
            {"$set": update},
            upsert=True,
        )


integration_db = IntegrationDatabase()
