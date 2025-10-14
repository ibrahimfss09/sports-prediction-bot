from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Sports Prediction Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    return {"status": "webhook received"}

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    return {"status": "webhook endpoint ready"}

if __name__ == '__main__':
    app.run(debug=True)
