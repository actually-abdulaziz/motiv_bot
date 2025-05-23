import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler
import os
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # формат: "-100..."

application: Application = Application.builder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

async def get_random_message_id():
    updates = await bot.get_chat_history(chat_id=CHANNEL_ID, limit=1)
    if not updates or not updates[-1].message_id:
        return None
    last_id = updates[-1].message_id
    return random.randint(1, last_id)

async def send_random_post(update, context):
    while True:
        message_id = await get_random_message_id()
        if not message_id:
            await update.message.reply_text("Канал пуст.")
            return
        try:
            await bot.forward_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=message_id)
            return
        except:
            continue  # если сообщение не существует, пробуем другое

async def start(update, context):
    await update.message.reply_text("Жми /motivate чтобы получить пост.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("motivate", send_random_post))

if __name__ == "__main__":
    asyncio.run(application.run_polling())
