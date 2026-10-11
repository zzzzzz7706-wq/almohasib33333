from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database.db import get_stats

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.effective_message.reply_text("هذا الأمر للمشرف فقط.")
        return

    data = get_stats()
    await update.effective_message.reply_text(
        "📊 إحصائيات البوت\n\n"
        f"👥 المستخدمون: {data['users']}\n"
        f"🎬 تنزيلات الفيديو: {data['videos']}\n"
        f"🎵 ملفات الصوت: {data['audios']}\n"
        f"⬇️ إجمالي العمليات: {data['total']}"
    )
