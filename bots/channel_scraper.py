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
        bot = Bot(token=SCRAPER_TOKEN)
        all_ids = []
        
        # Собираем сообщения через get_chat_history
        async for message in bot.get_chat_history(CHANNEL_ID):
            all_ids.append(message.message_id)
            
            # Сохраняем прогресс каждые 100 сообщений
            if len(all_ids) % 100 == 0:
                with open(JSON_PATH, "w") as f:
                    json.dump(all_ids, f)

        # Финальное сохранение
        with open(JSON_PATH, "w") as f:
            json.dump(all_ids, f)
            
        logger.info(f"✅ Собрано {len(all_ids)} сообщений")
    except Exception as e:
        logger.error(f"🚨 Ошибка: {e}")

def run_scraper():
    app = ApplicationBuilder().token(SCRAPER_TOKEN).build()
    app.run_polling()

if __name__ == "__main__":
    run_scraper()