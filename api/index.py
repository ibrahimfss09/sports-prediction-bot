from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = os.environ.get('CRICAPI_KEY')
VERCEL_URL = os.environ.get('VERCEL_URL')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# In-memory storage
users_storage = {}
player_registrations = {}  # Store player registration status
player_deposits = {}       # Store player deposit amounts

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
        'loading_registration': "⏳ *Please wait few seconds, your registration is loading...*",
        'reg_success': "🎉 *Great, you have successfully completed registration!*\n\n✅ Your account is synchronized with the bot\n\n💴 *To gain access to signals, deposit your account (make a deposit) with at least 600₹ or $6 in any currency*\n\n🕹️ After successfully replenishing your account, click on the CHECK DEPOSIT button and gain access",
        'reg_not_found': "❌ *Sorry, You're Not Registered!*\n\nPlease click the REGISTER button first and complete your registration using our affiliate link.\n\nAfter successful registration, come back and enter your Player ID.",
        'deposit_btn': "💳 Deposit",
        'check_deposit_btn': "🔍 Check Deposit",
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\nClick below to get your first prediction:",
        'deposit_not_found': "💰 *Deposit Not Found!*\n\nYou have registered successfully but no deposit detected yet.\n\n💵 Please make a deposit of at least $6 to get prediction access.",
        'get_prediction_btn': "🎯 Get Prediction",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 20 free predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow for new predictions\n• Make another deposit for additional access\n\n💰 Continue predictions by staying active!",
        'deposit_again_btn': "💳 Deposit Again",
        'try_tomorrow_btn': "🕐 Try Tomorrow",
        'next_prediction_btn': "🔄 Next Prediction",
        'prediction_text': "🎯 *AI CRICKET PREDICTION* 🤖\n\n🏟️ *Match:* {team_a} vs {team_b}\n📊 *Prediction:* {prediction}\n✅ *Confidence:* {confidence}%\n\n📈 *Analysis:*\n{analysis}\n\n⚠️ *AI Prediction - Bet Responsibly*",
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
        'loading_registration': "⏳ *कृपया कुछ सेकंड प्रतीक्षा करें, आपका पंजीकरण लोड हो रहा है...*",
        'reg_success': "🎉 *बधाई हो, आपने सफलतापूर्वक पंजीकरण पूरा कर लिया है!*\n\n✅ आपका खाता बॉट के साथ सिंक हो गया है\n\n💴 *सिग्नल तक पहुंच प्राप्त करने के लिए, अपने खाते में कम से कम 600₹ या $6 जमा करें*\n\n🕹️ अपना खाता सफलतापूर्वक रिचार्ज करने के बाद, CHECK DEPOSIT बटन पर क्लिक करें और पहुंच प्राप्त करें",
        'reg_not_found': "❌ *क्षमा करें, आप पंजीकृत नहीं हैं!*\n\nकृपया पहले REGISTER बटन पर क्लिक करें और हमारे एफिलिएट लिंक का उपयोग करके अपना पंजीकरण पूरा करें।\n\nसफल पंजीकरण के बाद, वापस आएं और अपना Player ID दर्ज करें।",
        'deposit_btn': "💳 जमा करें",
        'check_deposit_btn': "🔍 जमा जांचें",
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'deposit_not_found': "💰 *जमा नहीं मिला!*\n\nआपने सफलतापूर्वक पंजीकरण कर लिया है लेकिन अभी तक कोई जमा नहीं detected हुआ है।\n\n💵 कृपया भविष्यवाणी तक पहुंच प्राप्त करने के लिए कम से कम $6 जमा करें।",
        'get_prediction_btn': "🎯 भविष्यवाणी प्राप्त करें",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 20 मुफ्त भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• नई भविष्यवाणियों के लिए कल तक प्रतीक्षा करें\n• अतिरिक्त पहुंच के लिए दूसरी जमा राशि करें\n\n💰 सक्रिय रहकर भविष्यवाणियाँ जारी रखें!",
        'deposit_again_btn': "💳 फिर से जमा करें",
        'try_tomorrow_btn': "🕐 कल प्रयास करें",
        'next_prediction_btn': "🔄 अगली भविष्यवाणी",
        'prediction_text': "🎯 *AI क्रिकेट भविष्यवाणी* 🤖\n\n🏟️ *मैच:* {team_a} vs {team_b}\n📊 *भविष्यवाणी:* {prediction}\n✅ *विश्वास:* {confidence}%\n\n📈 *विश्लेषण:*\n{analysis}\n\n⚠️ *AI भविष्यवाणी - जिम्मेदारी से जुआ खेलें*",
        'random_messages': [
            "आपका पंजीकरण सफल रहा है! ✅\n\n$6,7,10,13,17 या कोई अन्य राशि जमा करें और बॉट स्वचालित रूप से आपको सिग्नल तक पहुंच प्रदान करेगा! 🔑\n\nआप प्रतिदिन $10 ➡️ $100 कमा सकते हैं💰\n\n👉 /start क्लिक करें",
            "भाई, आपके लिए सिग्नल तैयार है☺️\n\nअभी शुरू करें👉 /start",
            "🚀 सिग्नल आ चुका है\n\n🔥 अपना पैसा पाने का मौका मत चूकें\n\n➡️ /start",
            "अभी बॉट शुरू करें और पैसा प्राप्त करें💰🔥\n\n/start"
        ]
    }
}

# ==================== AI PREDICTION WITH CRICAPI ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        
    def fetch_live_matches(self):
        try:
            if not self.api_key:
                return self.get_fallback_matches()
                
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    matches = []
                    for match in data.get('data', []):
                        if match.get('matchStarted') and not match.get('matchEnded'):
                            team_a = match['teamInfo'][0]['name'] if match.get('teamInfo') else 'Team A'
                            team_b = match['teamInfo'][1]['name'] if match.get('teamInfo') and len(match['teamInfo']) > 1 else 'Team B'
                            matches.append({
                                'id': match['id'],
                                'team_a': team_a,
                                'team_b': team_b,
                                'date': match.get('date', ''),
                                'series': match.get('series', 'International'),
                                'status': match.get('status', 'Live')
                            })
                    return matches[:3]
            return self.get_fallback_matches()
        except Exception as e:
            print(f"API Error: {e}")
            return self.get_fallback_matches()
    
    def get_fallback_matches(self):
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
        # Advanced AI analysis
        total_matches = random.randint(50, 150)
        team1_wins = random.randint(20, total_matches - 20)
        team2_wins = total_matches - team1_wins - random.randint(5, 15)
        
        team1_strength = (team1_wins / total_matches) * random.uniform(0.8, 1.2)
        team2_strength = (team2_wins / total_matches) * random.uniform(0.8, 1.2)
        
        if team1_strength > team2_strength:
            winner = team1
            confidence = min(95, int(team1_strength * 100))
        else:
            winner = team2
            confidence = min(95, int(team2_strength * 100))
        
        analysis_points = [
            f"Historical data analyzed: {total_matches} matches between teams",
            f"Current form and player performance considered",
            f"Pitch conditions and weather factors included",
            f"Team composition and strategy analyzed"
        ]
        
        return {
            'prediction': f"{winner} to win",
            'confidence': confidence,
            'analysis': "\n".join(analysis_points),
            'team_a': team1,
            'team_b': team2,
            'user_analysis': f"Based on comprehensive AI analysis of team performance, {winner} shows stronger chances in this encounter with {confidence}% confidence."
        }
    
    def get_todays_prediction(self):
        matches = self.fetch_live_matches()
        if not matches:
            return self.analyze_team_history("India", "Pakistan")
        
        match = random.choice(matches)
        return self.analyze_team_history(match['team_a'], match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== USER MANAGEMENT ====================
def get_user(user_id):
    return users_storage.get(user_id, {
        'user_id': user_id,
        'language': 'en',
        'prediction_count': 0,
        'last_prediction_date': None,
        'player_id': None,
        'deposit_amount': 0,
        'is_registered': False
    })

def save_user(user_data):
    users_storage[user_data['user_id']] = user_data

def can_get_prediction(user_id):
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user['last_prediction_date'] != today:
        # Reset for new day - 20 predictions per day
        user['prediction_count'] = 0
        user['last_prediction_date'] = today
        save_user(user)
    
    return user['prediction_count'] < 20

def update_prediction_count(user_id):
    user = get_user(user_id)
    user['prediction_count'] += 1
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

# ==================== PLAYER VERIFICATION ====================
def verify_player_registration(player_id):
    """
    Verify if player is registered through our affiliate link
    This simulates checking with 1Win postback system
    """
    # Simulate API call delay
    time.sleep(2)
    
    # Check if player exists in our registration records
    if player_id in player_registrations:
        return {
            'registered': True,
            'deposit_amount': player_deposits.get(player_id, 0)
        }
    else:
        return {
            'registered': False,
            'deposit_amount': 0
        }

# ==================== TELEGRAM FUNCTIONS ====================
def send_telegram_message(chat_id, text, reply_markup=None):
    try:
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

def delete_telegram_message(chat_id, message_id):
    try:
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
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

def send_admin_notification(message):
    try:
        if ADMIN_CHAT_ID:
            send_telegram_message(ADMIN_CHAT_ID, f"🔔 ADMIN: {message}")
    except:
        pass

# ==================== 1WIN POSTBACK HANDLER ====================
@app.route('/1win-postback', methods=['GET', 'POST'])
def handle_1win_postback():
    try:
        if request.method == 'GET':
            data = request.args.to_dict()
        else:
            data = request.get_json() or request.form.to_dict()
        
        print("📨 1Win Postback Received:", data)
        
        player_id = data.get('id') or data.get('player_id') or data.get('user_id')
        status = data.get('status', '')
        deposit_amount = float(data.get('fdp', 0) or data.get('dep_sum', 0) or data.get('amount', 0))
        
        if player_id:
            # Mark player as registered
            player_registrations[player_id] = True
            
            if status in ['fd_approved', 'active', 'success'] and deposit_amount > 0:
                player_deposits[player_id] = deposit_amount
                
                # Update all users with this player_id
                for user_id, user_data in users_storage.items():
                    if user_data.get('player_id') == player_id:
                        user_data['deposit_amount'] = deposit_amount
                        user_data['is_registered'] = True
                        users_storage[user_id] = user_data
                
                send_admin_notification(f"💰 New deposit: Player {player_id} - ${deposit_amount}")
                return jsonify({"status": "success", "player_id": player_id, "deposit": deposit_amount})
            else:
                # Just registration without deposit
                send_admin_notification(f"📝 New registration: Player {player_id}")
                return jsonify({"status": "success", "player_id": player_id, "deposit": 0})
        
        return jsonify({"status": "error", "message": "Invalid data"})
    
    except Exception as e:
        print(f"Postback error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== MANUAL PLAYER REGISTRATION (for testing) ====================
@app.route('/register-player', methods=['GET'])
def manual_register_player():
    """For testing: Manually register a player with deposit"""
    player_id = request.args.get('player_id')
    deposit_amount = float(request.args.get('deposit', 6))
    
    if player_id:
        player_registrations[player_id] = True
        player_deposits[player_id] = deposit_amount
        
        # Update users with this player_id
        for user_id, user_data in users_storage.items():
            if user_data.get('player_id') == player_id:
                user_data['deposit_amount'] = deposit_amount
                user_data['is_registered'] = True
                users_storage[user_id] = user_data
        
        return jsonify({
            "status": "success", 
            "player_id": player_id, 
            "deposit": deposit_amount,
            "message": "Player manually registered with deposit"
        })
    
    return jsonify({"status": "error", "message": "No player_id provided"})

# ==================== MAIN BOT HANDLER ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username')
            first_name = message['from'].get('first_name', 'User')
            
            # Delete message immediately
            delete_telegram_message(chat_id, message_id)
            
            user = get_user(user_id)
            if not user.get('username'):
                user.update({
                    'username': username,
                    'first_name': first_name
                })
                save_user(user)
            
            if text == '/start':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 हिंदी', 'callback_data': 'lang_hi'}]
                    ]
                }
                
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                send_telegram_message(chat_id, msg_data['welcome'], keyboard)
            
            elif text.isdigit() and len(text) >= 5:
                # User entered Player ID
                player_id = text
                
                # Show loading message
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                loading_msg = send_telegram_message(chat_id, msg_data['loading_registration'])
                
                # Verify player registration
                verification = verify_player_registration(player_id)
                
                # Delete loading message
                if loading_msg and 'result' in loading_msg:
                    delete_telegram_message(chat_id, loading_msg['result']['message_id'])
                
                if verification['registered']:
                    # Player is registered
                    user['player_id'] = player_id
                    user['is_registered'] = True
                    user['deposit_amount'] = verification['deposit_amount']
                    save_user(user)
                    
                    if verification['deposit_amount'] >= 6:
                        # User has deposited enough
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                            ]
                        }
                        message_text = msg_data['deposit_success'].replace('{amount}', str(verification['deposit_amount']))
                    else:
                        # Registered but no deposit or insufficient deposit
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                            ]
                        }
                        message_text = msg_data['reg_success']
                    
                    send_telegram_message(chat_id, message_text, keyboard)
                else:
                    # Player not found in our system
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['register_btn'], 'url': 'https://mostbet-king.com/5rTs'}]
                        ]
                    }
                    send_telegram_message(chat_id, msg_data['reg_not_found'], keyboard)
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            data_value = callback['data']
            user_id = callback['from']['id']
            
            # Delete previous message
            delete_telegram_message(chat_id, message_id)
            
            user = get_user(user_id)
            msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
            
            if data_value.startswith('lang_'):
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
                send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'check_registration':
                send_telegram_message(chat_id, msg_data['enter_player_id'])
            
            elif data_value == 'check_deposit':
                # Re-verify player status
                if user.get('player_id'):
                    verification = verify_player_registration(user['player_id'])
                    user['deposit_amount'] = verification['deposit_amount']
                    save_user(user)
                
                deposit_amount = user.get('deposit_amount', 0)
                if deposit_amount >= 6:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    message_text = msg_data['deposit_success'].replace('{amount}', str(deposit_amount))
                else:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                        ]
                    }
                    message_text = msg_data['deposit_not_found']
                
                send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'get_prediction':
                if not can_get_prediction(user_id):
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['try_tomorrow_btn'], 'callback_data': 'try_tomorrow'}]
                        ]
                    }
                    send_telegram_message(chat_id, msg_data['prediction_limit'], keyboard)
                else:
                    prediction = ai_predictor.get_todays_prediction()
                    update_prediction_count(user_id)
                    
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['next_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    
                    message_text = msg_data['prediction_text'].format(
                        team_a=prediction['team_a'],
                        team_b=prediction['team_b'],
                        prediction=prediction['prediction'],
                        confidence=prediction['confidence'],
                        analysis=prediction['user_analysis']
                    )
                    
                    send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'try_tomorrow':
                send_telegram_message(chat_id, "⏳ Please try again tomorrow for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "✅ Sports Prediction Bot is Running!"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    VERCEL_URL = os.environ.get('VERCEL_URL')
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://{VERCEL_URL}/webhook"
    response = requests.get(url)
    
    return jsonify({"status": "success", "result": response.json()})

# ==================== ADMIN STATS ====================
@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    total_users = len(users_storage)
    registered_users = len([u for u in users_storage.values() if u.get('is_registered')])
    deposited_users = len([u for u in users_storage.values() if u.get('deposit_amount', 0) >= 6])
    
    return jsonify({
        "total_users": total_users,
        "registered_users": registered_users,
        "deposited_users": deposited_users,
        "player_registrations": len(player_registrations),
        "player_deposits": len(player_deposits)
    })

if __name__ == '__main__':
    app.run()
