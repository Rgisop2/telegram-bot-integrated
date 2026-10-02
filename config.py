import os


def _int_env(name: str, default: str = "0") -> int:
    value = os.environ.get(name, default).strip()
    return int(value) if value else 0


API_ID = _int_env("24916173")
API_HASH = os.environ.get("API_HASH", "5c82a6ae14e291efc20dee7757c9feee")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8815831623:AAFOeCPCZGLP1ZfnbjvDxESQgL7lm2vo8VY")
ADMIN = _int_env("1317519146")
ADMINS = ADMIN

# Gandmaro's admin user session is persisted in MongoDB by integration/database.py.
STRING_SESSION = os.environ.get("STRING_SESSION", "WZ_AwUBfDDNALypeRgjpz2W4TGwq2_tQHaUN20aiIgM7XIvwRGk9_uB5PxG-DddV9pY0rN11EavVBin7apAnoeyISfdM5h65etsinZDBl2tK9nd4NV4s7fF0qDHyO6ghl6OYkHRsa20P_UZVFjN7LcYpWif9lfLcTX8EEu2Jd8PHDgLITJfmesJMXsSswEZtcsUji_icDssVQIV0U4iOQoRyEP0u9JD9obl5L9nS9bK3MxMHiyUA59YNE98YxewDySD_jaq1kp7y0R0M1pdco3RqWUyM_i8ulN9L1NvMYm6Ar4MAaWdzTc8fmp76vyv4d2v1Wq8EI23oDJjdsnYhzuy9-16BA1GL08AAAACBNVChgABuzkxLjEwOC41Ni4xNjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALIUEE0")

FORCE_SUBS = os.environ.get("FORCE_SUBS", os.environ.get("FORCE_SUB", "-1002342624998"))
LOG_CHANNEL = _int_env("-1002342624998")

DATABASE_URL = os.environ.get("DATABASE_URL", os.environ.get("DB_URI", "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"))
DATABASE_NAME = os.environ.get("DATABASE_NAME", os.environ.get("DB_NAME", "madflixbotz"))
DB_URI = DATABASE_URL
DB_NAME = DATABASE_NAME

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")

# Automatic Source Channel -> Existing Rename-Bot processing -> Output Channel workflow.
DEFAULT_USERNAME = os.environ.get("DEFAULT_USERNAME", "hekajsiajbshjz")
PROCESSING_WORKERS = _int_env("PROCESSING_WORKERS", "2") or 2
MAX_RETRY_ATTEMPTS = _int_env("MAX_RETRY_ATTEMPTS", "3") or 3

# Compatibility settings retained from Gandmaro.
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "false").lower() == "true"
RELAY_MODE = os.environ.get("RELAY_MODE", "false").lower() == "true"
BOT_B_LINK = os.environ.get("BOT_B_LINK", "")
LINK_COOLDOWN = _int_env("LINK_COOLDOWN", "5")
RELAY_TIMEOUT = _int_env("RELAY_TIMEOUT", "8")
