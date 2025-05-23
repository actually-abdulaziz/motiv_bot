import os
import json
import logging
from telegram import Bot
from telegram.ext import ApplicationBuilder

logging.basicConfig(
    format="%(asctime)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SCRAPER_TOKEN = os.getenv("SCRAPER_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
JSON_PATH = "data/message_ids.json"

async def scrape_messages():
    try:
        bot = Bot(token=BOT_TOKEN)
        all_ids = []
        offset_id = None

        while True:
            # Пагинация по 100 сообщений
            messages = await bot.get_updates(
                chat_id=CHANNEL_ID,
                limit=100,
                offset=offset_id
            )

            if not messages:
                break

            new_ids = [msg.message_id for msg in messages]
            all_ids.extend(new_ids)
            offset_id = new_ids[-1] - 1

            # Сохранение данных
            with open(JSON_PATH, "w") as f:
                json.dump(all_ids, f)

        logger.info(f"✅ Собрано {len(all_ids)} сообщений")
    except Exception as e:
        logger.error(f"🚨 Ошибка: {e}")

def run_scraper():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.run_polling()

if __name__ == "__main__":
    run_scraper()