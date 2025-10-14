import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from supabase import create_client, Client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables se credentials lo
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Supabase setup
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Supabase connection error: {e}")
    supabase = None

# Create bot application
try:
    application = Application.builder().token(BOT_TOKEN).build()
    bot = application.bot
except Exception as e:
    logger.error(f"Bot creation error: {e}")
    application = None
    bot = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Language selection keyboard
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton("🇧🇩 Bangla", callback_data="lang_bn")],
        [InlineKeyboardButton("🇵🇰 Urdu", callback_data="lang_ur")],
        [InlineKeyboardButton("🇳🇵 Nepali", callback_data="lang_ne")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 *Select Your Preferred Language*\n\n"
        "Please choose your language:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language_code = query.data.split('_')[1]
    
    # Language messages
    messages = {
        'en': "You selected English! 🇺🇸",
        'hi': "आपने हिंदी चुनी! 🇮🇳",
        'bn': "আপনি বাংলা নির্বাচন করেছেন! 🇧🇩",
        'ur': "آپ نے اردو منتخب کی! 🇵🇰",
        'ne': "तपाईंले नेपाली चयन गर्नुभयो! 🇳🇵"
    }
    
    await query.edit_message_text(
        f"{messages.get(language_code, 'Language selected!')}\n\n"
        "🌐 *Step 1 - Register*\n\n"
        "‼️ THE ACCOUNT MUST BE NEW\n\n"
        "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, "
        "you need to log out of it and click the button again.\n\n"
        "2️⃣ Specify a promocode during registration: **FREE**\n\n"
        "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button",
        parse_mode='Markdown'
    )

# Webhook handler
def webhook_handler(request):
    try:
        from flask import jsonify
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# Register handlers
if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
