from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📨 Received:", data)
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            BOT_TOKEN = os.environ.get('BOT_TOKEN')
            
            if text == '/start':
                # Simple text message first
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': '🚀 *Welcome to Sports Prediction Bot!*\n\nPlease wait...',
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, json=payload)
                print("📤 Sent welcome:", response.json())
                
                # Language selection with ALL 5 languages
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 Hindi', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 Bangla', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 Urdu', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 Nepali', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                payload2 = {
                    'chat_id': chat_id,
                    'text': '🌍 *Select Your Preferred Language:*',
                    'reply_markup': keyboard,
                    'parse_mode': 'Markdown'
                }
                response2 = requests.post(url, json=payload2)
                print("📤 Sent language:", response2.json())
        
        elif 'callback_query' in data:
            # Handle language selection
            callback_data = data['callback_query']
            chat_id = callback_data['message']['chat']['id']
            data_value = callback_data['data']
            
            BOT_TOKEN = os.environ.get('BOT_TOKEN')
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
            if data_value.startswith('lang_'):
                lang_code = data_value.split('_')[1]
                
                # Language names
                lang_names = {
                    'en': 'English',
                    'hi': 'Hindi', 
                    'bn': 'Bangla',
                    'ur': 'Urdu',
                    'ne': 'Nepali'
                }
                
                lang_name = lang_names.get(lang_code, 'English')
                
                # Registration instructions
                message_text = f"""
✅ You selected {lang_name}!

🌐 *Step 1 - Register*

‼️ THE ACCOUNT MUST BE NEW

1️⃣ If after clicking the "REGISTER" button you get to the old account, you need to log out of it and click the button again.

2️⃣ Specify a promocode during registration: **FREE**

✅ After REGISTRATION, click the "CHECK REGISTRATION" button

💵 Minimum Deposit: $10
📊 Free Predictions: 5 predictions
                """
                
                # Register buttons
                keyboard = {
                    'inline_keyboard': [
                        [
                            {'text': '📲 REGISTER', 'url': 'https://lkxd.cc/98a4'},
                            {'text': '✅ CHECK REGISTRATION', 'callback_data': 'check_reg'}
                        ]
                    ]
                }
                
                payload = {
                    'chat_id': chat_id,
                    'text': message_text,
                    'reply_markup': keyboard,
                    'parse_mode': 'Markdown'
                }
                requests.post(url, json=payload)
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    VERCEL_URL = os.environ.get('VERCEL_URL')
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://{VERCEL_URL}/webhook"
    response = requests.get(url)
    
    return jsonify({
        "status": "success", 
        "result": response.json()
    })

if __name__ == '__main__':
    app.run()
