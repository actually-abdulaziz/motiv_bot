import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from db import init_db, get_all_message_ids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHANNEL_ID = os.getenv("CHANNEL_ID")  # example: -1002576049448

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡️Random Motivation⚡️", callback_data="random_post")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Жми на кнопку для мотивации:", reply_markup=reply_markup)

async def send_random_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message_ids = get_all_message_ids()
    if not message_ids:
        await query.edit_message_text("Нет доступных постов.")
        return

    message_id = random.choice(message_ids)
    await context.bot.copy_message(
        chat_id=query.message.chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=message_id,
    )

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡️Random Motivation⚡️", callback_data="random_post")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Жми на кнопку для мотивации:", reply_markup=reply_markup)

async def main():
    init_db()
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CallbackQueryHandler(send_random_post, pattern="^random_post$"))
    logger.info("Bot started")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
