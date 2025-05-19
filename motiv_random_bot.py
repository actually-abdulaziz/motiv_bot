from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from db import init_db, get_random

VIEWER_TOKEN = 'ТВОЙ_ТОКЕН_ВЬЮЕРА'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 Мотивация", callback_data='random')]]
    await update.message.reply_text("Нажми кнопку — получи мотивацию", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    content = get_random()
    if not content:
        await query.message.reply_text("⛔ База пуста.")
        return

    if content['type'] == 'video':
        await query.message.reply_video(content['file_id'])
    else:
        await query.message.reply_photo(content['file_id'])

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(VIEWER_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("🎲 motiv_random_bot запущен")
    app.run_polling()
