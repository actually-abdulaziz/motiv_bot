import os
import yt_dlp
import uuid
import logging
import asyncio
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from db import init_db, save_file_id

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LOADER_TOKEN = os.environ.get("LOADER_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
if CHANNEL_ID:
    try:
        CHANNEL_ID = int(CHANNEL_ID)
    except Exception as e:
        logger.error("CHANNEL_ID должен быть числом, например, -1002576049448")
        
# Инициализируем базу (файл ids.db будет создан автоматически)
init_db()

def download_media(url: str) -> list:
    unique_id = uuid.uuid4().hex
    ydl_opts = {
        "outtmpl": f"temp_{unique_id}/%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",      # Убедись, что файл существует или убери эту опцию
        "extractor_args": {"instagram": {"format": "best"}},
        "nooverwrites": True,
        "nocheckcertificate": True,
        "cachedir": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if "entries" in info:
                return [ydl.prepare_filename(entry) for entry in info["entries"]]
            return [ydl.prepare_filename(info)]
    except Exception as e:
        logger.error(f"Ошибка скачивания: {e}")
        return []

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" not in text:
        await update.message.reply_text("⚠️ Это не Instagram-ссылка.")
        return

    await update.message.reply_text("⏬ Скачиваю...")
    paths = download_media(text)
    
    if not paths:
        await update.message.reply_text("❌ Не удалось скачать контент.")
        return

    media_group = []
    for path in paths:
        if path.endswith((".jpg", ".jpeg", ".png")):
            with open(path, "rb") as file:
                media_group.append(InputMediaPhoto(file))
        elif path.endswith((".mp4", ".mkv")):
            with open(path, "rb") as file:
                media_group.append(InputMediaVideo(file))

    try:
        messages = await context.bot.send_media_group(CHANNEL_ID, media=media_group)
        for msg in messages:
            if msg.photo:
                # Берем последний элемент, т.к. там самые качественные размеры
                save_file_id(msg.photo[-1].file_id, "photo", text)
            elif msg.video:
                save_file_id(msg.video.file_id, "video", text)
        await update.message.reply_text("✅ Загружено и сохранено!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        for path in paths:
            if os.path.exists(path):
                os.remove(path)

def run_loader():
    # Создаем новый event loop для этого потока и устанавливаем его
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(LOADER_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
