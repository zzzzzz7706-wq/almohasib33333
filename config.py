import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(item.strip())
    for item in os.getenv("ADMIN_IDS", "").split(",")
    if item.strip().isdigit()
}

# Telegram Bot API upload limit is commonly 50 MB for these methods.
# Keep a little margin; increase only if your Bot API setup supports it.
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "49"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

DB_PATH = os.getenv("DB_PATH", "/data/bot.db")
if not os.path.isdir(os.path.dirname(DB_PATH) or "."):
    DB_PATH = "bot.db"

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/tmp/youtube-bot")
SOCKET_TIMEOUT = int(os.getenv("SOCKET_TIMEOUT", "30"))
