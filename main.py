import logging
import os

from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
)

from config import BOT_TOKEN
from database.db import init_db
from handlers.start import start, help_command
from handlers.download import handle_text, handle_download_callback
from handlers.admin import stats

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    init_db()
    logger.info("Database initialized; bot is starting.")


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it to Railway Variables.")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .concurrent_updates(4)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(handle_download_callback, pattern=r"^dl:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Starting Telegram bot with long polling.")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
