from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "success", "message": "Webhook received"})

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
