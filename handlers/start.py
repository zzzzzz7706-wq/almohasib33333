from telegram import Update
from telegram.ext import ContextTypes

WELCOME = (
    "أهلاً بك في بوت تنزيل الوسائط 🎬\n\n"
    "أرسل رابط فيديو YouTube، وسأعرض لك معلوماته وخيارات التنزيل.\n\n"
    "يدعم تنزيل الفيديو أو استخراج الصوت MP3.\n"
    "استخدم /help لمعرفة طريقة الاستخدام.\n\n"
    "تنبيه: استخدم البوت فقط مع المحتوى الذي تملكه أو لديك إذن بتنزيله، "
    "والتزم بحقوق النشر وشروط المنصة."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(WELCOME)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "طريقة الاستخدام:\n"
        "1) أرسل رابط فيديو من YouTube.\n"
        "2) انتظر ظهور معلومات الفيديو.\n"
        "3) اختر تنزيل الفيديو والجودة، أو استخراج الصوت MP3.\n\n"
        "الأوامر:\n"
        "/start - بدء الاستخدام\n"
        "/help - المساعدة\n"
        "/stats - إحصائيات (للمشرف فقط)\n\n"
        "ملاحظة: الملفات الكبيرة التي تتجاوز الحد المسموح به للإرسال "
        "لن يتم إرسالها عبر تيليجرام."
    )
