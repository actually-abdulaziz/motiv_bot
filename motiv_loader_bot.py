import yt_dlp
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

LOADER_TOKEN = '8012873883:AAHMno1W8YPIkxvCHIwYcI1p1_Y0r_eWUyA'
CHANNEL_ID = -1002576049448
DB_FILE = 'ids.json'

def save_file_id(file_id, file_type):
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = []

    data.append({"file_id": file_id, "type": file_type})
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def download_media(url):
    ydl_opts = {
        'outtmpl': 'temp.%(ext)s',
        'quiet': True,
        'format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
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

app = ApplicationBuilder().token(LOADER_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
print("🚀 motiv_loader_bot запущен")
app.run_polling()
