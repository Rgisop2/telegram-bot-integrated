import asyncio
import re
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    
    args = m.command
    if len(args) > 1 and args[1].startswith('generate_'):
        # User clicked on a shared link with specific link ID
        link_id = args[1].replace('generate_', '')
        await generate_fresh_link(c, m, link_id)
    else:
        # Regular start message
        await m.reply_photo(f"https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
            caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Link Generator Bot. I help you generate fresh join request links.\n\nShare my link with your users and they will get fresh links every time!</b>",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
                ],[
                    InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/Kingvj01'),
                    InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/VJ_Botz')
                ]]
            )
        )

@Client.on_message(filters.command('setlink') & filters.private)
async def set_link(client, message):
    try:
        # Extract link from command
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.reply("**Usage:** `/setlink https://t.me/Urban_Links_bot?start=req_xxxxx`")
        
        urban_link = args[1].strip()
        
        # Validate it's a Telegram URL
        if not urban_link.startswith('https://t.me/'):
            return await message.reply("**Invalid link format. Please provide a valid Telegram bot link.**")
        
        link_id = await db.add_urban_link(urban_link)
        
        # Generate bot's own shareable link with unique ID
        bot_me = await client.get_me()
        bot_link = f"https://t.me/{bot_me.username}?start=generate_{link_id}"
        
        await message.reply(
            f"**✅ Link has been saved successfully!**\n\n"
            f"**Use this link to share with users:**\n\n"
            f"`{bot_link}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"**Error:** {str(e)}")

@Client.on_message(filters.command('pub') & filters.private)
async def pub_command(client, message):
    try:
        args = message.command
        if len(args) < 2:
            return await message.reply("**Usage:** `/pub https://t.me/channel_username` or `/pub channel_username`")
        
        input_link = args[1].strip()
        
        # Normalize the link to a public username format or full t.me link
        if input_link.startswith('https://t.me/'):
            # Check if it's a private invite link (starts with + or joinchat)
            if '/+' in input_link or '/joinchat/' in input_link:
                return await message.reply("**❌ Only public Telegram channel links are allowed. Private links are rejected.**")
            channel_link = input_link
        else:
            # Handle username input
            username = input_link.replace('@', '')
            channel_link = f"https://t.me/{username}"

        # Final validation to ensure it's not a private link pattern
        if '/+' in channel_link or '/joinchat/' in channel_link:
            return await message.reply("**❌ Only public Telegram channel links are allowed. Private links are rejected.**")

        link_id = await db.add_urban_link(channel_link)
        bot_me = await client.get_me()
        bot_link = f"https://t.me/{bot_me.username}?start=generate_{link_id}"

        await message.reply(
            f"✅ **Link saved! Share this generated link with your users:**\n\n"
            f"`{bot_link}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"**Error:** {str(e)}")

async def generate_fresh_link(client, message, link_id):
    try:
        wait_msg = await message.reply("⏳ **Please wait...**")
        
        # Get stored Urban Links URL by ID
        urban_link = await db.get_urban_link_by_id(link_id)
        if not urban_link:
            return await wait_msg.edit_text("**The link configuration has expired or been removed.**")
        
        start_param_match = re.search(r'\?start=(.+)', urban_link)
        is_pub_link = start_param_match is None
        
        if is_pub_link:
            # For /pub links, we need to send the channel link to the configured Urban Bot
            # Try to find the target bot from other stored links, or use fallback
            all_links = await db.get_all_urban_links()
            target_bot = "Urban_Links_bot"
            for l_data in reversed(all_links):
                l = l_data['link']
                if "?start=" in l:
                    m = re.search(r'https://t\.me/(\w+)', l)
                    if m:
                        target_bot = m.group(1).lower()
                        break
            
            urban_bot_username = target_bot
            message_to_send = urban_link
            print(f"[v0] Handling /pub link. Sending channel link {urban_link} to bot {urban_bot_username}")
        else:
            bot_username_match = re.search(r'https://t\.me/(\w+)', urban_link)
            if not bot_username_match:
                return await wait_msg.edit_text("**Invalid link configuration.**")
            
            urban_bot_username = bot_username_match.group(1).lower()
            start_param = start_param_match.group(1)
            message_to_send = f"/start {start_param}"
            print(f"[v0] Handling /setlink. Sending /start {start_param} to bot {urban_bot_username}")
        
        admin_session = await db.get_admin_session()
        if admin_session is None:
            return await wait_msg.edit_text(
                "**Admin has not logged in yet. Please contact the bot administrator to complete setup.**\n\n"
                "Admin needs to use `/login` to authenticate."
            )
        
        uclient = None
        try:
            uclient = Client(":memory:", session_string=admin_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            
            try:
                await uclient.get_chat(urban_bot_username)
            except Exception as peer_err:
                print(f"[v0] Could not fetch peer {urban_bot_username}: {str(peer_err)}")
            
            # This ensures we only process messages that arrive AFTER our command
            last_msg_id = 0
            async for last_msg in uclient.get_chat_history(urban_bot_username, limit=1):
                last_msg_id = last_msg.id
            
            await uclient.send_message(urban_bot_username, message_to_send)
            
            messages_received = []
            message_with_button = None
            
            for _ in range(5): # Poll up to 5 times
                await asyncio.sleep(2)
                async for msg in uclient.get_chat_history(urban_bot_username, limit=10):
                    is_from_bot = msg.from_user and msg.from_user.username and msg.from_user.username.lower() == urban_bot_username
                    
                    if msg.id > last_msg_id and is_from_bot:
                        # Avoid duplicates
                        if msg.id not in [m.id for m in messages_received]:
                            messages_received.append(msg)
                        
                        if msg.reply_markup:
                            message_with_button = msg
                            print(f"[v0] Found fresh message with reply_markup: {msg.id}")
                            break
                if message_with_button:
                    break
            
            if messages_received:
                # Sort by ID to ensure chronological order
                messages_received.sort(key=lambda x: x.id)
                
                # Filter out messages that were already handled by finding the message_with_button
                final_messages = []
                for msg in messages_received:
                    final_messages.append(msg)
                    if msg.reply_markup:
                        break

                for idx, response_msg in enumerate(final_messages):
                    has_button = response_msg.reply_markup is not None
                    reply_markup = response_msg.reply_markup if has_button else None
                    
                    text_to_show = response_msg.text or response_msg.caption
                    if is_pub_link and has_button:
                        text_to_show = "ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ"
                    
                    if response_msg.text or response_msg.caption:
                        if idx == 0:
                            if response_msg.photo:
                                await wait_msg.delete()
                                await message.reply_photo(response_msg.photo.file_id, caption=text_to_show, reply_markup=reply_markup)
                            elif response_msg.document:
                                await wait_msg.delete()
                                await message.reply_document(response_msg.document.file_id, caption=text_to_show, reply_markup=reply_markup)
                            else:
                                await wait_msg.edit_text(text_to_show, reply_markup=reply_markup)
                        else:
                            if response_msg.photo:
                                await message.reply_photo(response_msg.photo.file_id, caption=text_to_show, reply_markup=reply_markup)
                            elif response_msg.document:
                                await message.reply_document(response_msg.document.file_id, caption=text_to_show, reply_markup=reply_markup)
                            else:
                                await message.reply(text_to_show, reply_markup=reply_markup)
                    
                    if has_button:
                        await message.reply("<b>This Link Will Expire in 30 Second please Join fast ...</b>", parse_mode=enums.ParseMode.HTML)
                
                # as it was replacing the actual content. Instead, show a warning if still no button.
                if not message_with_button:
                    await message.reply("**⚠️ Link generated but no button found. Please check manually.**")
            else:
                await wait_msg.edit_text("**Could not retrieve link. Please try again.**")
        
        except Exception as e:
            print(f"[v0] Error generating link: {str(e)}")
            await wait_msg.edit_text(f"**Error generating link:** {str(e)}")
        
        finally:
            if uclient:
                try:
                    await uclient.disconnect()
                except:
                    pass
    
    except Exception as e:
        print(f"[v0] Error in generate_fresh_link: {str(e)}")
        await message.reply("**An error occurred. Please try again.**")
