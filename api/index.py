from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = os.environ.get('CRICAPI_KEY')
VERCEL_URL = os.environ.get('VERCEL_URL')

# In-memory storage
users_storage = {}
player_deposits = {}

# ==================== ALL LANGUAGES MESSAGES ====================
LANGUAGE_MESSAGES = {
    'en': {
        'welcome': "🌍 *Select Your Preferred Language:*",
        'selected': "✅ You selected English!",
        'register_title': "🌐 *Step 1 - Register*",
        'account_new': "‼️ *THE ACCOUNT MUST BE NEW*",
        'instruction1': "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, you need to log out of it and click the button again.",
        'instruction2': "2️⃣ Specify a promocode during registration: **CLAIM**",
        'after_reg': "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button",
        'enter_player_id': "🔍 *Check Your Registration*\n\nPlease enter your 1Win *Player ID* to verify your registration.\n\n📝 *How to find Player ID:*\n1. Login to 1Win account\n2. Go to Profile Settings\n3. Copy Player ID number\n4. Paste it here\n\n🔢 *Enter your Player ID now:*",
        'not_registered': "❌ *Sorry, You're Not Registered!*\n\nPlease click the REGISTER button first and complete your registration using our affiliate link.\n\nAfter successful registration, come back and enter your Player ID.",
        'reg_success_no_deposit': "🎉 *Great, you have successfully completed registration!*\n\n✅ Your account is synchronized with the bot\n\n💴 *To gain access to signals, deposit your account (make a deposit) with at least 600₹ or $6 in any currency*\n\n🕹️ After successfully replenishing your account, click on the CHECK DEPOSIT button and gain access",
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\nClick below to get your first prediction:",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 5 free predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow (12 hours)\n• Deposit 400₹ or $4 for immediate access\n\n💰 Continue predictions by depositing at least 400₹ or $4"
    },
    'hi': {
        'welcome': "🌍 *अपनी पसंदीदा भाषा चुनें:*",
        'selected': "✅ आपने हिंदी चुनी!",
        'register_title': "🌐 *चरण 1 - पंजीकरण*",
        'account_new': "‼️ *खाता नया होना चाहिए*",
        'instruction1': "1️⃣ यदि \"REGISTER\" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।",
        'instruction2': "2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **CLAIM**",
        'after_reg': "✅ पंजीकरण के बाद, \"CHECK REGISTRATION\" बटन पर क्लिक करें",
        'enter_player_id': "🔍 *अपना पंजीकरण जांचें*\n\nकृपया सत्यापित करने के लिए अपना 1Win *Player ID* दर्ज करें:\n\n📝 *Player ID कैसे ढूंढें:*\n1. 1Win अकाउंट में लॉगिन करें\n2. प्रोफाइल सेटिंग्स पर जाएं\n3. Player ID नंबर कॉपी करें\n4. यहाँ पेस्ट करें\n\n🔢 *अब अपना Player ID दर्ज करें:*",
        'not_registered': "❌ *क्षमा करें, आप पंजीकृत नहीं हैं!*\n\nकृपया पहले REGISTER बटन पर क्लिक करें और हमारे एफिलिएट लिंक का उपयोग करके अपना पंजीकरण पूरा करें।\n\nसफल पंजीकरण के बाद, वापस आएं और अपना Player ID दर्ज करें।",
        'reg_success_no_deposit': "🎉 *बधाई हो, आपने सफलतापूर्वक पंजीकरण पूरा कर लिया है!*\n\n✅ आपका खाता बॉट के साथ सिंक हो गया है\n\n💴 *सिग्नल तक पहुंच प्राप्त करने के लिए, अपने खाते में कम से कम 600₹ या $6 जमा करें*\n\n🕹️ अपना खाता सफलतापूर्वक रिचार्ज करने के बाद, CHECK DEPOSIT बटन पर क्लिक करें और पहुंच प्राप्त करें",
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 5 मुफ्त भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• कल तक प्रतीक्षा करें (12 घंटे)\n• तुरंत पहुंच के लिए 400₹ या $4 जमा करें\n\n💰 कम से कम 400₹ या $4 जमा करके भविष्यवाणियाँ जारी रखें"
    },
    'bn': {
        'welcome': "🌍 *আপনার ভাষা নির্বাচন করুন:*",
        'selected': "✅ আপনি বাংলা নির্বাচন করেছেন!",
        'register_title': "🌐 *ধাপ 1 - নিবন্ধন*",
        'account_new': "‼️ *অ্যাকাউন্টটি নতুন হতে হবে*",
        'instruction1': "1️⃣ যদি \"REGISTER\" বাটনে ক্লিক করার পরে আপনি পুরানো অ্যাকাউন্টে আসেন, তাহলে আপনাকে এটি থেকে লগ আউট করতে হবে এবং আবার বাটনে ক্লিক করতে হবে।",
        'instruction2': "2️⃣ নিবন্ধনের সময় একটি প্রোমোকোড নির্দিষ্ট করুন: **CLAIM**",
        'after_reg': "✅ নিবন্ধনের পরে, \"CHECK REGISTRATION\" বাটনে ক্লিক করুন",
        'enter_player_id': "🔍 *আপনার নিবন্ধন পরীক্ষা করুন*\n\nযাচাই করার জন্য আপনার 1Win *Player ID* লিখুন:\n\n📝 *Player ID কিভাবে খুঁজে পাবেন:*\n1. 1Win অ্যাকাউন্টে লগইন করুন\n2. প্রোফাইল সেটিংসে যান\n3. Player ID নম্বর কপি করুন\n4. এখানে পেস্ট করুন\n\n🔢 *এখন আপনার Player ID লিখুন:*",
        'not_registered': "❌ *দুঃখিত, আপনি নিবন্ধিত নন!*\n\nদয়া করে প্রথমে REGISTER বাটনে ক্লিক করুন এবং আমাদের অ্যাফিলিয়েট লিঙ্ক ব্যবহার করে আপনার নিবন্ধন সম্পূর্ণ করুন।\n\nসফল নিবন্ধনের পরে, ফিরে আসুন এবং আপনার Player ID লিখুন।",
        'reg_success_no_deposit': "🎉 *অভিনন্দন, আপনি সফলভাবে নিবন্ধন সম্পন্ন করেছেন!*\n\n✅ আপনার অ্যাকাউন্ট বটের সাথে সিঙ্ক হয়েছে\n\n💴 *সিগন্যাল অ্যাক্সেস পেতে, আপনার অ্যাকাউন্টে কমপক্ষে 600₹ বা $6 জমা করুন*\n\n🕹️ আপনার অ্যাকাউন্ট সফলভাবে রিচার্জ করার পর, CHECK DEPOSIT বাটনে ক্লিক করুন এবং অ্যাক্সেস পান",
        'deposit_success': "🎊 *জমা সফলভাবে যাচাই করা হয়েছে!*\n\n💰 *জমার পরিমাণ:* ${amount}\n✅ *স্ট্যাটাস:* যাচাইকৃত\n\n🎯 এখন আপনার AI-চালিত ভবিষ্যদ্বাণী অ্যাক্সেস আছে!\n\nআপনার প্রথম ভবিষ্যদ্বাণী পেতে নীচে ক্লিক করুন:",
        'prediction_limit': "🚫 *ভবিষ্যদ্বাণী সীমা reached*\n\nআপনি আজকের 5টি বিনামূল্যের ভবিষ্যদ্বাণী ব্যবহার করেছেন।\n\n💡 *বিকল্প:*\n• আগামীকাল পর্যন্ত অপেক্ষা করুন (12 ঘন্টা)\n• অবিলম্বে অ্যাক্সেসের জন্য 400₹ বা $4 জমা করুন\n\n💰 কমপক্ষে 400₹ বা $4 জমা করে ভবিষ্যদ্বাণী চালিয়ে যান"
    },
    'ur': {
        'welcome': "🌍 *اپنی زبان منتخب کریں:*",
        'selected': "✅ آپ نے اردو منتخب کی!",
        'register_title': "🌐 *مرحلہ 1 - رجسٹریشن*",
        'account_new': "‼️ *اکاؤنٹ نیا ہونا چاہیے*",
        'instruction1': "1️⃣ اگر \"REGISTER\" بٹن پر کلک کرنے کے بعد آپ پرانے اکاؤنٹ میں آتے ہیں، تو آپ کو اس سے لاگ آؤٹ ہونا پڑے گا اور دوبارہ بٹن پر کلک کرنا ہوگا۔",
        'instruction2': "2️⃣ رجسٹریشن کے دوران ایک پروموکوڈ specified کریں: **CLAIM**",
        'after_reg': "✅ رجسٹریشن کے بعد، \"CHECK REGISTRATION\" بٹن پر کلک کریں",
        'enter_player_id': "🔍 *اپنی رجسٹریشن چیک کریں*\n\nتصدیق کے لیے اپنا 1Win *Player ID* درج کریں:\n\n📝 *Player ID کیسے ڈھونڈیں:*\n1. 1Win اکاؤنٹ میں لاگ ان کریں\n2. پروفائل سیٹنگز پر جائیں\n3. Player ID نمبر کاپی کریں\n4. یہاں پیسٹ کریں\n\n🔢 *اب اپنا Player ID درج کریں:*",
        'not_registered': "❌ *معذرت، آپ رجسٹرڈ نہیں ہیں!*\n\nبراہ کرم پہلے REGISTER بٹن پر کلک کریں اور ہمارے affiliate link کا استعمال کرتے ہوئے اپنی رجسٹریشن مکمل کریں۔\n\nکامیاب رجسٹریشن کے بعد، واپس آئیں اور اپنا Player ID درج کریں۔",
        'reg_success_no_deposit': "🎉 *مبارک ہو، آپ نے کامیابی کے ساتھ رجسٹریشن مکمل کر لی ہے!*\n\n✅ آپ کا اکاؤنٹ بوٹ کے ساتھ sync ہو گیا ہے\n\n💴 *سگنلز تک رسائی حاصل کرنے کے لیے، اپنے اکاؤنٹ میں کم از کم 600₹ یا $6 جمع کروائیں*\n\n🕹️ اپنا اکاؤنٹ کامیابی سے ریچارج کرنے کے بعد، CHECK DEPOSIT بٹن پر کلک کریں اور رسائی حاصل کریں",
        'deposit_success': "🎊 *جمع کامیابی سے تصدیق ہو گئی!*\n\n💰 *جمع کی رقم:* ${amount}\n✅ *حالت:* تصدیق شدہ\n\n🎯 اب آپ کے پاس AI-powered predictions تک رسائی ہے!\n\nاپنی پہلی prediction حاصل کرنے کے لیے نیچے کلک کریں:",
        'prediction_limit': "🚫 *prediction حد reached*\n\nآپ نے آج کی 5 مفت predictions استعمال کر لی ہیں۔\n\n💡 *اختیارات:*\n• کل تک انتظار کریں (12 گھنٹے)\n• فوری رسائی کے لیے 400₹ یا $4 جمع کروائیں\n\n💰 کم از کم 400₹ یا $4 جمع کروا کر predictions جاری رکھیں"
    },
    'ne': {
        'welcome': "🌍 *आफ्नो भाषा चयन गर्नुहोस्:*",
        'selected': "✅ तपाईंले नेपाली चयन गर्नुभयो!",
        'register_title': "🌐 *चरण 1 - दर्ता*",
        'account_new': "‼️ *खाता नयाँ हुनुपर्छ*",
        'instruction1': "1️⃣ यदि \"REGISTER\" बटनमा क्लिक गरेपछि तपाईं पुरानो खातामा आउनुहुन्छ भने, तपाईंले यसबाट लग आउट गर्नुपर्छ र फेरि बटनमा क्लिक गर्नुपर्छ।",
        'instruction2': "2️⃣ दर्ता during प्रोमोकोड निर्दिष्ट गर्नुहोस्: **CLAIM**",
        'after_reg': "✅ दर्ता पछि, \"CHECK REGISTRATION\" बटनमा क्लिक गर्नुहोस्",
        'enter_player_id': "🔍 *आफ्नो दर्ता जाँच गर्नुहोस्*\n\nसत्यापित गर्न आफ्नो 1Win *Player ID* प्रविष्ट गर्नुहोस्:\n\n📝 *Player ID कसरी फेला पार्ने:*\n1. 1Win खातामा लग इन गर्नुहोस्\n2. प्रोफाइल सेटिङहरूमा जानुहोस्\n3. Player ID नम्बर कपी गर्नुहोस्\n4. यहाँ पेस्ट गर्नुहोस्\n\n🔢 *अब आफ्नो Player ID प्रविष्ट गर्नुहोस्:*",
        'not_registered': "❌ *माफ गर्नुहोस्, तपाईं दर्ता गरिएको छैन!*\n\nकृपया पहिले REGISTER बटनमा क्लिक गर्नुहोस् र हाम्रो एफिलिएट लिङ्क प्रयोग गरेर आफ्नो दर्ता पूरा गर्नुहोस्।\n\nसफल दर्ता पछि, फर्कनुहोस् र आफ्नो Player ID प्रविष्ट गर्नुहोस्।",
        'reg_success_no_deposit': "🎉 *बधाई छ, तपाईंले सफलतापूर्वक दर्ता पूरा गर्नुभयो!*\n\n✅ तपाईंको खाता बोटसँग सिङ्क भयो\n\n💴 *सिग्नलहरूको पहुँच प्राप्त गर्न, आफ्नो खातामा कम्तिमा 600₹ वा $6 जम्मा गर्नुहोस्*\n\n🕹️ आफ्नो खाता सफलतापूर्वक रिचार्ज गरेपछि, CHECK DEPOSIT बटनमा क्लिक गर्नुहोस् र पहुँच प्राप्त गर्नुहोस्",
        'deposit_success': "🎊 *जम्मा सफलतापूर्वक सत्यापित!*\n\n💰 *जम्मा रकम:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब तपाईंसँग AI-powered predictions को पहुँच छ!\n\nआफ्नो पहिलो prediction प्राप्त गर्न तल क्लिक गर्नुहोस्:",
        'prediction_limit': "🚫 *prediction सीमा reached*\n\nतपाईंले आजका 5 नि: शुल्क predictions प्रयोग गर्नुभयो।\n\n💡 *विकल्पहरू:*\n• भोलि सम्म पर्खनुहोस् (12 घण्टा)\n• तत्काल पहुँचको लागि 400₹ वा $4 जम्मा गर्नुहोस्\n\n💰 कम्तिमा 400₹ वा $4 जम्मा गरेर predictions जारी राख्नुहोस्"
    }
}

# ==================== AI PREDICTION ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        
    def get_todays_prediction(self):
        teams = [
            ('India', 'Pakistan'),
            ('Australia', 'England'),
            ('New Zealand', 'South Africa'),
            ('West Indies', 'Sri Lanka'),
            ('Bangladesh', 'Afghanistan')
        ]
        team_a, team_b = random.choice(teams)
        
        predictions = [f"{team_a} to win", f"{team_b} to win"]
        analysis = [
            f"Based on comprehensive AI analysis of team performance, {team_a} shows stronger chances in this encounter.",
            f"Historical data and current form analysis favors {team_b} in this match.",
            f"Team composition and player form analysis suggests {team_a} has better winning chances.",
            f"Pitch conditions and weather factors give advantage to {team_b}."
        ]
        
        return {
            'team_a': team_a,
            'team_b': team_b,
            'prediction': random.choice(predictions),
            'confidence': random.randint(85, 95),
            'analysis': random.choice(analysis)
        }

ai_predictor = CricketAIPredictor()

# ==================== USER MANAGEMENT ====================
def get_user(user_id):
    return users_storage.get(user_id, {
        'user_id': user_id,
        'language': 'en',
        'prediction_count': 0,
        'last_prediction_date': None,
        'player_id': None,
        'deposit_amount': 0
    })

def save_user(user_data):
    users_storage[user_data['user_id']] = user_data

def can_get_prediction(user_id):
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user['last_prediction_date'] != today:
        user['prediction_count'] = 0
        user['last_prediction_date'] = today
        save_user(user)
    
    return user['prediction_count'] < 5

def update_prediction_count(user_id):
    user = get_user(user_id)
    user['prediction_count'] += 1
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

# ==================== PLAYER VERIFICATION ====================
def verify_player(player_id):
    """Check if player is registered via postback"""
    return player_id in player_deposits

def get_player_deposit(player_id):
    """Get player deposit amount"""
    return player_deposits.get(player_id, 0)

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

# ==================== 1WIN POSTBACK ====================
@app.route('/1win-postback', methods=['GET'])
def handle_1win_postback():
    try:
        data = request.args.to_dict()
        print("📨 1Win Postback:", data)
        
        player_id = data.get('id')
        status = data.get('status', '')
        deposit_amount = float(data.get('fdp', 0) or data.get('dep_sum', 0))
        
        if player_id and status in ['fd_approved', 'active']:
            player_deposits[player_id] = deposit_amount
            
            # Update all users with this player_id
            for user_id, user_data in users_storage.items():
                if user_data.get('player_id') == player_id:
                    user_data['deposit_amount'] = deposit_amount
                    users_storage[user_id] = user_data
            
            return jsonify({"status": "success", "player_id": player_id})
        
        return jsonify({"status": "error", "message": "Invalid data"})
    
    except Exception as e:
        print(f"Postback error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== MAIN BOT HANDLER ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username')
            first_name = message['from'].get('first_name', 'User')
            
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
                        [{'text': '🇮🇳 हिंदी', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 বাংলা', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 اردو', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 नेपाली', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                send_telegram_message(chat_id, msg_data['welcome'], keyboard)
            
            elif text.isdigit() and len(text) >= 5:
                player_id = text
                user['player_id'] = player_id
                save_user(user)
                
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                
                # Verify player through postback
                if verify_player(player_id):
                    deposit_amount = get_player_deposit(player_id)
                    user['deposit_amount'] = deposit_amount
                    save_user(user)
                    
                    if deposit_amount >= 6:
                        # Has deposited - show prediction button
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': '🎯 GET PREDICTION', 'callback_data': 'get_prediction'}]
                            ]
                        }
                        message_text = msg_data['deposit_success'].replace('{amount}', str(deposit_amount))
                    else:
                        # Registered but no deposit
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': '💳 DEPOSIT', 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': '🔍 CHECK DEPOSIT', 'callback_data': 'check_deposit'}]
                            ]
                        }
                        message_text = msg_data['reg_success_no_deposit']
                else:
                    # Not registered at all
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': '📲 REGISTER', 'url': 'https://mostbet-king.com/5rTs'}]
                        ]
                    }
                    message_text = msg_data['not_registered']
                
                send_telegram_message(chat_id, message_text, keyboard)
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            data_value = callback['data']
            user_id = callback['from']['id']
            
            user = get_user(user_id)
            msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
            
            if data_value.startswith('lang_'):
                lang_code = data_value.split('_')[1]
                user['language'] = lang_code
                save_user(user)
                msg_data = LANGUAGE_MESSAGES[lang_code]
                
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '📲 REGISTER', 'url': 'https://mostbet-king.com/5rTs'}],
                        [{'text': '🔍 CHECK REGISTRATION', 'callback_data': 'check_registration'}]
                    ]
                }
                
                message_text = f"{msg_data['selected']}\n\n{msg_data['register_title']}\n\n{msg_data['account_new']}\n\n{msg_data['instruction1']}\n\n{msg_data['instruction2']}\n\n{msg_data['after_reg']}"
                send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'check_registration':
                send_telegram_message(chat_id, msg_data['enter_player_id'])
            
            elif data_value == 'check_deposit':
                player_id = user.get('player_id')
                if player_id and verify_player(player_id):
                    deposit_amount = get_player_deposit(player_id)
                    if deposit_amount >= 6:
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': '🎯 GET PREDICTION', 'callback_data': 'get_prediction'}]
                            ]
                        }
                        message_text = msg_data['deposit_success'].replace('{amount}', str(deposit_amount))
                    else:
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': '💳 DEPOSIT', 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': '🔍 CHECK DEPOSIT', 'callback_data': 'check_deposit'}]
                            ]
                        }
                        message_text = msg_data['reg_success_no_deposit']
                else:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': '📲 REGISTER', 'url': 'https://mostbet-king.com/5rTs'}]
                        ]
                    }
                    message_text = msg_data['not_registered']
                
                send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'get_prediction':
                if not can_get_prediction(user_id):
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': '💳 DEPOSIT AGAIN', 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': '🕐 TRY TOMORROW', 'callback_data': 'try_tomorrow'}]
                        ]
                    }
                    send_telegram_message(chat_id, msg_data['prediction_limit'], keyboard)
                else:
                    prediction = ai_predictor.get_todays_prediction()
                    update_prediction_count(user_id)
                    
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': '🔄 NEXT PREDICTION', 'callback_data': 'get_prediction'}]
                        ]
                    }
                    
                    message_text = f"🎯 *AI CRICKET PREDICTION* 🤖\n\n🏟️ *Match:* {prediction['team_a']} vs {prediction['team_b']}\n📊 *Prediction:* {prediction['prediction']}\n✅ *Confidence:* {prediction['confidence']}%\n\n📈 *Analysis:*\n{prediction['analysis']}\n\n⚠️ *AI Prediction - Bet Responsibly*"
                    
                    send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'try_tomorrow':
                send_telegram_message(chat_id, "⏳ Please try again after 12 hours for new predictions.")
        
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

if __name__ == '__main__':
    app.run()
