"""
Simple CrabPass Bot - Groq via HTTP
Minimal dependencies - just telegram and requests
"""
import os
import sys
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check required env vars
for var in ["TELEGRAM_BOT_TOKEN", "OWNER_TELEGRAM_ID", "GROQ_API_KEY"]:
    if not os.environ.get(var):
        logger.error(f"Missing: {var}")
        sys.exit(1)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_TELEGRAM_ID"])
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = os.environ.get("MODEL", "llama-3.3-70b-versatile")

logger.info(f"Bot starting, owner={OWNER_ID}, model={MODEL}")

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

conversations = {}

SYSTEM_PROMPT = "You are a helpful AI assistant. Be concise and friendly."


def call_groq(messages):
    """Call Groq API directly via HTTP"""
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        },
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("👋 Hi! How can I help?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid != OWNER_ID:
        return
    
    msg = update.message.text
    logger.info(f"Got: {msg[:30]}...")
    
    if uid not in conversations:
        conversations[uid] = []
    
    conversations[uid].append({"role": "user", "content": msg})
    conversations[uid] = conversations[uid][-10:]
    
    try:
        reply = call_groq([
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversations[uid]
        ])
        conversations[uid].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Groq error: {e}")
        await update.message.reply_text(f"Error: {e}")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    conversations[update.effective_user.id] = []
    await update.message.reply_text("🧹 Cleared!")


def main():
    logger.info("Building app...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
