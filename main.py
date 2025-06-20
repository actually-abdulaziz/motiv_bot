import logging
import os
import random
import sqlite3

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
DB_FILE = "messages.db"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DB ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def save_message_id(message_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO messages (id) VALUES (?)", (message_id,))
    conn.commit()
    conn.close()

def get_random_message_id():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM messages ORDER BY RANDOM() LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# --- Handlers ---
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if msg and str(msg.chat.id) == CHANNEL_ID:
        save_message_id(msg.message_id)
        logger.info(f"Saved message_id: {msg.message_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("⚡️Random Motivation⚡️", callback_data="get_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Нажми кнопку ниже, чтобы получить мотивацию:",
        reply_markup=reply_markup
    )

async def send_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = get_random_message_id()
    if message_id:
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=message_id
        )
    else:
        await update.message.reply_text("Нет сохранённых постов.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "get_random":
        message_id = get_random_message_id()
        if message_id:
            await context.bot.forward_message(
                chat_id=query.message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id
            )
        else:
            await query.message.reply_text("Нет сохранённых постов.")

# --- Main ---
async def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", send_random))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

    await app.bot.set_my_commands([
        ("start", "Начало"),
        ("random", "⚡️Random Motivation⚡️")
    ])

    logger.info("Bot started")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "event loop is already running" in str(e):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(main())
        else:
            raise
