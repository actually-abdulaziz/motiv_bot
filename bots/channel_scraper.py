import os
import json
from telegram import Bot
from telegram.ext import ApplicationBuilder

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
JSON_PATH = "data/message_ids.json"

async def scrape_messages():
    bot = Bot(token=BOT_TOKEN)
    all_ids = []
    offset_id = None

    while True:
        # Пагинация по 100 сообщений за раз
        messages = await bot.get_updates(
            chat_id=CHANNEL_ID,
            limit=100,
            offset=offset_id
        )

        if not messages:
            break

        # Собираем ID
        new_ids = [msg.message_id for msg in messages]
        all_ids.extend(new_ids)
        offset_id = new_ids[-1] - 1  # Сдвиг для следующей порции

        # Сохраняем прогресс
        with open(JSON_PATH, "w") as f:
            json.dump(all_ids, f)

    print(f"✅ Собрано {len(all_ids)} сообщений")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.run(scrape_messages)