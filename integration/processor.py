import os
import re
import time
from pathlib import Path
from typing import Optional

from PIL import Image
from pyrogram import Client
from pyrogram.types import Message

from config import ADMIN
from helper.ffmpeg import add_metadata, fix_thumb, take_screen_shot
from helper.progress import progress_for_pyrogram, humanbytes
from helper.set import escape_invalid_curly_brackets
from helper.database import find_one, find
from integration.database import integration_db

DOWNLOAD_DIR = Path("downloads")
METADATA_DIR = Path("Metadata")
DOWNLOAD_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)


def replace_username(filename: str, username: str) -> str:
    if not username:
        return filename
    username = username if username.startswith("@") else f"@{username}"
    stem, ext = os.path.splitext(filename)
    replaced = re.sub(r"@[A-Za-z0-9_]+", username, stem, count=1)
    return replaced + ext


def _media(message: Message):
    return message.document or message.video or message.audio


def _filename(message: Message) -> str:
    media = _media(message)
    name = getattr(media, "file_name", None) or f"telegram_{message.id}"
    return name.replace("/", "_").replace("\\", "_")


async def _thumbnail_path(client: Client, source_channel_id: int, video_path: Optional[str]) -> Optional[str]:
    file_id = await integration_db.get_thumbnail(source_channel_id)
    if file_id:
        path = await client.download_media(file_id)
        if path:
            Image.open(path).convert("RGB").save(path, "JPEG")
            image = Image.open(path)
            image.thumbnail((320, 320))
            image.save(path, "JPEG")
            return path
    if video_path:
        try:
            screenshot = await take_screen_shot(video_path, str(DOWNLOAD_DIR), 1)
            _, _, fixed = await fix_thumb(screenshot)
            return fixed
        except Exception:
            return None
    return None


def _caption(filename: str, size: int) -> str:
    try:
        data = find(int(ADMIN))
        template = data[1] if data else None
    except Exception:
        template = None
    if template:
        try:
            return escape_invalid_curly_brackets(template, ["filename", "filesize"]).format(
                filename=filename, filesize=humanbytes(size)
            )
        except Exception:
            pass
    return f"**{filename}**"


async def process_source_message(session: Client, output_client: Client, message: Message, source_channel_id: int, output_channel_id: int) -> Message:
    """Process one source message using the existing Rename-Bot media helpers.

    This is an adapter for automatic intake. The original interactive callbacks in
    plugins/cb_data.py remain available and unchanged for normal user operation.
    """
    media = _media(message)
    if media is None:
        raise ValueError("unsupported media: expected document, video, or audio")

    username = await integration_db.get_username()
    original_name = _filename(message)
    target_name = replace_username(original_name, username)
    target_path = DOWNLOAD_DIR / target_name
    status = await session.send_message(output_channel_id, f"Processing `{original_name}`...")
    progress_started = time.time()
    downloaded = None
    thumb = None
    try:
        downloaded = await session.download_media(message, file_name=str(DOWNLOAD_DIR / f".incoming_{message.id}"), progress=progress_for_pyrogram, progress_args=("Downloading...", status, progress_started))
        if not downloaded:
            raise RuntimeError("download returned no path")
        os.replace(downloaded, target_path)

        # Preserve the existing Rename-Bot metadata setting when configured for the admin.
        metadata_enabled = False
        metadata_code = None
        try:
            data = find(int(ADMIN))
            metadata_enabled = bool(data and data[2])
            metadata_code = data[3] if data else None
        except Exception:
            pass
        upload_path = str(target_path)
        if metadata_enabled and metadata_code:
            metadata_path = METADATA_DIR / target_name
            await add_metadata(str(target_path), str(metadata_path), metadata_code, status)
            if metadata_path.exists():
                upload_path = str(metadata_path)

        kind = "document" if message.document else "video" if message.video else "audio"
        thumb = await _thumbnail_path(session, source_channel_id, upload_path if kind == "video" else None)
        caption = _caption(target_name, int(media.file_size or 0))
        kwargs = {"caption": caption}
        if thumb:
            kwargs["thumb"] = thumb
        if kind == "video":
            kwargs["video"] = upload_path
            if message.video.duration:
                kwargs["duration"] = message.video.duration
            sent = await output_client.send_video(output_channel_id, **kwargs)
        elif kind == "audio":
            kwargs["audio"] = upload_path
            sent = await output_client.send_audio(output_channel_id, **kwargs)
        else:
            kwargs["document"] = upload_path
            sent = await output_client.send_document(output_channel_id, **kwargs)
        await status.delete()
        return sent
    finally:
        for path in (downloaded, str(target_path), str(METADATA_DIR / target_name), thumb):
            if path:
                try:
                    os.remove(path)
                except FileNotFoundError:
                    pass
                except OSError:
                    pass
