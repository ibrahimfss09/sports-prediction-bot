import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, CallbackContext
)
from supabase import create_client, Client
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase setup
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Bot token from environment
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Currency conversion rates
CURRENCY_RATES = {
    'INR': 83.0,
    'BDT': 110.0,
    'PKR': 280.0,
    'NPR': 133.0,
    'USD': 1.0
}

# Language mapping
LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇺🇸'},
    'hi': {'name': 'Hindi', 'flag': '🇮🇳'},
    'bn': {'name': 'Bangla', 'flag': '🇧🇩'},
    'ur': {'name': 'Urdu', 'flag': '🇵🇰'},
    'ne': {'name': 'Nepali', 'flag': '🇳🇵'}
}

# Create bot application
application = Application.builder().token(BOT_TOKEN).build()
bot = application.bot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Check if user exists
    user_data = supabase.table('users').select('*').eq('user_id', user_id).execute()
    
    if not user_data.data:
        # Create new user
        supabase.table('users').insert({
            'user_id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language': 'en',
            'currency': 'USD'
        }).execute()
    
    # Show language selection
    await show_language_selection(update, context)

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    
    for code, info in LANGUAGES.items():
        button = InlineKeyboardButton(
            f"{info['flag']} {info['name']}", 
            callback_data=f"lang_{code}"
        )
        keyboard.append([button])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 *Select Your Preferred Language*\n\nPlease choose your language:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    # Update user language
    supabase.table('users').update({
        'language': language_code,
        'currency': get_currency_for_language(language_code)
    }).eq('user_id', user_id).execute()
    
    # Show registration instructions
    await show_registration_instructions(query, context, language_code)

def get_currency_for_language(lang_code):
    currency_map = {
        'en': 'USD',
        'hi': 'INR', 
        'bn': 'BDT',
        'ur': 'PKR',
        'ne': 'NPR'
    }
    return currency_map.get(lang_code, 'USD')

async def show_registration_instructions(query, context: ContextTypes.DEFAULT_TYPE, lang_code):
    user_id = query.from_user.id
    user_data = supabase.table('users').select('*').eq('user_id', user_id).execute()
    currency = user_data.data[0]['currency'] if user_data.data else 'USD'
    
    min_deposit_local = 10 * CURRENCY_RATES.get(currency, 1)
    additional_deposit_local = 3.5 * CURRENCY_RATES.get(currency, 1)
    
    messages = {
        'en': {
            'title': "🌐 *Step 1 - Register*",
            'instructions': f"""
‼️ *THE ACCOUNT MUST BE NEW*

1️⃣ If after clicking the "REGISTER" button you get to the old account, you need to log out of it and click the button again.

2️⃣ Specify a promocode during registration: **FREE**

✅ After REGISTRATION, click the "CHECK REGISTRATION" button

💳 *Minimum Deposit:* {min_deposit_local:.2f} {currency}
📊 *Free Predictions:* 5 predictions
🔄 *Additional Predictions:* Deposit {additional_deposit_local:.2f} {currency} for more predictions
            """,
            'register_btn': "📲 Register",
            'check_btn': "✅ Check Registration"
        },
        'hi': {
            'title': "🌐 *चरण 1 - पंजीकरण*",
            'instructions': f"""
‼️ *खाता नया होना चाहिए*

1️⃣ यदि "REGISTER" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।

2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **FREE**

✅ पंजीकरण के बाद, "CHECK REGISTRATION" बटन पर क्लिक करें

💳 *न्यूनतम जमा:* {min_deposit_local:.2f} {currency}
📊 *मुफ्त भविष्यवाणियाँ:* 5 भविष्यवाणियाँ
🔄 *अतिरिक्त भविष्यवाणियाँ:* अधिक भविष्यवाणियों के लिए {additional_deposit_local:.2f} {currency} जमा करें
            """,
            'register_btn': "📲 पंजीकरण",
            'check_btn': "✅ पंजीकरण जांचें"
        }
    }
    
    msg_data = messages.get(lang_code, messages['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(msg_data['register_btn'], url="https://lkxd.cc/98a4"),
            InlineKeyboardButton(msg_data['check_btn'], callback_data="check_registration")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{msg_data['title']}\n\n{msg_data['instructions']}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def check_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = supabase.table('users').select('*').eq('user_id', user_id).execute()
    
    if user_data.data and user_data.data[0]['is_registered'] and user_data.data[0]['deposit_amount'] >= 10:
        lang_code = user_data.data[0]['language']
        prediction_count = user_data.data[0]['prediction_count']
        
        if prediction_count < 5:
            await send_prediction(query, context, lang_code)
        else:
            await show_deposit_required(query, context, lang_code)
    else:
        lang_code = user_data.data[0]['language'] if user_data.data else 'en'
        await query.edit_message_text(
            "❌ *Registration Not Found*\n\nPlease complete registration and minimum deposit to get predictions.",
            parse_mode='Markdown'
        )

async def send_prediction(query, context: ContextTypes.DEFAULT_TYPE, lang_code):
    user_id = query.from_user.id
    
    # Mock prediction
    prediction = {
        'match_id': 'match_001',
        'team_a': 'India',
        'team_b': 'Australia', 
        'prediction': 'India to win',
        'confidence': 78.5,
        'analysis': 'Based on recent form and head-to-head records'
    }
    
    # Update prediction count
    user_data = supabase.table('users').select('*').eq('user_id', user_id).execute()
    current_count = user_data.data[0]['prediction_count']
    supabase.table('users').update({'prediction_count': current_count + 1}).eq('user_id', user_id).execute()
    
    # Save prediction
    supabase.table('predictions').insert({
        'user_id': user_id,
        'match_id': prediction['match_id'],
        'team_a': prediction['team_a'],
        'team_b': prediction['team_b'],
        'prediction': prediction['prediction'],
        'confidence': prediction['confidence']
    }).execute()
    
    await query.edit_message_text(
        f"🎯 *Prediction Result*\n\n"
        f"🏏 **Match:** {prediction['team_a']} vs {prediction['team_b']}\n"
        f"📊 **Prediction:** {prediction['prediction']}\n"
        f"✅ **Confidence:** {prediction['confidence']}%\n"
        f"📈 **Analysis:** {prediction['analysis']}\n\n"
        f"🔢 Predictions used: {current_count + 1}/5",
        parse_mode='Markdown'
    )

async def show_deposit_required(query, context: ContextTypes.DEFAULT_TYPE, lang_code):
    user_id = query.from_user.id
    user_data = supabase.table('users').select('*').eq('user_id', user_id).execute()
    currency = user_data.data[0]['currency']
    
    deposit_amount = 3.5 * CURRENCY_RATES.get(currency, 1)
    
    messages = {
        'en': f"🚫 *Prediction Limit Reached*\n\nYou've used all 5 free predictions. Please deposit at least {deposit_amount:.2f} {currency} to continue.",
        'hi': f"🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने सभी 5 मुफ्त भविष्यवाणियों का उपयोग कर लिया है। कृपया और भविष्यवाणियाँ प्राप्त करने के लिए कम से कम {deposit_amount:.2f} {currency} जमा करें।"
    }
    
    keyboard = [
        [InlineKeyboardButton("💳 Deposit Now", url="https://lkxd.cc/98a4")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        messages.get(lang_code, messages['en']),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Webhook handler
def webhook_handler(request):
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return {"status": "ok"}

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
application.add_handler(CallbackQueryHandler(check_registration, pattern="^check_registration"))
