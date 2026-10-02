# Telegram Link Relay Bot Setup Guide

## Overview
This bot system acts as a bridge between two Telegram bots using a user account session (Pyrogram). It fetches temporary join links from Bot B and relays them to users.

## How It Works

### System Architecture
1. **Bot A (Our Bot)** - The relay bot that users interact with
2. **Bot B (Source Bot)** - Generates temporary join links (expires every 1 minute)
3. **User Account** - Acts as a legal bridge between the two bots

### User Flow
```
User starts Bot A
    ↓
Bot A shows "Generating your link, please wait..."
    ↓
User account sends /start <payload> to Bot B
    ↓
Bot B responds with join link button
    ↓
Bot A extracts and relays the link back to user
    ↓
User sees "HERE IS YOUR LINK! CLICK BELOW TO PROCEED" with button
```

## Setup Instructions

### 1. Environment Variables

Add these to your deployment environment or .env file:

```
API_ID=<your_api_id>
API_HASH=<your_api_hash>
BOT_TOKEN=<your_bot_token>
LOG_CHANNEL=<your_log_channel_id>
ADMINS=<your_admin_user_id>
DB_URI=<your_mongodb_uri>
DB_NAME=vjjoinrequestbot

# Relay Mode Configuration
RELAY_MODE=True
BOT_B_LINK=https://t.me/YourBotB?start=your_payload
LINK_COOLDOWN=10
RELAY_TIMEOUT=8
```

### 2. Set Bot B Link via Admin Command

Instead of hardcoding, you can set it dynamically:

```
/setlink https://t.me/Urban_Links_bot?start=req_LTEwMDE4MjU1MjgwMDI
```

### 3. Commands

#### Admin Commands:
- `/setlink <BOT_B_START_LINK>` - Save Bot B's start link (only admins)
- `/getlink` - View current Bot B link (only admins)

#### User Commands:
- `/start` - Request a fresh join link

## Features

### Cooldown Protection
- Per-user 10-second cooldown (configurable via `LINK_COOLDOWN`)
- Prevents spam and respects Telegram rate limits

### FloodWait Protection
- 2-3 second delay between user account requests
- Automatic handling of Telegram API throttling

### Error Handling
- Graceful error messages if Bot B doesn't respond
- Timeout protection (8 seconds max wait)
- Session validation before attempting relay

### No Join Request Approval
- This bot does NOT approve join requests
- It only relays links from Bot B to users
- Can optionally approve via `/accept` command with user session

## Database Schema

### Users Collection
```
{
  _id: ObjectId,
  id: int,                    # User ID
  name: string,               # User's first name
  session: string,            # Pyrogram session (optional)
  last_link_request: float    # Timestamp of last link request
}
```

### Relay Config Collection
```
{
  _id: "bot_b_link",
  link: string,              # Bot B's start link
  set_by: int,               # Admin ID who set it
  timestamp: float           # When it was set
}
```

## Important Notes

1. **User Account Session**: The relay functionality requires a Pyrogram user account session. Without it, the relay won't work.
2. **Bot B Link Format**: Must be a valid Telegram link: `https://t.me/botusername?start=payload`
3. **Link Expiry**: Each request fetches a fresh link (no caching) since Bot B links expire every minute
4. **No Bot-to-Bot**: This system avoids direct bot-to-bot communication, which Telegram doesn't allow
5. **Rate Limiting**: Always respect FloodWait errors; built-in delays are configured

## Troubleshooting

### Bot doesn't respond to /start
- Check if `RELAY_MODE=True` is set
- Verify Bot B link is correct: `/getlink`
- Check user session exists in database

### "Bot B did not respond in time"
- Bot B might be offline or slow
- Increase `RELAY_TIMEOUT` in config
- Check network connectivity

### "Could not extract link from response"
- Bot B's response format might have changed
- Check if button text includes "join" keyword
- Review Bot B's message format in `extract_link_from_response()`

### Cooldown errors
- Per-user cooldown is working as intended
- Adjust `LINK_COOLDOWN` if needed

## Deployment Notes

This bot is designed for deployment on platforms like:
- Heroku (with Procfile included)
- Railway
- Replit
- Any server with Python 3.8+

Ensure MongoDB is connected and accessible from your deployment environment.
