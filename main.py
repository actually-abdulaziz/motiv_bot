import os
import logging
import asyncio
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

from db import init_db, get_all_message_ids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # пример: -1002576049448

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Нажми /random чтобы получить мотивацию.")

async def random_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_all_message_ids()
    if not messages:
        await update.message.reply_text("Контент не загружен.")
        return

    message_id = random.choice(messages)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Ещё мотивация", callback_data="get_new")]])
    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=CHANNEL_ID,
        message_id=message_id,
        reply_markup=keyboard
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "get_new":
        messages = get_all_message_ids()
        if messages:
            message_id = random.choice(messages)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Ещё мотивация", callback_data="get_new")]])
            await context.bot.copy_message(
                chat_id=query.message.chat_id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id,
                reply_markup=keyboard
            )

async def main():
    await init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_motivation))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Bot started")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
