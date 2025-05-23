import logging
import random
import sqlite3
import os

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

DB_FILE = "messages.db"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- DB Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()


def save_message_id(message_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO messages (id) VALUES (?)", (message_id,))
    conn.commit()
    conn.close()


def get_random_message_id() -> int | None:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM messages ORDER BY RANDOM() LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


# --- Handlers ---
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if message and str(message.chat.id) == CHANNEL_ID:
        save_message_id(message.message_id)
        logger.info(f"Saved message_id: {message.message_id}")


async def send_random_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = get_random_message_id()
    if message_id:
        await context.bot.forward_message(chat_id=update.effective_chat.id,
                                          from_chat_id=CHANNEL_ID,
                                          message_id=message_id)
    else:
        await update.message.reply_text("Нет сохранённых постов.")


# --- Main ---
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", send_random_post))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
