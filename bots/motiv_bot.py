import os
import json
import random
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
JSON_PATH = "data/message_ids.json"

async def send_random_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not os.path.exists(JSON_PATH):
            await update.message.reply_text("⚠️ Контент еще не загружен. Попробуйте позже.")
            return

        with open(JSON_PATH, "r") as f:
            raw_data = f.read().strip()
            if not raw_data:
                await update.message.reply_text("😔 В канале пока нет контента.")
                return

            message_ids = json.loads(raw_data)

        random_id = random.choice(message_ids)
        await context.bot.forward_message(
            chat_id=update.message.chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=random_id
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("🔥 Системная ошибка!")

def run_bot():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(1)  # Фикс конфликтов
        .build()
    )
    app.add_handler(CommandHandler("start", send_random_post))
    app.run_polling()

if __name__ == "__main__":
    run_bot()