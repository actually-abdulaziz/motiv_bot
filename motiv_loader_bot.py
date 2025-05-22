import os
import yt_dlp
import uuid
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from db import init_db, save_file_id

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LOADER_TOKEN = os.environ.get("LOADER_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def download_media(url):
    unique_id = uuid.uuid4().hex
    output_template = f"temp_{unique_id}.%(ext)s"
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,
        "format": "best",
        "cookiefile": "cookies.txt",  # ⚠️ Создайте этот файл (инструкция ниже)
        "extractor_args": {"instagram": {"format": "best"}},
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logger.error(f"Ошибка скачивания: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" not in text:
        await update.message.reply_text("⚠️ Это не Instagram-ссылка.")
        return

    await update.message.reply_text("⏬ Скачиваю...")
    path = None
    try:
        path = download_media(text)
        if not path:
            raise Exception("Не удалось скачать контент")

        if path.endswith(('.jpg', '.jpeg', '.png')):
            with open(path, "rb") as file:
                msg = await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=file,
                    caption=f"Источник: {text}"
                )
                save_file_id(msg.photo[-1].file_id, "photo", url=text)
        else:
            with open(path, "rb") as file:
                msg = await context.bot.send_video(
                    chat_id=CHANNEL_ID,
                    video=file,
                    caption=f"Источник: {text}"
                )
                save_file_id(msg.video.file_id, "video", url=text)

        await update.message.reply_text("✅ Загружено и сохранено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(LOADER_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logger.info("🚀 motiv_loader_bot запущен")
    app.run_polling()