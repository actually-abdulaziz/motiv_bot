import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from db import init_db, save_file_id

LOADER_TOKEN = 'ТВОЙ_ТОКЕН_ЗАГРУЗЧИКА'
CHANNEL_ID = -1002576049448

def download_media(url):
    ydl_opts = {'outtmpl': 'temp.%(ext)s', 'quiet': True, 'format': 'mp4'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'temp.mp4'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'instagram.com' not in text:
        await update.message.reply_text("⚠️ Это не Instagram-ссылка.")
        return

    await update.message.reply_text("⏬ Скачиваю...")
    try:
        path = download_media(text)
        msg = await context.bot.send_video(chat_id=CHANNEL_ID, video=open(path, 'rb'))
        save_file_id(msg.video.file_id, "video")
        await update.message.reply_text("✅ Загружено и сохранено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(LOADER_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🚀 motiv_loader_bot запущен")
    app.run_polling()
