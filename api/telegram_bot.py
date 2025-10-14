import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from supabase import create_client, Client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase setup
SUPABASE_URL = os.environ.get('https://ogazgeeqwnhricpjegao.supabase.co')
SUPABASE_KEY = os.environ.get('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nYXpnZWVxd25ocmljcGplZ2FvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAzMzI4NDUsImV4cCI6MjA3NTkwODg0NX0.p9HLWNpCMKQ39-kxm0_XKTDF60hpDOAvcFfEYrURXvc')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Bot token
BOT_TOKEN = os.environ.get('8269825565:AAH5o_NacyhD-7Sw2ahuX3S9u4VVEJf5sxM')

# Create bot
application = Application.builder().token(BOT_TOKEN).build()
bot = application.bot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Hello {user.first_name}! Welcome to Sports Prediction Bot.")

# Webhook handler
def webhook_handler(request):
    return {"status": "ok"}

# Register handlers
application.add_handler(CommandHandler("start", start))
