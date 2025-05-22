import os
import random
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_PATH = "motiv.db"
VIEWER_TOKEN = os.environ.get("VIEWER_TOKEN")

app = ApplicationBuilder().token(VIEWER_TOKEN).build()  # <-- вынесено из if

def get_random_file():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_type, url FROM files ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"file_id": row[0], "file_type": row[1], "url": row[2]}
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Нажми /motivate чтобы получить мотивашку.")

async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_random_file()
    if not data:
        await update.message.reply_text("⚠️ Пока нет сохранённого контента.")
        return

    caption = f"Источник: {data['url']}" if data["url"] else None
    try:
        if data["file_type"] == "photo":
            await update.message.reply_photo(photo=data["file_id"], caption=caption)
        else:
            await update.message.reply_video(video=data["file_id"], caption=caption)
    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}")
        await update.message.reply_text("❌ Не удалось отправить файл.")

app.add_handler(CommandHandler("start", start))     # <-- вынесено вне if
app.add_handler(CommandHandler("motivate", motivate))

if __name__ == "__main__":
    logger.info("🚀 motiv_random_bot запущен")
    app.run_polling()
