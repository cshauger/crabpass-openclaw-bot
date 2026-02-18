"""
Simple CrabPass Bot - Groq-powered Telegram bot
"""
import os
import sys
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check required env vars
required_vars = ["TELEGRAM_BOT_TOKEN", "OWNER_TELEGRAM_ID", "GROQ_API_KEY"]
for var in required_vars:
    if not os.environ.get(var):
        logger.error(f"Missing required env var: {var}")
        sys.exit(1)

# Config from environment
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = os.environ.get("MODEL", "llama-3.3-70b-versatile")
BOT_NAME = os.environ.get("BOT_NAME", "CrabPass Bot")

logger.info(f"Starting {BOT_NAME}")
logger.info(f"Owner ID: {OWNER_ID}")
logger.info(f"Model: {MODEL}")

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

groq_client = Groq(api_key=GROQ_API_KEY)

# Conversation history per user
conversations = {}

SYSTEM_PROMPT = """You are a helpful personal AI assistant created by CrabPass.
Be friendly, helpful, and concise. You can use emoji occasionally but don't overdo it.
If you don't know something, say so honestly."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Sorry, this bot is private.")
        return
    await update.message.reply_text(f"👋 Hi! I'm {BOT_NAME}. How can I help you today?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        logger.info(f"Ignoring message from non-owner: {user_id}")
        return
    
    user_message = update.message.text
    logger.info(f"Message from {user_id}: {user_message[:50]}...")
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({"role": "user", "content": user_message})
    conversations[user_id] = conversations[user_id][-20:]
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversations[user_id]
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        
        assistant_message = response.choices[0].message.content
        conversations[user_id].append({"role": "assistant", "content": assistant_message})
        
        await update.message.reply_text(assistant_message)
        
    except Exception as e:
        logger.error(f"Error calling Groq: {e}")
        await update.message.reply_text("Sorry, I encountered an error. Please try again.")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    conversations[update.effective_user.id] = []
    await update.message.reply_text("🧹 Conversation cleared!")


def main():
    logger.info("Building application...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
