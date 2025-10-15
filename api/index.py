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
                # Language selection with NATIVE language names
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                        [{'text': '🇮🇳 हिंदी', 'callback_data': 'lang_hi'}],
                        [{'text': '🇧🇩 বাংলা', 'callback_data': 'lang_bn'}],
                        [{'text': '🇵🇰 اردو', 'callback_data': 'lang_ur'}],
                        [{'text': '🇳🇵 नेपाली', 'callback_data': 'lang_ne'}]
                    ]
                }
                
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': '🌍 *Select Your Preferred Language:*\n\nकृपया अपनी भाषा चुनें:\nদয়া করে আপনার ভাষা নির্বাচন করুন:\nبراہ کرم اپنی زبان منتخب کریں:\nकृपया आफ्नो भाषा चयन गर्नुहोस्:',
                    'reply_markup': keyboard,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, json=payload)
                print("📤 Sent language:", response.json())
        
        elif 'callback_query' in data:
            # Handle language selection
            callback_data = data['callback_query']
            chat_id = callback_data['message']['chat']['id']
            data_value = callback_data['data']
            
            BOT_TOKEN = os.environ.get('BOT_TOKEN')
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
            if data_value.startswith('lang_'):
                lang_code = data_value.split('_')[1]
                
                # Language messages in NATIVE languages (WITHOUT prediction limit)
                messages = {
                    'en': {
                        'selected': '✅ You selected English!',
                        'title': '🌐 *Step 1 - Register*',
                        'account_new': '‼️ *THE ACCOUNT MUST BE NEW*',
                        'instruction1': '1️⃣ If after clicking the "REGISTER" button you get to the old account, you need to log out of it and click the button again.',
                        'instruction2': '2️⃣ Specify a promocode during registration: **FREE**',
                        'after_reg': '✅ After REGISTRATION, click the "CHECK REGISTRATION" button'
                    },
                    'hi': {
                        'selected': '✅ आपने हिंदी चुनी!',
                        'title': '🌐 *चरण 1 - पंजीकरण*',
                        'account_new': '‼️ *खाता नया होना चाहिए*',
                        'instruction1': '1️⃣ यदि "REGISTER" बटन पर क्लिक करने के बाद आप पुराने खाते में आते हैं, तो आपको उससे लॉग आउट करना होगा और फिर से बटन पर क्लिक करना होगा।',
                        'instruction2': '2️⃣ पंजीकरण के दौरान प्रोमोकोड निर्दिष्ट करें: **FREE**',
                        'after_reg': '✅ पंजीकरण के बाद, "CHECK REGISTRATION" बटन पर क्लिक करें'
                    },
                    'bn': {
                        'selected': '✅ আপনি বাংলা নির্বাচন করেছেন!',
                        'title': '🌐 *ধাপ 1 - নিবন্ধন*',
                        'account_new': '‼️ *অ্যাকাউন্টটি নতুন হতে হবে*',
                        'instruction1': '1️⃣ যদি "REGISTER" বাটনে ক্লিক করার পরে আপনি পুরানো অ্যাকাউন্টে আসেন, তাহলে আপনাকে এটি থেকে লগ আউট করতে হবে এবং আবার বাটনে ক্লিক করতে হবে।',
                        'instruction2': '2️⃣ নিবন্ধনের সময় একটি প্রোমোকোড নির্দিষ্ট করুন: **FREE**',
                        'after_reg': '✅ নিবন্ধনের পরে, "CHECK REGISTRATION" বাটনে ক্লিক করুন'
                    },
                    'ur': {
                        'selected': '✅ آپ نے اردو منتخب کی!',
                        'title': '🌐 *مرحلہ 1 - رجسٹریشن*',
                        'account_new': '‼️ *اکاؤنٹ نیا ہونا چاہیے*',
                        'instruction1': '1️⃣ اگر "REGISTER" بٹن پر کلک کرنے کے بعد آپ پرانے اکاؤنٹ میں آتے ہیں، تو آپ کو اس سے لاگ آؤٹ ہونا پڑے گا اور دوبارہ بٹن پر کلک کرنا ہوگا۔',
                        'instruction2': '2️⃣ رجسٹریشن کے دوران ایک پروموکوڈ指定 کریں: **FREE**',
                        'after_reg': '✅ رجس्टریشن کے بعد، "CHECK REGISTRATION" بٹن پر کلک کریں'
                    },
                    'ne': {
                        'selected': '✅ तपाईंले नेपाली चयन गर्नुभयो!',
                        'title': '🌐 *चरण 1 - दर्ता*',
                        'account_new': '‼️ *खाता नयाँ हुनुपर्छ*',
                        'instruction1': '1️⃣ यदि "REGISTER" बटनमा क्लिक गरेपछि तपाईं पुरानो खातामा आउनुहुन्छ भने, तपाईंले यसबाट लग आउट गर्नुपर्छ र फेरि बटनमा क्लिक गर्नुपर्छ।',
                        'instruction2': '2️⃣ दर्ता during प्रोमोकोड निर्दिष्ट गर्नुहोस्: **FREE**',
                        'after_reg': '✅ दर्ता पछि, "CHECK REGISTRATION" बटनमा क्लिक गर्नुहोस्'
                    }
                }
                
                msg = messages.get(lang_code, messages['en'])
                
                # Registration instructions in selected language (WITHOUT prediction limit)
                message_text = f"""
{msg['selected']}

{msg['title']}

{msg['account_new']}

{msg['instruction1']}

{msg['instruction2']}

{msg['after_reg']}
                """
                
                # Buttons VERTICAL (upar-niche)
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '📲 REGISTER', 'url': 'https://1w.com/registration?affiliate=FREE'}],
                        [{'text': '✅ CHECK REGISTRATION', 'callback_data': 'check_registration'}]
                    ]
                }
                
                payload = {
                    'chat_id': chat_id,
                    'text': message_text,
                    'reply_markup': keyboard,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, json=payload)
                print("📤 Sent registration:", response.json())
            
            elif data_value == 'check_registration':
                # Check registration logic (system me limit hai but user ko nahi dikhega)
                payload = {
                    'chat_id': chat_id,
                    'text': '🔍 *Checking your registration...*\n\nPlease wait while we verify your account and deposit.',
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, json=payload)
                print("📤 Sent check registration:", response.json())
        
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
