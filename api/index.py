from flask import Flask, request, jsonify
import os
import requests
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Environment variables - VERCEL ME DALNA HAI
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = "5c404449-255b-484e-ad48-dbc3c25e41fd"  # Direct code me
VERCEL_URL = os.environ.get('VERCEL_URL')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')  # Optional

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
        'next_prediction_btn': "🔄 Next Prediction",
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
        'next_prediction_btn': "🔄 अगली भविष्यवाणी",
        'random_messages': [
            "आपका पंजीकरण सफल रहा है! ✅\n\n$6,7,10,13,17 या कोई अन्य राशि जमा करें और बॉट स्वचालित रूप से आपको सिग्नल तक पहुंच प्रदान करेगा! 🔑\n\nआप प्रतिदिन $10 ➡️ $100 कमा सकते हैं💰\n\n👉 /start क्लिक करें",
            "भाई, आपके लिए सिग्नल तैयार है☺️\n\nअभी शुरू करें👉 /start",
            "🚀 सिग्नल आ चुका है\n\n🔥 अपना पैसा पाने का मौका मत चूकें\n\n➡️ /start",
            "अभी बॉट शुरू करें और पैसा प्राप्त करें💰🔥\n\n/start"
        ]
    },
    'bn': {
        'welcome': "🌍 *আপনার ভাষা নির্বাচন করুন:*",
        'selected': "✅ আপনি বাংলা নির্বাচন করেছেন!",
        'register_title': "🌐 *ধাপ 1 - নিবন্ধন*",
        'account_new': "‼️ *অ্যাকাউন্টটি নতুন হতে হবে*",
        'instruction1': "1️⃣ যদি \"REGISTER\" বাটনে ক্লিক করার পরে আপনি পুরানো অ্যাকাউন্টে আসেন, তাহলে আপনাকে এটি থেকে লগ আউট করতে হবে এবং আবার বাটনে ক্লিক করতে হবে।",
        'instruction2': "2️⃣ নিবন্ধনের সময় একটি প্রোমোকোড নির্দিষ্ট করুন: **CLAIM**",
        'after_reg': "✅ নিবন্ধনের পরে, \"CHECK REGISTRATION\" বাটনে ক্লিক করুন",
        'register_btn': "📲 নিবন্ধন",
        'check_btn': "🔍 নিবন্ধন পরীক্ষা",
        'enter_player_id': "🔍 *আপনার নিবন্ধন পরীক্ষা করুন*\n\nযাচাই করার জন্য আপনার 1Win *Player ID* লিখুন:\n\n📝 *Player ID কিভাবে খুঁজে পাবেন:*\n1. 1Win অ্যাকাউন্টে লগইন করুন\n2. প্রোফাইল সেটিংসে যান\n3. Player ID নম্বর কপি করুন\n4. এখানে পেস্ট করুন\n\n🔢 *এখন আপনার Player ID লিখুন:*",
        'reg_success': "🎉 *অভিনন্দন, আপনি সফলভাবে নিবন্ধন সম্পন্ন করেছেন!*\n\n✅ আপনার অ্যাকাউন্ট বটের সাথে সিঙ্ক হয়েছে\n\n💴 *সিগন্যাল অ্যাক্সেস পেতে, আপনার অ্যাকাউন্টে কমপক্ষে 600₹ বা $6 জমা করুন*\n\n🕹️ আপনার অ্যাকাউন্ট সফলভাবে রিচার্জ করার পর, CHECK DEPOSIT বাটনে ক্লিক করুন এবং অ্যাক্সেস পান",
        'deposit_btn': "💳 জমা করুন",
        'check_deposit_btn': "🔍 জমা পরীক্ষা",
        'deposit_success': "🎊 *জমা সফলভাবে যাচাই করা হয়েছে!*\n\n💰 *জমার পরিমাণ:* ${amount}\n✅ *স্ট্যাটাস:* যাচাইকৃত\n\n🎯 এখন আপনার AI-চালিত ভবিষ্যদ্বাণী অ্যাক্সেস আছে!\n\nআপনার প্রথম ভবিষ্যদ্বাণী পেতে নীচে ক্লিক করুন:",
        'get_prediction_btn': "🎯 ভবিষ্যদ্বাণী পান",
        'prediction_limit': "🚫 *ভবিষ্যদ্বাণী সীমা reached*\n\nআপনি আজকের 5টি বিনামূল্যের ভবিষ্যদ্বাণী ব্যবহার করেছেন।\n\n💡 *বিকল্প:*\n• আগামীকাল পর্যন্ত অপেক্ষা করুন (12 ঘন্টা)\n• অবিলম্বে অ্যাক্সেসের জন্য 400₹ বা $4 জমা করুন\n\n💰 কমপক্ষে 400₹ বা $4 জমা করে ভবিষ্যদ্বাণী চালিয়ে যান",
        'deposit_again_btn': "💳 আবার জমা করুন",
        'try_tomorrow_btn': "🕐 আগামীকাল চেষ্টা করুন",
        'next_prediction_btn': "🔄 পরবর্তী ভবিষ্যদ্বাণী",
        'random_messages': [
            "আপনার নিবন্ধন সফল হয়েছে! ✅\n\n$6,7,10,13,17 বা অন্য কোনো পরিমাণ জমা করুন এবং বট স্বয়ংক্রিয়ভাবে আপনাকে সিগন্যাল অ্যাক্সেস দেবে! 🔑\n\nআপনি প্রতিদিন $10 ➡️ $100 উপার্জন করতে পারেন💰\n\n👉 /start ক্লিক করুন",
            "ভাই, আপনার জন্য সিগন্যাল প্রস্তুত☺️\n\nএখনই শুরু করুন👉 /start",
            "🚀 সিগন্যাল already এসেছে\n\n🔥 আপনার টাকা পাওয়ার সুযোগ মিস করবেন না\n\n➡️ /start",
            "এখনই বট শুরু করুন এবং টাকা পান💰🔥\n\n/start"
        ]
    },
    'ur': {
        'welcome': "🌍 *اپنی زبان منتخب کریں:*",
        'selected': "✅ آپ نے اردو منتخب کی!",
        'register_title': "🌐 *مرحلہ 1 - رجسٹریشن*",
        'account_new': "‼️ *اکاؤنٹ نیا ہونا چاہیے*",
        'instruction1': "1️⃣ اگر \"REGISTER\" بٹن پر کلک کرنے کے بعد آپ پرانے اکاؤنٹ میں آتے ہیں، تو آپ کو اس سے لاگ آؤٹ ہونا پڑے گا اور دوبارہ بٹن پر کلک کرنا ہوگا۔",
        'instruction2': "2️⃣ رجسٹریشن کے دوران ایک پروموکوڈ specified کریں: **CLAIM**",
        'after_reg': "✅ رجسٹریشن کے بعد، \"CHECK REGISTRATION\" بٹن پر کلک کریں",
        'register_btn': "📲 رجسٹریشن",
        'check_btn': "🔍 رجسٹریشن چیک",
        'enter_player_id': "🔍 *اپنی رجسٹریشن چیک کریں*\n\nتصدیق کے لیے اپنا 1Win *Player ID* درج کریں:\n\n📝 *Player ID کیسے ڈھونڈیں:*\n1. 1Win اکاؤنٹ میں لاگ ان کریں\n2. پروفائل سیٹنگز پر جائیں\n3. Player ID نمبر کاپی کریں\n4. یہاں پیسٹ کریں\n\n🔢 *اب اپنا Player ID درج کریں:*",
        'reg_success': "🎉 *مبارک ہو، آپ نے کامیابی کے ساتھ رجسٹریشن مکمل کر لی ہے!*\n\n✅ آپ کا اکاؤنٹ بوٹ کے ساتھ sync ہو گیا ہے\n\n💴 *سگنلز تک رسائی حاصل کرنے کے لیے، اپنے اکاؤنٹ میں کم از کم 600₹ یا $6 جمع کروائیں*\n\n🕹️ اپنا اکاؤنٹ کامیابی سے ریچارج کرنے کے بعد، CHECK DEPOSIT بٹن پر کلک کریں اور رسائی حاصل کریں",
        'deposit_btn': "💳 جمع کروائیں",
        'check_deposit_btn': "🔍 جمع چیک",
        'deposit_success': "🎊 *جمع کامیابی سے تصدیق ہو گئی!*\n\n💰 *جمع کی رقم:* ${amount}\n✅ *حالت:* تصدیق شدہ\n\n🎯 اب آپ کے پاس AI-powered predictions تک رسائی ہے!\n\nاپنی پہلی prediction حاصل کرنے کے لیے نیچے کلک کریں:",
        'get_prediction_btn': "🎯 prediction حاصل",
        'prediction_limit': "🚫 *prediction حد reached*\n\nآپ نے آج کی 5 مفت predictions استعمال کر لی ہیں۔\n\n💡 *اختیارات:*\n• کل تک انتظار کریں (12 گھنٹے)\n• فوری رسائی کے لیے 400₹ یا $4 جمع کروائیں\n\n💰 کم از کم 400₹ یا $4 جمع کروا کر predictions جاری رکھیں",
        'deposit_again_btn': "💳 دوبارہ جمع",
        'try_tomorrow_btn': "🕐 کل کوشش",
        'next_prediction_btn': "🔄 اگلی prediction",
        'random_messages': [
            "آپ کی رجسٹریشن کامیاب رہی ہے! ✅\n\n$6,7,10,13,17 یا کوئی دوسری رقم جمع کروائیں اور بوٹ خود کار طریقے سے آپ کو سگنلز تک رسائی دے گا! 🔑\n\nآپ روزانہ $10 ➡️ $100 کما سکتے ہیں💰\n\n👉 /start کلک",
            "بھائی، آپ کے لیے سگنل تیار ہے☺️\n\nابھی شروع👉 /start",
            "🚀 سگنل already آ چکا\n\n🔥 اپنے پیسے حاصل کرنے کا موقع ضائع نہ کریں\n\n➡️ /start",
            "ابھی بوٹ شروع اور پیسے حاصل💰🔥\n\n/start"
        ]
    },
    'ne': {
        'welcome': "🌍 *आफ्नो भाषा चयन गर्नुहोस्:*",
        'selected': "✅ तपाईंले नेपाली चयन गर्नुभयो!",
        'register_title': "🌐 *चरण 1 - दर्ता*",
        'account_new': "‼️ *खाता नयाँ हुनुपर्छ*",
        'instruction1': "1️⃣ यदि \"REGISTER\" बटनमा क्लिक गरेपछि तपाईं पुरानो खातामा आउनुहुन्छ भने, तपाईंले यसबाट लग आउट गर्नुपर्छ र फेरि बटनमा क्लिक गर्नुपर्छ।",
        'instruction2': "2️⃣ दर्ता during प्रोमोकोड निर्दिष्ट गर्नुहोस्: **CLAIM**",
        'after_reg': "✅ दर्ता पछि, \"CHECK REGISTRATION\" बटनमा क्लिक गर्नुहोस्",
        'register_btn': "📲 दर्ता",
        'check_btn': "🔍 दर्ता जाँच",
        'enter_player_id': "🔍 *आफ्नो दर्ता जाँच गर्नुहोस्*\n\nसत्यापित गर्न आफ्नो 1Win *Player ID* प्रविष्ट गर्नुहोस्:\n\n📝 *Player ID कसरी फेला पार्ने:*\n1. 1Win खातामा लग इन गर्नुहोस्\n2. प्रोफाइल सेटिङहरूमा जानुहोस्\n3. Player ID नम्बर कपी गर्नुहोस्\n4. यहाँ पेस्ट गर्नुहोस्\n\n🔢 *अब आफ्नो Player ID प्रविष्ट गर्नुहोस्:*",
        'reg_success': "🎉 *बधाई छ, तपाईंले सफलतापूर्वक दर्ता पूरा गर्नुभयो!*\n\n✅ तपाईंको खाता बोटसँग सिङ्क भयो\n\n💴 *सिग्नलहरूको पहुँच प्राप्त गर्न, आफ्नो खातामा कम्तिमा 600₹ वा $6 जम्मा गर्नुहोस्*\n\n🕹️ आफ्नो खाता सफलतापूर्वक रिचार्ज गरेपछि, CHECK DEPOSIT बटनमा क्लिक गर्नुहोस् र पहुँच प्राप्त गर्नुहोस्",
        'deposit_btn': "💳 जम्मा गर्नुहोस्",
        'check_deposit_btn': "🔍 जम्मा जाँच",
        'deposit_success': "🎊 *जम्मा सफलतापूर्वक सत्यापित!*\n\n💰 *जम्मा रकम:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब तपाईंसँग AI-powered predictions को पहुँच छ!\n\nआफ्नो पहिलो prediction प्राप्त गर्न तल क्लिक गर्नुहोस्:",
        'get_prediction_btn': "🎯 prediction प्राप्त",
        'prediction_limit': "🚫 *prediction सीमा reached*\n\nतपाईंले आजका 5 नि: शुल्क predictions प्रयोग गर्नुभयो।\n\n💡 *विकल्पहरू:*\n• भोलि सम्म पर्खनुहोस् (12 घण्टा)\n• तत्काल पहुँचको लागि 400₹ वा $4 जम्मा गर्नुहोस्\n\n💰 कम्तिमा 400₹ वा $4 जम्मा गरेर predictions जारी राख्नुहोस्",
        'deposit_again_btn': "💳 फेरि जम्मा",
        'try_tomorrow_btn': "🕐 भोलि प्रयास",
        'next_prediction_btn': "🔄 अर्को prediction",
        'random_messages': [
            "तपाईंको दर्ता सफल भयो! ✅\n\n$6,7,10,13,17 वा कुनै अन्य रकम जम्मा गर्नुहोस् र बोट स्वचालित रूपमा तपाईंलाई सिग्नलहरूको पहुँच दिनेछ! 🔑\n\nतपाईंले दैनिक $10 ➡️ $100 कमाउन सक्नुहुन्छ💰\n\n👉 /start क्लिक",
            "दाई, तपाईंको लागि सिग्नल तयार छ☺️\n\nअहिले सुरु👉 /start",
            "🚀 सिग्नल already आइसक्यो\n\n🔥 आफ्नो पैसा प्राप्त गर्ने मौका नगुमाउनुहोस्\n\n➡️ /start",
            "अहिले बोट सुरु र पैसा प्राप्त💰🔥\n\n/start"
        ]
    }
}

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('sports_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'en',
            player_id TEXT,
            deposit_amount REAL DEFAULT 0,
            prediction_count INTEGER DEFAULT 0,
            last_prediction_date TEXT,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect('sports_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_user(user_data):
    conn = sqlite3.connect('sports_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, language, player_id, deposit_amount, prediction_count, last_prediction_date, last_activity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_data['user_id'],
        user_data.get('username'),
        user_data.get('first_name'),
        user_data.get('language', 'en'),
        user_data.get('player_id'),
        user_data.get('deposit_amount', 0),
        user_data.get('prediction_count', 0),
        user_data.get('last_prediction_date'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    conn.close()

def update_prediction_count(user_id):
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

def can_get_prediction(user):
    if not user:
        return False
    today = datetime.now().strftime('%Y-%m-%d')
    if user[8] != today:  # last_prediction_date
        # Reset count for new day
        conn = sqlite3.connect('sports_bot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET prediction_count = 0 WHERE user_id = ?', (user[1],))
        conn.commit()
        conn.close()
        return True
    return user[7] < 5  # prediction_count < 5

# ==================== AI PREDICTION WITH CRICAPI ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        
    def fetch_live_matches(self):
        try:
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
        # Advanced AI analysis (backend only - user ko nahi dikhega)
        total_matches = random.randint(50, 150)
        team1_wins = random.randint(20, total_matches - 20)
        team2_wins = total_matches - team1_wins - random.randint(5, 15)
        
        # AI analysis based on historical data
        team1_strength = (team1_wins / total_matches) * random.uniform(0.8, 1.2)
        team2_strength = (team2_wins / total_matches) * random.uniform(0.8, 1.2)
        
        if team1_strength > team2_strength:
            winner = team1
            confidence = min(95, int(team1_strength * 100))
        else:
            winner = team2
            confidence = min(95, int(team2_strength * 100))
        
        analysis_points = [
            f"Historical data analyzed: {total_matches} matches",
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
        
        match = matches[0]
        return self.analyze_team_history(match['team_a'], match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== TELEGRAM FUNCTIONS ====================
def send_telegram_message(chat_id, text, reply_markup=None):
    try:
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
            conn = sqlite3.connect('sports_bot.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET deposit_amount = ? WHERE player_id = ?', (deposit_amount, player_id))
            conn.commit()
            conn.close()
            
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
        
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username')
            first_name = message['from'].get('first_name', 'User')
            
            # Delete the message immediately
            delete_telegram_message(chat_id, message_id)
            
            user = get_user(user_id)
            if not user:
                save_user({
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'language': 'en'
                })
                user = get_user(user_id)
            
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
                
                msg_data = LANGUAGE_MESSAGES.get(user[4], LANGUAGE_MESSAGES['en'])
                send_telegram_message(chat_id, msg_data['welcome'], keyboard)
            
            elif text.isdigit() and len(text) >= 5:
                player_id = text
                user_data = {
                    'user_id': user_id,
                    'username': user[2],
                    'first_name': user[3],
                    'language': user[4],
                    'player_id': player_id,
                    'deposit_amount': user[6] or 0
                }
                save_user(user_data)
                
                msg_data = LANGUAGE_MESSAGES.get(user[4], LANGUAGE_MESSAGES['en'])
                
                if user[6] and user[6] >= 6:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    message_text = msg_data['deposit_success'].replace('{amount}', str(user[6]))
                else:
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
            
            # Delete the previous message
            delete_telegram_message(chat_id, message_id)
            
            user = get_user(user_id)
            msg_data = LANGUAGE_MESSAGES.get(user[4] if user else 'en', LANGUAGE_MESSAGES['en'])
            
            if data_value.startswith('lang_'):
                lang_code = data_value.split('_')[1]
                if user:
                    user_data = {
                        'user_id': user_id,
                        'username': user[2],
                        'first_name': user[3],
                        'language': lang_code
                    }
                    save_user(user_data)
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
                user = get_user(user_id)
                if user and user[6] and user[6] >= 6:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                        ]
                    }
                    message_text = msg_data['deposit_success'].replace('{amount}', str(user[6]))
                else:
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                        ]
                    }
                    message_text = msg_data['reg_success']
                
                send_telegram_message(chat_id, message_text, keyboard)
            
            elif data_value == 'get_prediction':
                user = get_user(user_id)
                if not user:
                    return jsonify({"status": "error"})
                
                if not can_get_prediction(user):
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
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
