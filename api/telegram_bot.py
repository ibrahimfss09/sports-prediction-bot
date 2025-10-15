import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.environ.get('BOT_TOKEN')

logger.info(f"Bot token exists: {bool(BOT_TOKEN)}")

# Create bot application
try:
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info("Bot application created successfully")
except Exception as e:
    logger.error(f"Failed to create bot application: {e}")
    application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Start command received from user: {user.id}")
    
    try:
        await update.message.reply_text(
            f"🚀 **Welcome {user.first_name}!**\n\n"
            "✅ Bot is working!\n\n"
            "🌍 Select your language:\n"
            "• 🇺🇸 English - Type /english\n"
            "• 🇮🇳 Hindi - Type /hindi\n"
            "• 🇧🇩 Bangla - Type /bangla\n"
            "• 🇵🇰 Urdu - Type /urdu\n" 
            "• 🇳🇵 Nepali - Type /nepali"
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Step 1 - Register*\n\n"
        "‼️ THE ACCOUNT MUST BE NEW\n\n"
        "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, "
        "you need to log out of it and click the button again.\n\n"
        "2️⃣ Specify a promocode during registration: **FREE**\n\n"
        "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button\n\n"
        "[📲 Register Now](https://1w.com/registration?affiliate=FREE)",
        parse_mode='Markdown'
    )

async def hindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *चरण 1 - पंजीकरण*\n\n"
        "‼️ खाता नया होना चाहिए\n\n"
        "1️⃣ यदि \"REGISTER\" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, "
        "तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।\n\n"
        "2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **FREE**\n\n"
        "✅ पंजीकरण के बाद, \"CHECK REGISTRATION\" बटन पर क्लिक करें\n\n"
        "[📲 अभी पंजीकरण करें](https://1w.com/registration?affiliate=FREE)",
        parse_mode='Markdown'
    )

# Add other language commands similarly...

# Register handlers
if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("english", english))
    application.add_handler(CommandHandler("hindi", hindi))
    # Add other commands...
    logger.info("Handlers registered successfully")
else:
    logger.error("Application not initialized - cannot register handlers")
