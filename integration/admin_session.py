from pyrogram import Client, filters
from pyrogram.errors import (ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
                             PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid)
from pyrogram.types import Message

from config import ADMIN, API_HASH, API_ID
from integration.database import integration_db


@Client.on_message(filters.private & filters.command("logout"))
async def logout(client: Client, message: Message):
    if not message.from_user or message.from_user.id != ADMIN:
        return await message.reply("Only the configured admin can logout.")
    await integration_db.set_admin_session(None)
    await message.reply("Admin session cleared. Restart the bot to disable monitoring immediately.")


@Client.on_message(filters.private & filters.command("login"))
async def login(bot: Client, message: Message):
    if not message.from_user or message.from_user.id != ADMIN:
        return await message.reply("Only the configured admin can login.")
    if await integration_db.get_admin_session():
        return await message.reply("Admin is already logged in. Use `/logout` first to replace the session.")
    client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
    try:
        await client.connect()
        phone_msg = await bot.ask(message.from_user.id, "Send your phone number with country code, or /cancel.", timeout=600)
        if phone_msg.text == "/cancel":
            return await phone_msg.reply("Login cancelled.")
        sent_code = await client.send_code(phone_msg.text.strip())
        code_msg = await bot.ask(message.from_user.id, "Send the OTP separated by spaces, or /cancel.", timeout=600)
        if code_msg.text == "/cancel":
            return await code_msg.reply("Login cancelled.")
        try:
            await client.sign_in(phone_msg.text.strip(), sent_code.phone_code_hash, code_msg.text.replace(" ", ""))
        except SessionPasswordNeeded:
            password_msg = await bot.ask(message.from_user.id, "Send your two-step verification password, or /cancel.", timeout=600)
            if password_msg.text == "/cancel":
                return await password_msg.reply("Login cancelled.")
            await client.check_password(password_msg.text)
        session = await client.export_session_string()
        await integration_db.set_admin_session(session)
        await message.reply("Admin user session saved. Restart the bot or use the process supervisor to start source monitoring.")
    except (ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, PasswordHashInvalid) as exc:
        await message.reply(f"Login failed: `{exc}`")
    finally:
        if client.is_connected:
            await client.disconnect()
