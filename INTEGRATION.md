# Integrated Workflow

The active entry point is `bot.py`. It preserves the original Rename-Bot plugin architecture and adds `integration/` as an additive workflow layer. The original full Gandmaro and Rename-Bot source trees are retained under `original_projects/` for auditability.

## Commands

The administrator uses `/login` to create and persist a Gandmaro-compatible Pyrogram user session. `/set -100SOURCE -100OUTPUT` stores the monitored source and output channels. `/setusername @example` stores the username token used in filename replacement. `/setthumb -100SOURCE` arms the next administrator photo as the thumbnail for that source only.

## Automatic path

After restart, the persisted admin session monitors the configured source channel. Supported documents, videos, and audio files are atomically claimed in MongoDB, processed through the existing Rename-Bot FFmpeg/media helpers, and uploaded to the configured output channel. The original interactive Rename-Bot handlers remain available through the normal plugin system.

## Integration collections

The additive collections are `integration_settings`, `source_thumbnails`, `processed_messages`, and `admin_session`. The original Rename-Bot `user` collection is preserved for existing user settings, quotas, captions, metadata, and thumbnails.

## Deployment requirements

Use Python dependencies from `requirements.txt` and ensure FFmpeg is installed. Required environment variables are listed in `.env.example`. Credentials must be supplied through deployment secrets; no source-controlled fallback secrets should be used.
