import os


def _int_env(name: str, default: str = "0") -> int:
    value = os.environ.get(name, default).strip()
    return int(value) if value else 0


API_ID = _int_env("API_ID")
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = _int_env("ADMIN")
ADMINS = ADMIN

# Gandmaro's admin user session is persisted in MongoDB by integration/database.py.
STRING_SESSION = os.environ.get("STRING_SESSION", "")

FORCE_SUBS = os.environ.get("FORCE_SUBS", os.environ.get("FORCE_SUB", ""))
LOG_CHANNEL = _int_env("LOG_CHANNEL")

DATABASE_URL = os.environ.get("DATABASE_URL", os.environ.get("DB_URI", ""))
DATABASE_NAME = os.environ.get("DATABASE_NAME", os.environ.get("DB_NAME", "madflixbotz"))
DB_URI = DATABASE_URL
DB_NAME = DATABASE_NAME

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")

# Automatic Source Channel -> Existing Rename-Bot processing -> Output Channel workflow.
DEFAULT_USERNAME = os.environ.get("DEFAULT_USERNAME", "")
PROCESSING_WORKERS = _int_env("PROCESSING_WORKERS", "2") or 2
MAX_RETRY_ATTEMPTS = _int_env("MAX_RETRY_ATTEMPTS", "3") or 3

# Compatibility settings retained from Gandmaro.
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "false").lower() == "true"
RELAY_MODE = os.environ.get("RELAY_MODE", "false").lower() == "true"
BOT_B_LINK = os.environ.get("BOT_B_LINK", "")
LINK_COOLDOWN = _int_env("LINK_COOLDOWN", "5")
RELAY_TIMEOUT = _int_env("RELAY_TIMEOUT", "8")
