import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Пример: -1002576049448

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔁 Отправляю случайный мотивационный пост...")

    async for message in context.bot.get_chat(CHANNEL_ID).iter_history(limit=None):
        context.bot_data.setdefault("messages", []).append(message.message_id)

    if not context.bot_data["messages"]:
        await update.message.reply_text("❌ Нет доступных постов в канале.")
        return

    random_id = random.choice(context.bot_data["messages"])

    await context.bot.forward_message(
        chat_id=update.effective_chat.id,
        from_chat_id=CHANNEL_ID,
        message_id=random_id
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()
