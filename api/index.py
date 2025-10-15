from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

def send_telegram_message(chat_id, text, reply_markup=None):
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("Received data:", data)
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            if text == '/start':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 Hindi', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 Bangla', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 Urdu', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 Nepali', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                send_telegram_message(
                    chat_id, 
                    "🌍 *Select Your Preferred Language*\n\nPlease choose your language:", 
                    keyboard
                )
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        VERCEL_URL = os.environ.get('VERCEL_URL')
        
        webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://{VERCEL_URL}/webhook"
        response = requests.get(webhook_url)
        
        return jsonify({
            "status": "success",
            "webhook_set": response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
