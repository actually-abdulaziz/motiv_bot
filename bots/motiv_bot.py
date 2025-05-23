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
        with open(JSON_PATH, "r") as f:
            message_ids = json.load(f)

        # 3 попытки на случай удаленных сообщений
        for _ in range(3):
            if not message_ids:
                await update.message.reply_text("😔 Контент закончился.")
                return

            random_id = random.choice(message_ids)
            try:
                await context.bot.forward_message(
                    chat_id=update.message.chat_id,
                    from_chat_id=CHANNEL_ID,
                    message_id=random_id
                )
                return
            except Exception as e:
                message_ids.remove(random_id)
                logger.warning(f"Удален ID {random_id}: {e}")

        await update.message.reply_text("⚠️ Все выбранные посты удалены.")

        # Обновляем файл
        with open(JSON_PATH, "w") as f:
            json.dump(message_ids, f)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        await update.message.reply_text("🔥 Системная ошибка!")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", send_random_post))
    app.run_polling()

if __name__ == "__main__":
    run_bot()