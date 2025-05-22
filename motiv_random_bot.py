import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from db import load_random, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

VIEWER_TOKEN = os.environ.get("VIEWER_TOKEN")

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 Получить мотивацию", callback_data="random")]]
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы получить случайную мотивацию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await query.message.reply_text("⚠️ Не удалось загрузить контент.")

def run_viewer():
    # Явное создание event loop для процесса
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(VIEWER_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()