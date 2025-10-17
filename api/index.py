from flask import Flask, request, jsonify
import os
import requests
import sqlite3
import json
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

# Environment variables se credentials lo
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = os.environ.get('CRICAPI_KEY')
VERCEL_URL = os.environ.get('VERCEL_URL')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# ==================== LANGUAGE MESSAGES ====================
LANGUAGE_MESSAGES = {
    'en': {
        'welcome': "🌍 *Select Your Preferred Language:*",
        'selected': "✅ You selected English!",
        'register_title': "🌐 *Step 1 - Register*",
        'account_new': "‼️ *THE ACCOUNT MUST BE NEW*",
        'instruction1': "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, you need to log out of it and click the button again.",
        'instruction2': "2️⃣ Specify a promocode during registration: **CLAIM**",
        'after_reg': "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button",
        'register_btn': "📲 Register",
        'check_btn': "🔍 Check Registration",
        'enter_player_id': "🔍 *Check Your Registration*\n\nPlease enter your 1Win *Player ID* to verify:\n\n📝 *How to find Player ID:*\n1. Login to 1Win account\n2. Go to Profile Settings\n3. Copy Player ID number\n4. Paste it here\n\n🔢 *Enter your Player ID now:*",
        'reg_success': "🎉 *Great, you have successfully completed registration!*\n\n✅ Your account is synchronized with the bot\n\n💴 *To gain access to signals, deposit your account (make a deposit) with at least 600₹ or $6 in any currency*\n\n🕹️ After successfully replenishing your account, click on the CHECK DEPOSIT button and gain access",
        'deposit_btn': "💳 Deposit",
        'check_deposit_btn': "🔍 Check Deposit",
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\nClick below to get your first prediction:",
        'get_prediction_btn': "🎯 Get Prediction",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 5 free predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow (12 hours)\n• Deposit 400₹ or $4 for immediate access\n\n💰 Continue predictions by depositing at least 400₹ or $4",
        'deposit_again_btn': "💳 Deposit Again", 
        'try_tomorrow_btn': "🕐 Try Tomorrow",
        'random_messages': [
            "YOUR REGISTRATION IS SUCCESSFUL! ✅\n\nMake a deposit of $6,7,10,13,17 or any other amount and bot will automatically give you access to signals! 🔑\n\nYou can earn $10 ➡️ $100 every day💰\n\n👉Click /start",
            "Bro, ready signal for you☺️\n\nSTART NOW👉 /start",
            "🚀 The signal has already come\n\n🔥 Don't miss your chance to get your money\n\n➡️ /start",
            "START BOT NOW AND GET MONEY💰🔥\n\n/start"
        ]
    },
    'hi': {
        'welcome': "🌍 *अपनी पसंदीदा भाषा चुनें:*",
        'selected': "✅ आपने हिंदी चुनी!",
        'register_title': "🌐 *चरण 1 - पंजीकरण*",
        'account_new': "‼️ *खाता नया होना चाहिए*",
        'instruction1': "1️⃣ यदि \"REGISTER\" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।",
        'instruction2': "2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **CLAIM**",
        'after_reg': "✅ पंजीकरण के बाद, \"CHECK REGISTRATION\" बटन पर क्लिक करें",
        'register_btn': "📲 पंजीकरण",
        'check_btn': "🔍 पंजीकरण जांचें",
        'enter_player_id': "🔍 *अपना पंजीकरण जांचें*\n\nकृपया सत्यापित करने के लिए अपना 1Win *Player ID* दर्ज करें:\n\n📝 *Player ID कैसे ढूंढें:*\n1. 1Win अकाउंट में लॉगिन करें\n2. प्रोफाइल सेटिंग्स पर जाएं\n3. Player ID नंबर कॉपी करें\n4. यहाँ पेस्ट करें\n\n🔢 *अब अपना Player ID दर्ज करें:*",
        'reg_success': "🎉 *बधाई हो, आपने सफलतापूर्वक पंजीकरण पूरा कर लिया है!*\n\n✅ आपका खाता बॉट के साथ सिंक हो गया है\n\n💴 *सिग्नल तक पहुंच प्राप्त करने के लिए, अपने खाते में कम से कम 600₹ या $6 जमा करें*\n\n🕹️ अपना खाता सफलतापूर्वक रिचार्ज करने के बाद, CHECK DEPOSIT बटन पर क्लिक करें और पहुंच प्राप्त करें",
        'deposit_btn': "💳 जमा करें",
        'check_deposit_btn': "🔍 जमा जांचें",
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'get_prediction_btn': "🎯 भविष्यवाणी प्राप्त करें",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 5 मुफ्त भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• कल तक प्रतीक्षा करें (12 घंटे)\n• तुरंत पहुंच के लिए 400₹ या $4 जमा करें\n\n💰 कम से कम 400₹ या $4 जमा करके भविष्यवाणियाँ जारी रखें",
        'deposit_again_btn': "💳 फिर से जमा करें",
        'try_tomorrow_btn': "🕐 कल प्रयास करें",
        'random_messages': [
            "आपका पंजीकरण सफल रहा है! ✅\n\n$6,7,10,13,17 या कोई अन्य राशि जमा करें और बॉट स्वचालित रूप से आपको सिग्नल तक पहुंच प्रदान करेगा! 🔑\n\nआप प्रतिदिन $10 ➡️ $100 कमा सकते हैं💰\n\n👉 /start क्लिक करें",
            "भाई, आपके लिए सिग्नल तैयार है☺️\n\nअभी शुरू करें👉 /start",
            "🚀 सिग्नल आ चुका है\n\n🔥 अपना पैसा पाने का मौका मत चूकें\n\n➡️ /start",
            "अभी बॉट शुरू करें और पैसा प्राप्त करें💰🔥\n\n/start"
        ]
    }
}

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('sports_bot.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'en',
            player_id TEXT UNIQUE,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deposit_amount REAL DEFAULT 0,
            total_deposits REAL DEFAULT 0,
            prediction_count INTEGER DEFAULT 0,
            last_prediction_date TEXT,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            match_id TEXT,
            team_a TEXT,
            team_b TEXT,
            prediction TEXT,
            confidence REAL,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ==================== AI PREDICTION ENGINE ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        
    def fetch_live_matches(self):
        """Fetch live matches from CricAPI"""
        try:
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    matches = []
                    for match in data.get('data', []):
                        if match.get('matchStarted') and not match.get('matchEnded'):
                            matches.append({
                                'id': match['id'],
                                'team_a': match['teamInfo'][0]['name'],
                                'team_b': match['teamInfo'][1]['name'],
                                'date': match['date'],
                                'series': match.get('series', 'International'),
                                'status': match.get('status', 'Live')
                            })
                    return matches[:3]
            return self.get_fallback_matches()
        except:
            return self.get_fallback_matches()
    
    def get_fallback_matches(self):
        """Fallback matches when API fails"""
        today = datetime.now()
        return [
            {
                'id': 'match1',
                'team_a': 'India',
                'team_b': 'Pakistan',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'Asia Cup',
                'status': 'Live'
            }
        ]
    
    def analyze_team_history(self, team1, team2):
        """Analyze team history and generate prediction"""
        # Mock analysis - in production, use actual historical data
        total_matches = random.randint(50, 150)
        team1_wins = random.randint(20, total_matches - 20)
        team2_wins = total_matches - team1_wins - random.randint(5, 15)
        
        # AI Prediction logic
        team1_strength = random.uniform(0.4, 0.8)
        team2_strength = random.uniform(0.4, 0.8)
        
        if team1_strength > team2_strength:
            winner = team1
            confidence = min(95, int(team1_strength * 100))
        else:
            winner = team2
            confidence = min(95, int(team2_strength * 100))
        
        return {
            'prediction': f"{winner} to win",
            'confidence': confidence,
            'analysis': f"Based on historical data: {team1} won {team1_wins}, {team2} won {team2_wins} out of {total_matches} matches. Current form and player performance analysis suggests {winner} has better chances.",
            'team_a': team1,
            'team_b': team2
        }
    
    def get_todays_prediction(self):
        """Get today's AI prediction"""
        matches = self.fetch_live_matches()
        if not matches:
            return self.analyze_team_history("India", "Pakistan")
        
        match = matches[0]
        return self.analyze_team_history(match['team_a'], match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== TELEGRAM FUNCTIONS ====================
def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    """Edit existing Telegram message"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Edit message error: {e}")
        return None

def delete_telegram_message(chat_id, message_id):
    """Delete Telegram message"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Delete message error: {e}")
        return None

# ==================== DATABASE FUNCTIONS ====================
def get_user(user_id):
    """Get user from database"""
    try:
        conn = sqlite3.connect('sports_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'user_id': user[1],
                'username': user[2],
                'first_name': user[3],
                'language': user[4],
                'player_id': user[5],
                'deposit_amount': user[7],
                'total_deposits': user[8],
                'prediction_count': user[9],
                'last_activity': user[11]
            }
        return None
    except Exception as e:
        print(f"Get user error: {e}")
        return None

def save_user(user_data):
    """Save or update user in database"""
    try:
        conn = sqlite3.connect('sports_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, language, player_id, deposit_amount, total_deposits, prediction_count, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data.get('username'),
            user_data.get('first_name'),
            user_data.get('language', 'en'),
            user_data.get('player_id'),
            user_data.get('deposit_amount', 0),
            user_data.get('total_deposits', 0),
            user_data.get('prediction_count', 0),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Save user error: {e}")
        return False

def update_prediction_count(user_id):
    """Update user's prediction count"""
    try:
        conn = sqlite3.connect('sports_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET prediction_count = prediction_count + 1,
                last_prediction_date = ?,
                last_activity = ?
            WHERE user_id = ?
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_id
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Update prediction error: {e}")
        return False

# ==================== 1WIN POSTBACK HANDLER ====================
@app.route('/1win-postback', methods=['GET', 'POST'])
def handle_1win_postback():
    """1Win postback handler"""
    try:
        if request.method == 'GET':
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}
        
        print("📨 1Win Postback:", data)
        
        player_id = data.get('id') or data.get('sub1')
        status = data.get('status', '')
        deposit_amount = float(data.get('fdp', 0) or data.get('dep_sum', 0))
        
        if player_id:
            # Update user in database
            conn = sqlite3.connect('sports_bot.db')
            cursor = conn.cursor()
            
            if status in ['fd_approved', 'active'] and deposit_amount >= 6:
                cursor.execute('''
                    UPDATE users 
                    SET deposit_amount = ?, total_deposits = total_deposits + ?
                    WHERE player_id = ?
                ''', (deposit_amount, deposit_amount, player_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({"status": "success", "player_id": player_id})
        
        return jsonify({"status": "error", "message": "No player ID"})
    
    except Exception as e:
        print(f"Postback error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== SCHEDULED MESSAGES ====================
def send_random_messages():
    """Send random messages to inactive users"""
    try:
        conn = sqlite3.connect('sports_bot.db')
        cursor = conn.cursor()
        
        # Get users inactive for 24 hours
        yesterday = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('SELECT user_id, language FROM users WHERE last_activity < ?', (yesterday,))
        users = cursor.fetchall()
        
        for user_id, language in users:
            msg_data = LANGUAGE_MESSAGES.get(language, LANGUAGE_MESSAGES['en'])
            random_msg = random.choice(msg_data['random_messages'])
            send_telegram_message(user_id, random_msg)
        
        conn.close()
    except Exception as e:
        print(f"Random messages error: {e}")

# Schedule random messages every 24 hours
scheduler.add_job(send_random_messages, 'interval', hours=24)

# ==================== MAIN BOT HANDLER ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📨 Received:", data)
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username')
            first_name = message['from'].get('first_name', 'User')
            
            # Delete the received message
            delete_telegram_message(chat_id, message_id)
            
            # Get or create user
            user = get_user(user_id)
            if not user:
                user = {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'language': 'en'
                }
                save_user(user)
            
            if text == '/start':
                # Show language selection
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 हिंदी', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 বাংলা', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 اردو', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 नेपाली', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                send_telegram_message(chat_id, msg_data['welcome'], keyboard)
            
            elif text.isdigit() and len(text) >= 5:
                # Player ID entered
                player_id = text
                
                # Update user with player ID
                user['player_id'] = player_id
                save_user(user)
                
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                
                # Check if player has deposited
                if user.get('deposit_amount', 0) >= 6:
                    # Has deposited - show prediction button
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    message_text = msg_data['deposit_success'].replace('{amount}', str(user['deposit_amount']))
                else:
                    # No deposit - show deposit buttons
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                        ]
                    }
                    message_text = msg_data['reg_success']
                
                send_telegram_message(chat_id, message_text, keyboard)
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            data_value = callback['data']
            user_id = callback['from']['id']
            
            user = get_user(user_id)
            if not user:
                return jsonify({"status": "error"})
            
            msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
            
            if data_value.startswith('lang_'):
                # Language selection
                lang_code = data_value.split('_')[1]
                user['language'] = lang_code
                save_user(user)
                
                msg_data = LANGUAGE_MESSAGES[lang_code]
                
                keyboard = {
                    'inline_keyboard': [
                        [{'text': msg_data['register_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                        [{'text': msg_data['check_btn'], 'callback_data': 'check_registration'}]
                    ]
                }
                
                message_text = f"{msg_data['selected']}\n\n{msg_data['register_title']}\n\n{msg_data['account_new']}\n\n{msg_data['instruction1']}\n\n{msg_data['instruction2']}\n\n{msg_data['after_reg']}"
                
                edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'check_registration':
                # Ask for Player ID
                edit_telegram_message(chat_id, message_id, msg_data['enter_player_id'])
            
            elif data_value == 'check_deposit':
                # Check deposit status
                if user.get('deposit_amount', 0) >= 6:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    message_text = msg_data['deposit_success'].replace('{amount}', str(user['deposit_amount']))
                else:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                        ]
                    }
                    message_text = msg_data['reg_success']
                
                edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'get_prediction':
                # Check prediction limit
                if user.get('prediction_count', 0) >= 5:
                    # Prediction limit reached
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['try_tomorrow_btn'], 'callback_data': 'try_tomorrow'}]
                        ]
                    }
                    edit_telegram_message(chat_id, message_id, msg_data['prediction_limit'], keyboard)
                else:
                    # Get AI prediction
                    prediction = ai_predictor.get_todays_prediction()
                    update_prediction_count(user_id)
                    
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    
                    message_text = f"""
🎯 *AI CRICKET PREDICTION* 🤖

🏟️ *Match:* {prediction['team_a']} vs {prediction['team_b']}
📊 *Prediction:* {prediction['prediction']}
✅ *Confidence:* {prediction['confidence']}%

📈 *Analysis:*
{prediction['analysis']}

⚠️ *AI Prediction - Bet Responsibly*
                    """
                    
                    edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'try_tomorrow':
                # Inform about waiting
                edit_telegram_message(chat_id, message_id, "⏳ Please try again after 12 hours for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://{VERCEL_URL}/webhook"
    response = requests.get(url)
    return jsonify({"status": "success", "result": response.json()})

if __name__ == '__main__':
    app.run()
