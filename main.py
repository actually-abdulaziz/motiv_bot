import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from db import init_db, get_all_message_ids

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start — только приветствие и кнопка
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡️Получить мотивацию⚡️", callback_data="get_random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Нажми кнопку ниже, чтобы получить мотивацию:",
        reply_markup=reply_markup,
    )

# Команда /random — пересылает случайное сообщение
async def random_motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_ids = get_all_message_ids()
    if not message_ids:
        await update.message.reply_text("Нет доступных сообщений.")
        return
    msg_id = random.choice(message_ids)
    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=CHANNEL_ID,
        message_id=msg_id,
    )

# Кнопка из InlineKeyboard
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "get_random":
        message_ids = get_all_message_ids()
        if not message_ids:
            await query.edit_message_text("Нет доступных сообщений.")
            return
        msg_id = random.choice(message_ids)
        await context.bot.copy_message(
            chat_id=query.message.chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=msg_id,
        )

async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Начать"),
        BotCommand("random", "⚡️Random Motivation⚡️"),
    ]
    await application.bot.set_my_commands(commands)

async def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_motivation))
    app.add_handler(
        telegram.ext.CallbackQueryHandler(handle_callback)
    )

    await set_bot_commands(app)
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
