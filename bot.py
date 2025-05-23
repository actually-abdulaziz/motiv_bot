import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, CallbackQueryHandler, ChannelPostHandler
)
from db import init_db, save_post, get_random_post

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Обработка старта и кнопки
async def send_random_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_ids = get_random_post()
    if not post_ids:
        await update.effective_message.reply_text("Нет доступного контента.")
        return

    for message_id in post_ids:
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=message_id
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Новый пост", callback_data="get_new")]
    ])
    await update.effective_message.reply_text(
        "Нажми кнопку, чтобы получить мотивацию:",
        reply_markup=keyboard
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_random_post(update, context)

# Хендлер загрузки из канала
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return

    post_type = (
        'photo' if message.photo else
        'video' if message.video else
        'animation' if message.animation else
        'document' if message.document else
        None
    )

    if post_type:
        media_group_id = message.media_group_id
        save_post(message.message_id, media_group_id, post_type)

# Инициализация
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", send_random_post))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(ChannelPostHandler(handle_new_post))

    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
