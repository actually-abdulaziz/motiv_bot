import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from db import init_db, load_random

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

VIEWER_TOKEN = os.environ["VIEWER_TOKEN"]
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 Получить мотивацию", callback_data="random")]]
    await update.message.reply_text(
        "🌟 Нажмите кнопку, чтобы получить случайный мотивационный контент:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_random_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    content = load_random()
    
    if not content:
        await query.message.reply_text("😔 В базе пока нет контента.")
        return
    
    try:
        if content["type"] == "photo":
            await query.message.reply_photo(content["file_id"])
        else:
            await query.message.reply_video(content["file_id"])
        logger.info(f"Отправлен контент: {content['file_id']}")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

def run_viewer():
    app = ApplicationBuilder().token(VIEWER_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(send_random_content, pattern="^random$"))
    app.run_polling()