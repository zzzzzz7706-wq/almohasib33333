import asyncio
import logging
import os
import shutil

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from config import MAX_UPLOAD_MB, MAX_UPLOAD_BYTES
from database.db import register_user, record_download
from keyboards.buttons import quality_keyboard
from services.youtube import is_youtube_url, get_video_info
from services.downloader import download_media

logger = logging.getLogger(__name__)
DOWNLOAD_LIMIT = asyncio.Semaphore(2)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not message.text:
        return

    register_user(user.id, user.username or "", user.full_name or "")

    url = message.text.strip()
    if not is_youtube_url(url):
        await message.reply_text("أرسل رابط فيديو صحيحاً من YouTube.")
        return

    status = await message.reply_text("🔎 جارٍ قراءة معلومات الفيديو...")
    try:
        info = await asyncio.to_thread(get_video_info, url)
    except Exception as exc:
        logger.warning("Metadata extraction failed: %s", exc)
        await status.edit_text(
            "تعذر قراءة الفيديو. قد يكون الرابط غير متاح أو يتطلب تسجيل دخول.\n"
            "تحقق من الرابط وحاول مرة أخرى."
        )
        return

    context.user_data["youtube_url"] = url
    title = info.get("title") or "فيديو بدون عنوان"
    duration = info.get("duration")
    duration_text = f"{int(duration)//60}:{int(duration)%60:02d}" if duration else "غير معروف"
    thumbnail = info.get("thumbnail")
    text = (
        f"🎬 <b>{escape_html(title)}</b>\n"
        f"⏱ المدة: {duration_text}\n"
        "اختر الإجراء المطلوب:"
    )
    keyboard = quality_keyboard()
    await status.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


async def handle_download_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("youtube_url")
    if not url:
        await query.edit_message_text("انتهت صلاحية الرابط. أرسل الرابط من جديد.")
        return

    parts = query.data.split(":")
    if len(parts) != 3:
        await query.edit_message_text("طلب غير صالح.")
        return

    _, mode, quality = parts
    if mode not in {"video", "audio"}:
        await query.edit_message_text("نوع التنزيل غير صالح.")
        return

    if mode == "video" and quality not in {"360", "480", "720", "1080"}:
        await query.edit_message_text("الجودة المطلوبة غير مدعومة.")
        return

    async with DOWNLOAD_LIMIT:
        status = await query.edit_message_text("⏳ جارٍ تجهيز التنزيل...")
        progress = {"percent": 0.0, "status": "starting"}
        task = asyncio.create_task(
            asyncio.to_thread(download_media, url, mode, quality, progress)
        )

        last_percent = -1
        while not task.done():
            await asyncio.sleep(3)
            percent = int(progress.get("percent", 0))
            if percent != last_percent and percent > 0:
                last_percent = percent
                try:
                    await status.edit_text(f"⬇️ جارٍ التنزيل... {percent}%")
                except Exception:
                    pass

        try:
            directory, file_path, title = await task
        except Exception as exc:
            logger.exception("Download failed: %s", exc)
            await status.edit_text(
                "تعذر تنزيل هذا المحتوى. قد لا تكون الجودة متاحة أو قد يكون "
                "الفيديو محمياً/غير متاح."
            )
            return

        try:
            size = os.path.getsize(file_path)
            if size > MAX_UPLOAD_BYTES:
                await status.edit_text(
                    f"حجم الملف أكبر من حد الإرسال الحالي ({MAX_UPLOAD_MB} MB). "
                    "جرّب جودة أقل أو محتوى أقصر."
                )
                return

            await status.edit_text("📤 اكتمل التنزيل، جارٍ الإرسال...")
            await context.bot.send_chat_action(
                chat_id=query.message.chat_id, action=ChatAction.UPLOAD_DOCUMENT
            )

            with open(file_path, "rb") as media:
                if mode == "audio":
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=media,
                        title=title[:64],
                        caption="تم استخراج الصوت بنجاح 🎵",
                        read_timeout=120,
                        write_timeout=120,
                    )
                else:
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=media,
                        caption=f"{title[:700]}",
                        supports_streaming=True,
                        read_timeout=120,
                        write_timeout=120,
                    )

            record_download(query.from_user.id, mode)
            await status.edit_text("✅ تم إرسال الملف بنجاح.")
        except Exception as exc:
            logger.exception("Telegram upload failed: %s", exc)
            await status.edit_text(
                "اكتمل التنزيل، لكن تعذر إرسال الملف إلى تيليجرام. "
                "قد يكون حجم الملف أو الاتصال هو السبب."
            )
        finally:
            shutil.rmtree(directory, ignore_errors=True)


def escape_html(value: str) -> str:
    return (
        str(value).replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
