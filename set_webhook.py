import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def set_webhook():
    bot = Bot(token=TOKEN)
    await bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    print(f"✅ Webhook set to: {WEBHOOK_URL}/{TOKEN}")

asyncio.run(set_webhook())
