"""
Simple CrabPass Bot - Groq-powered Telegram bot
No OpenClaw dependency, direct Groq API integration
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Config from environment
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = os.environ.get("MODEL", "llama-3.3-70b-versatile")
BOT_NAME = os.environ.get("BOT_NAME", "CrabPass Bot")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Only respond to owner
    if user_id != OWNER_ID:
        return
    
    user_message = update.message.text
    
    # Get or create conversation history
    if user_id not in conversations:
        conversations[user_id] = []
    
    # Add user message to history
    conversations[user_id].append({"role": "user", "content": user_message})
    
    # Keep last 20 messages for context
    conversations[user_id] = conversations[user_id][-20:]
    
    try:
        # Call Groq
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
        
        # Add assistant response to history
        conversations[user_id].append({"role": "assistant", "content": assistant_message})
        
        await update.message.reply_text(assistant_message)
        
    except Exception as e:
        logger.error(f"Error calling Groq: {e}")
        await update.message.reply_text("Sorry, I encountered an error. Please try again.")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    if update.effective_user.id != OWNER_ID:
        return
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("🧹 Conversation cleared!")


def main():
    logger.info(f"Starting {BOT_NAME}...")
    logger.info(f"Owner ID: {OWNER_ID}")
    logger.info(f"Model: {MODEL}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
