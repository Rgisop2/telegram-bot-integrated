from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN
from integration.database import integration_db

_pending_thumbnail_source = None


def _is_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == ADMIN)


@Client.on_message(filters.private & filters.command("set"))
async def set_channels(client: Client, message: Message):
    if not _is_admin(message):
        return
    if len(message.command) != 3:
        return await message.reply("Usage: `/set SOURCE_CHANNEL_ID OUTPUT_CHANNEL_ID`")
    try:
        source_id, output_id = int(message.command[1]), int(message.command[2])
        await integration_db.set_channels(source_id, output_id)
        await message.reply(f"Saved source `{source_id}` and output `{output_id}` channel IDs.")
    except ValueError:
        await message.reply("Both channel IDs must be integers, normally beginning with `-100`.")


@Client.on_message(filters.private & filters.command("setusername"))
async def set_username(client: Client, message: Message):
    if not _is_admin(message):
        return
    if len(message.command) != 2:
        return await message.reply("Usage: `/setusername @example`")
    username = message.command[1]
    if not username.startswith("@") or len(username) < 2:
        return await message.reply("Username must look like `@example`.")
    await integration_db.set_username(username)
    await message.reply(f"Saved filename username replacement: `{username}`")


@Client.on_message(filters.private & filters.command("setthumb"))
async def set_thumbnail(client: Client, message: Message):
    global _pending_thumbnail_source
    if not _is_admin(message):
        return
    if len(message.command) != 2:
        return await message.reply("Usage: `/setthumb SOURCE_CHANNEL_ID`")
    try:
        _pending_thumbnail_source = int(message.command[1])
    except ValueError:
        return await message.reply("Source channel ID must be an integer.")
    await message.reply("Send the thumbnail photo now. It will be saved only for this source channel.")


@Client.on_message(filters.private & filters.photo)
async def receive_source_thumbnail(client: Client, message: Message):
    global _pending_thumbnail_source
    if not _is_admin(message) or _pending_thumbnail_source is None:
        return
    source_id = _pending_thumbnail_source
    _pending_thumbnail_source = None
    await integration_db.set_thumbnail(source_id, str(message.photo.file_id))
    await message.reply(f"Thumbnail saved for source channel `{source_id}`.")
