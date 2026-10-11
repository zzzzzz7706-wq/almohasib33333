from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def quality_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎥 فيديو 360p", callback_data="dl:video:360"),
            InlineKeyboardButton("🎥 فيديو 480p", callback_data="dl:video:480"),
        ],
        [
            InlineKeyboardButton("🎥 فيديو 720p", callback_data="dl:video:720"),
            InlineKeyboardButton("🎥 فيديو 1080p", callback_data="dl:video:1080"),
        ],
        [InlineKeyboardButton("🎵 استخراج MP3", callback_data="dl:audio:mp3")],
    ])
