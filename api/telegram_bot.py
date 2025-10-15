import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Start command from user {user.id}")
    
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
        'en': "✅ You selected English! 🇺🇸",
        'hi': "✅ आपने हिंदी चुनी! 🇮🇳", 
        'bn': "✅ আপনি বাংলা নির্বাচন করেছেন! 🇧🇩",
        'ur': "✅ آپ نے اردو منتخب کی! 🇵🇰",
        'ne': "✅ तपाईंले नेपाली चयन गर्नुभयो! 🇳🇵"
    }
    
    instructions = {
        'en': """🌐 *Step 1 - Register*

‼️ THE ACCOUNT MUST BE NEW

1️⃣ If after clicking the "REGISTER" button you get to the old account, you need to log out of it and click the button again.

2️⃣ Specify a promocode during registration: **FREE**

✅ After REGISTRATION, click the "CHECK REGISTRATION" button""",

        'hi': """🌐 *चरण 1 - पंजीकरण*

‼️ खाता नया होना चाहिए

1️⃣ यदि "REGISTER" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।

2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **FREE**

✅ पंजीकरण के बाद, "CHECK REGISTRATION" बटन पर क्लिक करें"""
    }
    
    keyboard = [
        [
            InlineKeyboardButton("📲 Register", url="https://1w.com/registration?affiliate=FREE"),
            InlineKeyboardButton("✅ Check Registration", callback_data="check_reg")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{messages.get(language_code, '✅ Language selected!')}\n\n{instructions.get(language_code, instructions['en'])}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_polling():
    """Start the bot with polling"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
        
        logger.info("Starting bot polling...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Polling failed: {e}")

# For webhook method (optional)
def webhook_handler(request):
    return {"status": "Using polling method"}
