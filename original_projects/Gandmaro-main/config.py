from os import environ

API_ID = int(environ.get("API_ID", "38627319"))
API_HASH = environ.get("API_HASH", "18b0827896e979267ae2251b63830827")
BOT_TOKEN = environ.get("BOT_TOKEN", "8417073518:AAFM9UQxtk25FBqKRSX8nYw2HP8waF77IJk")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1001918476761"))
ADMINS = int(environ.get("ADMINS", "1327021082"))

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "mongodb+srv://poulomig644_db_user:d9MMUd5PsTP5MDFf@cluster0.q5evcku.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "vjjoinrequetbot")

# If this is True Then Bot Accept New Join Request 
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))

RELAY_MODE = bool(environ.get('RELAY_MODE', False))  # Enable relay link functionality
BOT_B_LINK = environ.get("BOT_B_LINK", "")  # Fallback link if not set via admin command
LINK_COOLDOWN = int(environ.get('LINK_COOLDOWN', 5))  # Cooldown per user in seconds
RELAY_TIMEOUT = int(environ.get('RELAY_TIMEOUT', 8))  # Max time to wait for Bot B response
