import logging
import random
import sqlite3
import os
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
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
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()


def save_message_id(message_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO messages (id) VALUES (?)", (message_id,))
    conn.commit()
    conn.close()


def get_all_message_ids():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM messages")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]


def delete_message_id(message_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()


# --- Handlers ---
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if message and str(message.chat.id) == CHANNEL_ID:
        save_message_id(message.message_id)
        logger.info(f"Saved message_id: {message.message_id}")


async def send_random_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_ids = get_all_message_ids()
    if not message_ids:
        await update.message.reply_text("Нет сохранённых постов.")
        return

    while message_ids:
        message_id = random.choice(message_ids)
        try:
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=message_id,
            )
            return
        except Exception as e:
            logger.warning(f"Ошибка при пересылке {message_id}: {e}")
            delete_message_id(message_id)
            message_ids.remove(message_id)

    await update.message.reply_text("Все сохранённые сообщения недоступны.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот активен. Жми /random для мотивации ⚡️"
    )


# --- Main ---
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", send_random_post))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

    # Настроим команду в меню Telegram
    await app.bot.set_my_commands([
    	BotCommand("random", "⚡️Random Motivation⚡️")
    ])


    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
