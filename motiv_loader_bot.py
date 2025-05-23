import os
import yt_dlp
import uuid
import logging
import asyncio
import sqlite3
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)
from db import init_db, save_file_id, delete_file_id

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LOADER_TOKEN = os.environ["LOADER_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
init_db()

def download_media(url: str) -> list:
    unique_id = uuid.uuid4().hex
    ydl_opts = {
        "outtmpl": f"temp_{unique_id}/%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",
        "format": "best",
        "ffmpeg_location": "/usr/bin/ffmpeg",
        "extractor_args": {"instagram": {"carousel": True}},
        "nooverwrites": True,
        "nocheckcertificate": True,
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
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    logger.info(f"Получена ссылка: {text}")
    
    if "instagram.com" not in text:
        await update.message.reply_text("⚠️ Отправьте ссылку на Instagram.")
        return
    
    await update.message.reply_text("⏬ Скачиваю...")
    paths = download_media(text)
    
    if not paths:
        await update.message.reply_text("❌ Не удалось скачать контент.")
        return
    
    media_group = []
    for path in paths:
        try:
            if path.endswith((".jpg", ".jpeg", ".png")):
                with open(path, "rb") as file:
                    media_group.append(InputMediaPhoto(file))
            elif path.endswith((".mp4", ".mkv")):
                with open(path, "rb") as file:
                    media_group.append(InputMediaVideo(file))
        except Exception as e:
            logger.error(f"Ошибка чтения файла {path}: {e}")
    
    if not media_group:
        await update.message.reply_text("❌ Нет подходящих медиафайлов.")
        return
    
    try:
        messages = await context.bot.send_media_group(CHANNEL_ID, media=media_group)
        for msg in messages:
            if msg.photo:
                save_file_id(msg.photo[-1].file_id, "photo", text, msg.message_id)
            elif msg.video:
                save_file_id(msg.video.file_id, "video", text, msg.message_id)
        await update.message.reply_text("✅ Контент загружен в канал!")
    except Exception as e:
        logger.error(f"Ошибка отправки в канал: {e}")
        await update.message.reply_text("❌ Ошибка загрузки.")
    finally:
        for path in paths:
            try:
                os.remove(path)
            except Exception as e:
                logger.error(f"Ошибка удаления {path}: {e}")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        post = update.channel_post
        if post.photo:
            file_id = post.photo[-1].file_id
            save_file_id(file_id, "photo", "manual_upload", post.message_id)
            logger.info(f"Ручное сохранение фото: {file_id}")
        elif post.video:
            file_id = post.video.file_id
            save_file_id(file_id, "video", "manual_upload", post.message_id)
            logger.info(f"Ручное сохранение видео: {file_id}")

async def check_channel_updates(context: ContextTypes.DEFAULT_TYPE):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT message_id FROM media")
        for row in cursor.fetchall():
            message_id = row[0]
            try:
                await context.bot.get_chat_message(CHANNEL_ID, message_id)
            except Exception as e:
                logger.info(f"Сообщение {message_id} удалено, очистка базы...")
                conn.execute("DELETE FROM media WHERE message_id = ?", (message_id,))
                conn.commit()

def run_loader():
    app = ApplicationBuilder().token(LOADER_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    
    # JobQueue требует установки python-telegram-bot[job-queue]
    app.job_queue.run_repeating(check_channel_updates, interval=3600)
    
    app.run_polling()