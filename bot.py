import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from tinydb import TinyDB, Query
from cleanup import cleanup_db
from utils import get_trending_memecoins, filter_scams

TOKEN = os.getenv("BOT_TOKEN")
db = TinyDB('settings.json')
UserSettings = Query()
cleanup_db(db)

# Telegram application
application = Application.builder().token(TOKEN).build()

# Flask app
flask_app = Flask(__name__)

# === Telegram Command Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to the Memecoin Tracker Bot!\n\n"
        "Use /alerts to see trending memecoins.\n"
        "Use /hot to see currently hot memecoins 🔥.\n"
        "Use /settings to configure your alert preferences."
    )
    await update.message.reply_text(welcome_text)

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔔 Set Alert Frequency", callback_data="set_frequency")],
        [InlineKeyboardButton("📈 Set Price Filter", callback_data="set_price_filter")],
        [InlineKeyboardButton("🔍 Enable Rug-Pull Detection", callback_data="enable_rug_detection")],
        [InlineKeyboardButton("⚙️ Select APIs", callback_data="select_api")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Configure Your Alerts:", reply_markup=reply_markup)

async def send_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        memecoins = get_trending_memecoins()
        safe_coins = filter_scams(memecoins)
        message = "\n".join([f"{coin['name']} - ${coin['price']}" for coin in safe_coins])
        await update.message.reply_text(f"📢 Trending Memecoins:\n{message}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching memecoins: {str(e)}")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("settings", settings_menu))
application.add_handler(CommandHandler("alerts", send_alert))

# === Flask Routes ===

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook() -> str:
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        return "OK"
    except Exception as e:
        return f"Webhook error: {e}", 500

@flask_app.route("/", methods=["GET"])
def home():
    return "🚀 Telegram bot is live!"
