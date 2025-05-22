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

init_db()

def download_media(url: str) -> list:
    unique_id = uuid.uuid4().hex
    ydl_opts = {
        "outtmpl": f"temp_{unique_id}/%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",
        "format": "bestvideo+bestaudio/best",
        "ffmpeg_location": os.environ.get("FFMPEG_PATH", "ffmpeg"),
        "nooverwrites": True,
        "nocheckcertificate": True,
        "cachedir": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if "entries" in info:
                logger.info(f"Обработка карусели из {len(info['entries'])} элементов.")
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

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        logger.info(f"Получено сообщение из канала: {update.channel_post}")
        if update.channel_post.photo:
            file_id = update.channel_post.photo[-1].file_id
            save_file_id(file_id, "photo")
            logger.info(f"Сохранено фото (file_id: {file_id})")
        elif update.channel_post.video:
            file_id = update.channel_post.video.file_id
            save_file_id(file_id, "video")
            logger.info(f"Сохранено видео (file_id: {file_id})")

def run_loader():
    logger.info("🚀 Запуск бота-загрузчика...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = ApplicationBuilder().token(LOADER_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
        logger.info("Бот-загрузчик готов к работе.")
        app.run_polling()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        loop.close()