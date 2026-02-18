"""Minimal test bot"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=== STARTING ===")
logger.info(f"TOKEN present: {bool(os.environ.get('TELEGRAM_BOT_TOKEN'))}")
logger.info(f"OWNER present: {bool(os.environ.get('OWNER_TELEGRAM_ID'))}")
logger.info(f"GROQ present: {bool(os.environ.get('GROQ_API_KEY'))}")

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    logger.info("Telegram imports OK")
except Exception as e:
    logger.error(f"Import error: {e}")
    raise

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("No BOT_TOKEN!")
    exit(1)

async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm alive!")

async def echo(update: Update, context):
    await update.message.reply_text(f"You said: {update.message.text}")

def main():
    logger.info("Building app...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    logger.info("Starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
