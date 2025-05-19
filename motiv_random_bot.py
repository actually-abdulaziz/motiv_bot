import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

VIEWER_TOKEN = '7860361239:AAFaD60SyLaF5gEqXfyTpsHkgWLOgHjkpTE'
DB_FILE = 'ids.json'

def load_random():
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    return random.choice(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 Мотивация", callback_data='random')]]
    await update.message.reply_text("Нажми кнопку — получи мотивацию", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    content = load_random()

    if content['type'] == 'video':
        await query.message.reply_video(content['file_id'])
    else:
        await query.message.reply_photo(content['file_id'])

app = ApplicationBuilder().token(VIEWER_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
print("🎲 motiv_random_bot запущен")
app.run_polling()