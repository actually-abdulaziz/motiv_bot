import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from db import init_db, save_message_id

# Получите эти данные на https://my.telegram.org
API_ID = int(os.environ.get("TELEGRAM_API_ID", "123456"))  # замените 123456 на ваш API_ID
API_HASH = os.environ.get("TELEGRAM_API_HASH", "your_api_hash")
# Например, CHANNEL_USERNAME может быть '-1002576049448' (как строка) или '@channelusername'
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "-1002576049448")

# Создаем клиента (сессия автоматически сохранится в файле session_name.session)
client = TelegramClient('session_name', API_ID, API_HASH)

async def scrape_channel():
    await client.start()
    print("Начинаю обход канала...")
    async for message in client.iter_messages(CHANNEL_USERNAME):
        # Если сообщение содержит фото или видео
        if message.photo or message.video:
            media_type = "photo" if message.photo else "video"
            print(f"Найдено сообщение: id={message.id}, type={media_type}")
            # В качестве url можно сохранить исходную ссылку или оставить пустым
            save_message_id(message.id, media_type, "")
    print("Обход канала завершён.")

if __name__ == "__main__":
    init_db()
    with client:
        client.loop.run_until_complete(scrape_channel())
