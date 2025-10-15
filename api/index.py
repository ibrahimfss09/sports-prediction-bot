from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Language mapping
LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇺🇸'},
    'hi': {'name': 'Hindi', 'flag': '🇮🇳'},
    'bn': {'name': 'Bangla', 'flag': '🇧🇩'},
    'ur': {'name': 'Urdu', 'flag': '🇵🇰'},
    'ne': {'name': 'Nepali', 'flag': '🇳🇵'}
}

def send_telegram_message(chat_id, text, reply_markup=None):
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            if text == '/start':
                # Language selection keyboard
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 Hindi', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 Bangla', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 Urdu', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 Nepali', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                message_text = (
                    "🌍 <b>Select Your Preferred Language</b>\n\n"
                    "Please choose your language:"
                )
                
                send_telegram_message(chat_id, message_text, keyboard)
        
        elif 'callback_query' in data:
            callback_data = data['callback_query']
            chat_id = callback_data['message']['chat']['id']
            data_value = callback_data['data']
            
            if data_value.startswith('lang_'):
                lang_code = data_value.split('_')[1]
                lang_name = LANGUAGES.get(lang_code, {}).get('name', 'Unknown')
                
                # Registration instructions
                message_text = (
                    f"✅ You selected {lang_name}!\n\n"
                    "🌐 <b>Step 1 - Register</b>\n\n"
                    "‼️ <b>THE ACCOUNT MUST BE NEW</b>\n\n"
                    "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, "
                    "you need to log out of it and click the button again.\n\n"
                    "2️⃣ Specify a promocode during registration: <b>FREE</b>\n\n"
                    "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button\n\n"
                    "💵 <b>Minimum Deposit: $10</b>\n"
                    "📊 <b>Free Predictions: 5</b>"
                )
                
                # Register button
                keyboard = {
                    'inline_keyboard': [
                        [
                            {'text': '📲 REGISTER', 'url': 'https://1w.com/registration?affiliate=FREE'},
                            {'text': '✅ CHECK REGISTRATION', 'callback_data': 'check_reg'}
                        ]
                    ]
                }
                
                send_telegram_message(chat_id, message_text, keyboard)
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        VERCEL_URL = os.environ.get('VERCEL_URL')
        
        if not BOT_TOKEN:
            return jsonify({"error": "BOT_TOKEN not set"})
        
        webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://{VERCEL_URL}/webhook"
        response = requests.get(webhook_url)
        
        return jsonify({
            "status": "success",
            "webhook_set": response.json(),
            "webhook_url": f"https://{VERCEL_URL}/webhook"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
