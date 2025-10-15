from flask import Flask, request, jsonify
import os
import asyncio
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Import and start bot
def start_bot():
    try:
        from api.telegram_bot import start_polling
        asyncio.run(start_polling())
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")

# Start bot in background thread
@app.before_first_request
def startup():
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Bot polling started in background")

@app.route('/')
def home():
    return "Sports Prediction Bot is Running with Polling!"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    return jsonify({"status": "Using polling method - no webhook needed"})

if __name__ == '__main__':
    app.run(debug=True)
