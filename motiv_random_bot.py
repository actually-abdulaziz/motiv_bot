import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import load_random, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

VIEWER_TOKEN = os.environ.get("VIEWER_TOKEN")
# Наш канал, откуда будут пересылаться сообщения
CHANNEL_ID = os.environ.get("CHANNEL_ID")
if CHANNEL_ID:
    CHANNEL_ID = int(CHANNEL_ID)

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = load_random()
    if not content:
        await update.message.reply_text("😔 В базе пока нет контента.")
        return
    try:
        # Пересылаем сообщение из канала в чат с пользователем
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=content["message_id"]
        )
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ Не удалось переслать сообщение.")

def run_viewer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(VIEWER_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    run_viewer()
