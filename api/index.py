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
                
                # Then send language selection
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 Hindi', 'callback_data': 'lang_hi'}]
                    ]
                }
                
                payload2 = {
                    'chat_id': chat_id,
                    'text': '🌍 *Select Your Language:*',
                    'reply_markup': keyboard,
                    'parse_mode': 'Markdown'
                }
                response2 = requests.post(url, json=payload2)
                print("📤 Sent language:", response2.json())
        
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
