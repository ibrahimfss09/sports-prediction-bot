from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime, timedelta
import time
import json

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = os.environ.get('CRICAPI_KEY')
VERCEL_URL = os.environ.get('VERCEL_URL', 'sports-prediction-bot.vercel.app')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Database simulation
users_storage = {}
player_registrations = {}
player_deposits = {}

# ==================== COMPLETE 5 LANGUAGES ====================
LANGUAGE_MESSAGES = {
    'en': {
        'welcome': "🌍 *Select Your Preferred Language:*",
        'selected': "✅ You selected English!",
        'register_title': "🌐 *Step 1 - Register*",
        'account_new': "‼️ *THE ACCOUNT MUST BE NEW*",
        'instruction1': "1️⃣ If after clicking the \"REGISTER\" button you get to the old account, you need to log out of it and click the button again.",
        'instruction2': "2️⃣ Specify a promocode during registration: **CLAIM**",
        'after_reg': "✅ After REGISTRATION, click the \"CHECK REGISTRATION\" button",
        'register_btn': "📲 REGISTER NOW",
        'check_btn': "🔍 CHECK REGISTRATION",
        'enter_player_id': "🔍 *Check Your Registration*\n\nPlease enter your 1Win *Player ID* to verify:\n\n📝 *How to find Player ID:*\n1. Login to 1Win account\n2. Go to Profile Settings\n3. Copy Player ID number\n4. Paste it here\n\n🔢 *Enter your Player ID now:*",
        'loading_registration': "⏳ *Please wait few seconds, your registration is loading...*",
        'reg_success': "🎉 *Great, you have successfully completed registration!*\n\n✅ Your account is synchronized with the bot\n\n💴 *To gain access to signals, deposit your account (make a deposit) with at least 600₹ or $6 in any currency*\n\n🕹️ After successfully replenishing your account, click on the CHECK DEPOSIT button and gain access",
        'reg_not_found': "❌ *Sorry, You're Not Registered!*\n\nPlease click the REGISTER button first and complete your registration using our affiliate link.\n\nAfter successful registration, come back and enter your Player ID.",
        'deposit_btn': "💳 DEPOSIT NOW",
        'check_deposit_btn': "🔍 CHECK DEPOSIT",
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\nClick below to get your first prediction:",
        'deposit_not_found': "💰 *Deposit Not Found!*\n\nYou have registered successfully but no deposit detected yet.\n\n💵 Please make a deposit of at least $6 to get prediction access.",
        'get_prediction_btn': "🎯 GET PREDICTION",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 20 free predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow for new predictions\n• Deposit 400₹ or $4 for immediate access\n\n💰 Continue predictions by depositing at least 400₹ or $4",
        'deposit_again_btn': "💳 DEPOSIT AGAIN",
        'try_tomorrow_btn': "🕐 TRY TOMORROW",
        'next_prediction_btn': "🔄 NEXT PREDICTION",
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
        'register_btn': "📲 पंजीकरण करें",
        'check_btn': "🔍 पंजीकरण जांचें",
        'enter_player_id': "🔍 *अपना पंजीकरण जांचें*\n\nकृपया सत्यापित करने के लिए अपना 1Win *Player ID* दर्ज करें:\n\n📝 *Player ID कैसे ढूंढें:*\n1. 1Win अकाउंट में लॉगिन करें\n2. प्रोफाइल सेटिंग्स पर जाएं\n3. Player ID नम्बर कॉपी करें\n4. यहाँ पेस्ट करें\n\n🔢 *अब अपना Player ID दर्ज करें:*",
        'loading_registration': "⏳ *कृपया कुछ सेकंड प्रतीक्षा करें, आपका पंजीकरण लोड हो रहा है...*",
        'reg_success': "🎉 *बधाई हो, आपने सफलतापूर्वक पंजीकरण पूरा कर लिया है!*\n\n✅ आपका खाता बॉट के साथ सिंक हो गया है\n\n💴 *सिग्नल तक पहुंच प्राप्त करने के लिए, अपने खाते में कम से कम 600₹ या $6 जमा करें*\n\n🕹️ अपना खाता सफलतापूर्वक रिचार्ज करने के बाद, CHECK DEPOSIT बटन पर क्लिक करें और पहुंच प्राप्त करें",
        'reg_not_found': "❌ *क्षमा करें, आप पंजीकृत नहीं हैं!*\n\nकृपया पहले REGISTER बटन पर क्लिक करें और हमारे एफिलिएट लिंक का उपयोग करके अपना पंजीकरण पूरा करें।\n\nसफल पंजीकरण के बाद, वापस आएं और अपना Player ID दर्ज करें।",
        'deposit_btn': "💳 जमा करें",
        'check_deposit_btn': "🔍 जमा जांचें",
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'deposit_not_found': "💰 *जमा नहीं मिला!*\n\nआपने सफलतापूर्वक पंजीकरण कर लिया है लकिन अभी तक कोई जमा नहीं detected हुआ है।\n\n💵 कृपया भविष्यवाणी तक पहुंच प्राप्त करने के लिए कम से कम $6 जमा करें।",
        'get_prediction_btn': "🎯 भविष्यवाणी प्राप्त करें",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 20 मुफ्त भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• नई भविष्यवाणियों के लिए कल तक प्रतीक्षा करें\n• तुरंत पहुंच के लिए 400₹ या $4 जमा करें\n\n💰 कम से कम 400₹ या $4 जमा करके भविष्यवाणियाँ जारी रखें",
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
    },
    'bn': {
        'welcome': "🌍 *আপনার ভাষা নির্বাচন করুন:*",
        'selected': "✅ আপনি বাংলা নির্বাচন করেছেন!",
        'register_title': "🌐 *ধাপ 1 - নিবন্ধন*",
        'account_new': "‼️ *অ্যাকাউন্টটি নতুন হতে হবে*",
        'instruction1': "1️⃣ যদি \"REGISTER\" বাটনে ক্লিক করার পরে আপনি পুরানো অ্যাকাউন্টে আসেন, তাহলে আপনাকে এটি থেকে লগ আউট করতে হবে এবং আবার বাটনে ক্লিক করতে হবে।",
        'instruction2': "2️⃣ নিবন্ধনের সময় একটি প্রোমোকোড নির্দিষ্ট করুন: **CLAIM**",
        'after_reg': "✅ নিবন্ধনের পরে, \"CHECK REGISTRATION\" বাটনে ক্লিক করুন",
        'register_btn': "📲 নিবন্ধন করুন",
        'check_btn': "🔍 নিবন্ধন পরীক্ষা",
        'enter_player_id': "🔍 *আপনার নিবন্ধন পরীক্ষা করুন*\n\nযাচাই করার জন্য আপনার 1Win *Player ID* লিখুন:\n\n📝 *Player ID কিভাবে খুঁজে পাবেন:*\n1. 1Win অ্যাকাউন্টে লগইন করুন\n2. প্রোফাইল সেটিংসে যান\n3. Player ID নম্বর কপি করুন\n4. এখানে পেস্ট করুন\n\n🔢 *এখন আপনার Player ID লিখুন:*",
        'loading_registration': "⏳ *অনুগ্রহ করে কয়েক সেকেন্ড অপেক্ষা করুন, আপনার নিবন্ধন লোড হচ্ছে...*",
        'reg_success': "🎉 *অভিনন্দন, আপনি সফলভাবে নিবন্ধন সম্পন্ন করেছেন!*\n\n✅ আপনার অ্যাকাউন্ট বটের সাথে সিঙ্ক হয়েছে\n\n💴 *সিগন্যাল অ্যাক্সেস পেতে, আপনার অ্যাকাউন্টে কমপক্ষে 600₹ বা $6 জমা করুন*\n\n🕹️ আপনার অ্যাকাউন্ট সফলভাবে রিচার্জ করার পর, CHECK DEPOSIT বাটনে ক্লিক করুন এবং অ্যাক্সেস পান",
        'reg_not_found': "❌ *দুঃখিত, আপনি নিবন্ধিত নন!*\n\nঅনুগ্রহ করে প্রথমে REGISTER বাটনে ক্লিক করুন এবং আমাদের অ্যাফিলিয়েট লিঙ্ক ব্যবহার করে আপনার নিবন্ধন সম্পূর্ণ করুন।\n\nসফল নিবন্ধনের পরে, ফিরে আসুন এবং আপনার Player ID লিখুন।",
        'deposit_btn': "💳 জমা করুন",
        'check_deposit_btn': "🔍 জমা পরীক্ষা",
        'deposit_success': "🎊 *জমা সফলভাবে যাচাই করা হয়েছে!*\n\n💰 *জমার পরিমাণ:* ${amount}\n✅ *স্ট্যাটাস:* যাচাইকৃত\n\n🎯 এখন আপনার AI-চালিত ভবিষ্যদ্বাণী অ্যাক্সেস আছে!\n\nআপনার প্রথম ভবিষ্যদ্বাণী পেতে নীচে ক্লিক করুন:",
        'deposit_not_found': "💰 *জমা পাওয়া যায়নি!*\n\nআপনি সফলভাবে নিবন্ধন করেছেন কিন্তু এখনও কোন জমা সনাক্ত করা যায়নি।\n\n💵 ভবিষ্যদ্বাণী অ্যাক্সেস পেতে কমপক্ষে $6 জমা করুন।",
        'get_prediction_btn': "🎯 ভবিষ্যদ্বাণী পান",
        'prediction_limit': "🚫 *ভবিষ্যদ্বাণী সীমা reached*\n\nআপনি আজকের 20টি বিনামূল্যের ভবিষ্যদ্বাণী ব্যবহার করেছেন।\n\n💡 *বিকল্প:*\n• নতুন ভবিষ্যদ্বাণীর জন্য আগামীকাল পর্যন্ত অপেক্ষা করুন\n• তাত্ক্ষণিক অ্যাক্সেসের জন্য 400₹ বা $4 জমা করুন\n\n💰 কমপক্ষে 400₹ বা $4 জমা করে ভবিষ্যদ্বাণী চালিয়ে যান",
        'deposit_again_btn': "💳 আবার জমা করুন",
        'try_tomorrow_btn': "🕐 আগামীকাল চেষ্টা করুন",
        'next_prediction_btn': "🔄 পরবর্তী ভবিষ্যদ্বাণী",
        'prediction_text': "🎯 *AI ক্রিকেট ভবিষ্যদ্বাণী* 🤖\n\n🏟️ *ম্যাচ:* {team_a} vs {team_b}\n📊 *ভবিষ্যদ্বাণী:* {prediction}\n✅ *আত্মবিশ্বাস:* {confidence}%\n\n📈 *বিশ্লেষণ:*\n{analysis}\n\n⚠️ *AI ভবিষ্যদ্বাণী - দায়িত্ব সহকারে বেট করুন*",
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
        'register_btn': "📲 رجسٹریشن کریں",
        'check_btn': "🔍 رجسٹریشن چیک",
        'enter_player_id': "🔍 *اپنی رجسٹریشن چیک کریں*\n\nتصدیق کے لیے اپنا 1Win *Player ID* درج کریں:\n\n📝 *Player ID کیسے ڈھونڈیں:*\n1. 1Win اکاؤنٹ میں لاگ ان کریں\n2. پروفائل سیٹنگز پر جائیں\n3. Player ID نمبر کاپی کریں\n4. یہاں پیسٹ کریں\n\n🔢 *اب اپنا Player ID درج کریں:*",
        'loading_registration': "⏳ *براہ کرم کچھ سیکنڈ انتظار کریں، آپ کی رجسٹریشن لوڈ ہو رہی ہے...*",
        'reg_success': "🎉 *مبارک ہو، آپ نے کامیابی کے ساتھ رجسٹریشن مکمل کر لی ہے!*\n\n✅ آپ کا اکاؤنٹ بوٹ کے ساتھ sync ہو گیا ہے\n\n💴 *سگنلز تک رسائی حاصل کرنے کے لیے، اپنے اکاؤنٹ میں کم از کم 600₹ یا $6 جمع کروائیں*\n\n🕹️ اپنا اکاؤنٹ کامیابی سے ریچارج کرنے کے بعد، CHECK DEPOSIT بٹن پر کلک کریں اور رسائی حاصل کریں",
        'reg_not_found': "❌ *معذرت، آپ رجسٹرڈ نہیں ہیں!*\n\nبراہ کرم پہلے REGISTER بٹن پر کلک کریں اور ہمارے affiliate link کا استعمال کرتے ہوئے اپنی رجسٹریشن مکمل کریں۔\n\nکامیاب رجسٹریشن کے بعد، واپس آئیں اور اپنا Player ID درج کریں۔",
        'deposit_btn': "💳 جمع کروائیں",
        'check_deposit_btn': "🔍 جمع چیک",
        'deposit_success': "🎊 *جمع کامیابی سے تصدیق ہو گئی!*\n\n💰 *جمع کی رقم:* ${amount}\n✅ *حالت:* تصدیق شدہ\n\n🎯 اب آپ کے پاس AI-powered predictions تک رسائی ہے!\n\nاپنی پہلی prediction حاصل کرنے کے لیے نیچے کلک کریں:",
        'deposit_not_found': "💰 *جمع نہیں ملی!*\n\nآپ نے کامیابی کے ساتھ رجسٹریشن کر لی ہے لیکن ابھی تک کوئی جمع کا پتہ نہیں چلا ہے۔\n\n💵 prediction تک رسائی حاصل کرنے کے لیے کم از کم $6 جمع کروائیں۔",
        'get_prediction_btn': "🎯 prediction حاصل",
        'prediction_limit': "🚫 *prediction حد reached*\n\nآپ نے آج کی 20 مفت predictions استعمال کر لی ہیں۔\n\n💡 *اختیارات:*\n• نئی predictions کے لیے کل تک انتظار کریں\n• فوری رسائی کے لیے 400₹ یا $4 جمع کروائیں\n\n💰 کم از کم 400₹ یا $4 جمع کروا کر predictions جاری رکھیں",
        'deposit_again_btn': "💳 دوبارہ جمع",
        'try_tomorrow_btn': "🕐 کل کوشش",
        'next_prediction_btn': "🔄 اگلی prediction",
        'prediction_text': "🎯 *AI کرکٹ prediction* 🤖\n\n🏟️ *مقابلہ:* {team_a} vs {team_b}\n📊 *prediction:* {prediction}\n✅ *اعتماد:* {confidence}%\n\n📈 *تجزیہ:*\n{analysis}\n\n⚠️ *AI prediction - ذمہ داری سے جوا کھیلیں*",
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
        'register_btn': "📲 दर्ता गर्नुहोस्",
        'check_btn': "🔍 दर्ता जाँच",
        'enter_player_id': "🔍 *आफ्नो दर्ता जाँच गर्नुहोस्*\n\nसत्यापित गर्न आफ्नो 1Win *Player ID* प्रविष्ट गर्नुहोस्:\n\n📝 *Player ID कसरी फेला पार्ने:*\n1. 1Win खातामा लग इन गर्नुहोस्\n2. प्रोफाइल सेटिङहरूमा जानुहोस्\n3. Player ID नम्बर कपी गर्नुहोस्\n4. यहाँ पेस्ट गर्नुहोस्\n\n🔢 *अब आफ्नो Player ID प्रविष्ट गर्नुहोस्:*",
        'loading_registration': "⏳ *कृपया केही सेकेन्ड पर्खनुहोस्, तपाईंको दर्ता लोड हुदैछ...*",
        'reg_success': "🎉 *बधाई छ, तपाईंले सफलतापूर्वक दर्ता पूरा गर्नुभयो!*\n\n✅ तपाईंको खाता बोटसँग सिङ्क भयो\n\n💴 *सिग्नलहरूको पहुँच प्राप्त गर्न, आफ्नो खातामा कम्तिमा 600₹ वा $6 जम्मा गर्नुहोस्*\n\n🕹️ आफ्नो खाता सफलतापूर्वक रिचार्ज गरेपछि, CHECK DEPOSIT बटनमा क्लिक गर्नुहोस् र पहुँच प्राप्त गर्नुहोस्",
        'reg_not_found': "❌ *माफ गर्नुहोस्, तपाईं दर्ता गरिएको छैन!*\n\nकृपया पहिले REGISTER बटनमा क्लिक गर्नुहोस् र हाम्रो एफिलिएट लिङ्क प्रयोग गरेर आफ्नो दर्ता पूरा गर्नुहोस्।\n\nसफल दर्ता पछि, फर्कनुहोस् र आफ्नो Player ID प्रविष्ट गर्नुहोस्।",
        'deposit_btn': "💳 जम्मा गर्नुहोस्",
        'check_deposit_btn': "🔍 जम्मा जाँच",
        'deposit_success': "🎊 *जम्मा सफलतापूर्वक सत्यापित!*\n\n💰 *जम्मा रकम:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब तपाईंसँग AI-powered predictions को पहुँच छ!\n\nआफ्नो पहिलो prediction प्राप्त गर्न तल क्लिक गर्नुहोस्:",
        'deposit_not_found': "💰 *जम्मा फेला परेन!*\n\nतपाईंले सफलतापूर्वक दर्ता गर्नुभएको छ तर अहिले सम्म कुनै जम्मा पत्ता लागेको छैन।\n\n💵 prediction पहुँच प्राप्त गर्न कम्तिमा $6 जम्मा गर्नुहोस्।",
        'get_prediction_btn': "🎯 prediction प्राप्त",
        'prediction_limit': "🚫 *prediction सीमा reached*\n\nतपाईंले आजका 20 नि: शुल्क predictions प्रयोग गर्नुभयो।\n\n💡 *विकल्पहरू:*\n• नयाँ predictions को लागि भोलि सम्म पर्खनुहोस्\n• तत्काल पहुँचको लागि 400₹ वा $4 जम्मा गर्नुहोस्\n\n💰 कम्तिमा 400₹ वा $4 जम्मा गरेर predictions जारी राख्नुहोस्",
        'deposit_again_btn': "💳 फेरि जम्मा",
        'try_tomorrow_btn': "🕐 भोलि प्रयास",
        'next_prediction_btn': "🔄 अर्को prediction",
        'prediction_text': "🎯 *AI क्रिकेट prediction* 🤖\n\n🏟️ *खेल:* {team_a} vs {team_b}\n📊 *prediction:* {prediction}\n✅ *विश्वास:* {confidence}%\n\n📈 *विश्लेषण:*\n{analysis}\n\n⚠️ *AI prediction - जिम्मेवारी संग जुआ खेल्नुहोस्*",
        'random_messages': [
            "तपाईंको दर्ता सफल भयो! ✅\n\n$6,7,10,13,17 वा कुनै अन्य रकम जम्मा गर्नुहोस् र बोट स्वचालित रूपमा तपाईंलाई सिग्नलहरूको पहुँच दिनेछ! 🔑\n\nतपाईंले दैनिक $10 ➡️ $100 कमाउन सक्नुहुन्छ💰\n\n👉 /start क्लिक",
            "दाई, तपाईंको लागि सिग्नल तयार छ☺️\n\nअहिले सुरु👉 /start",
            "🚀 सिग्नल already आइसक्यो\n\n🔥 आफ्नो पैसा प्राप्त गर्ने मौका नगुमाउनुहोस्\n\n➡️ /start",
            "अहिले बोट सुरु र पैसा प्राप्त💰🔥\n\n/start"
        ]
    }
}

# ==================== ENHANCED AI PREDICTION WITH CRICAPI ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        self.last_fetch_time = None
        self.cached_matches = []
        self.used_matches = set()  # Track used matches to avoid repetition
        
    def fetch_live_matches(self):
        try:
            # Cache matches for 10 minutes to avoid too many API calls
            current_time = datetime.now()
            if (self.last_fetch_time and 
                (current_time - self.last_fetch_time).seconds < 600 and 
                self.cached_matches):
                print("🔄 Returning cached matches")
                return self.cached_matches
                
            if not self.api_key:
                print("❌ No CricAPI key found, using fallback matches")
                return self.get_fallback_matches()
                
            print("🌐 Fetching live matches from CricAPI...")
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 API Response Status: {data.get('status')}")
                
                if data.get('status') == 'success':
                    matches = []
                    api_matches = data.get('data', [])
                    print(f"📈 Total matches from API: {len(api_matches)}")
                    
                    for match in api_matches:
                        try:
                            # Check if match is live or upcoming
                            match_started = match.get('matchStarted', False)
                            match_ended = match.get('matchEnded', False)
                            status = match.get('status', '').lower()
                            
                            # Include live matches and recently started matches
                            is_live = (match_started and not match_ended) or 'live' in status or 'running' in status or 'started' in status
                            
                            if is_live:
                                # Get team names safely
                                team_info = match.get('teamInfo', [])
                                if len(team_info) >= 2:
                                    team_a = team_info[0].get('name', 'Team A').strip()
                                    team_b = team_info[1].get('name', 'Team B').strip()
                                    
                                    # Skip if teams are not properly defined
                                    if team_a and team_b and team_a != 'Team A' and team_b != 'Team B':
                                        match_data = {
                                            'id': match.get('id', ''),
                                            'team_a': team_a,
                                            'team_b': team_b,
                                            'date': match.get('date', ''),
                                            'series': match.get('series', 'International'),
                                            'status': match.get('status', 'Live'),
                                            'venue': match.get('venue', 'Unknown'),
                                            'score': match.get('score', [])
                                        }
                                        matches.append(match_data)
                                        print(f"✅ Found live match: {team_a} vs {team_b} - {match.get('status')}")
                        except Exception as e:
                            print(f"⚠️ Error processing match: {e}")
                            continue
                    
                    if matches:
                        self.cached_matches = matches
                        self.last_fetch_time = current_time
                        print(f"🎯 Total live matches found: {len(matches)}")
                        return matches
                    else:
                        print("❌ No live matches found in API response, using fallback")
                        return self.get_fallback_matches()
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"❌ API Error: {error_msg}")
                    return self.get_fallback_matches()
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return self.get_fallback_matches()
                
        except Exception as e:
            print(f"❌ CricAPI Error: {e}")
            return self.get_fallback_matches()
    
    def get_fallback_matches(self):
        """Get realistic fallback matches with current dates"""
        today = datetime.now()
        fallback_matches = [
            {
                'id': 'fallback_1',
                'team_a': 'India',
                'team_b': 'Pakistan', 
                'date': today.strftime('%Y-%m-%d'),
                'series': 'Asia Cup 2024',
                'status': 'Live',
                'venue': 'Dubai International Stadium',
                'score': []
            },
            {
                'id': 'fallback_2',
                'team_a': 'Australia',
                'team_b': 'England',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'World Cup 2024',
                'status': 'Live',
                'venue': 'Melbourne Cricket Ground',
                'score': []
            },
            {
                'id': 'fallback_3', 
                'team_a': 'South Africa',
                'team_b': 'New Zealand',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'World Championship',
                'status': 'Live',
                'venue': 'Newlands Cricket Ground',
                'score': []
            },
            {
                'id': 'fallback_4',
                'team_a': 'West Indies',
                'team_b': 'Bangladesh',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'Caribbean Premier League',
                'status': 'Live', 
                'venue': 'Kensington Oval',
                'score': []
            },
            {
                'id': 'fallback_5',
                'team_a': 'Sri Lanka',
                'team_b': 'Afghanistan',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'Asia Cup Qualifiers',
                'status': 'Live',
                'venue': 'R. Premadasa Stadium',
                'score': []
            }
        ]
        print("🔄 Using fallback matches")
        return fallback_matches
    
    def analyze_team_performance(self, team1, team2):
        """Advanced AI analysis with realistic data"""
        # Enhanced team performance database
        team_stats = {
            'india': {'rating': 118, 'home_advantage': 1.2, 'key_players': ['Virat Kohli', 'Rohit Sharma', 'Jasprit Bumrah'], 'strength': 'Batting'},
            'pakistan': {'rating': 112, 'home_advantage': 1.1, 'key_players': ['Babar Azam', 'Mohammad Rizwan', 'Shaheen Afridi'], 'strength': 'Bowling'},
            'australia': {'rating': 116, 'home_advantage': 1.3, 'key_players': ['Steve Smith', 'David Warner', 'Pat Cummins'], 'strength': 'All-round'},
            'england': {'rating': 114, 'home_advantage': 1.2, 'key_players': ['Joe Root', 'Jos Buttler', 'Ben Stokes'], 'strength': 'Batting'},
            'south africa': {'rating': 106, 'home_advantage': 1.1, 'key_players': ['Aiden Markram', 'Kagiso Rabada', 'David Miller'], 'strength': 'Bowling'},
            'new zealand': {'rating': 108, 'home_advantage': 1.1, 'key_players': ['Kane Williamson', 'Trent Boult', 'Devon Conway'], 'strength': 'All-round'},
            'west indies': {'rating': 92, 'home_advantage': 1.4, 'key_players': ['Shai Hope', 'Alzarri Joseph', 'Jason Holder'], 'strength': 'Power Hitting'},
            'bangladesh': {'rating': 88, 'home_advantage': 1.3, 'key_players': ['Shakib Al Hasan', 'Mehidy Hasan', 'Taskin Ahmed'], 'strength': 'Spin'},
            'sri lanka': {'rating': 90, 'home_advantage': 1.3, 'key_players': ['Kusal Mendis', 'Maheesh Theekshana', 'Dasun Shanaka'], 'strength': 'Spin'},
            'afghanistan': {'rating': 82, 'home_advantage': 1.2, 'key_players': ['Rashid Khan', 'Mohammad Nabi', 'Rahmanullah Gurbaz'], 'strength': 'Spin'}
        }
        
        # Get team ratings
        team1_lower = team1.lower()
        team2_lower = team2.lower()
        
        team1_data = team_stats.get(team1_lower, {'rating': 95, 'home_advantage': 1.0, 'key_players': ['Key Players'], 'strength': 'Balanced'})
        team2_data = team_stats.get(team2_lower, {'rating': 95, 'home_advantage': 1.0, 'key_players': ['Key Players'], 'strength': 'Balanced'})
        
        team1_rating = team1_data['rating']
        team2_rating = team2_data['rating']
        
        # Add random form factor (current performance) - more realistic
        team1_form = random.uniform(0.85, 1.25)
        team2_form = random.uniform(0.85, 1.25)
        
        # Calculate strength with form
        team1_strength = team1_rating * team1_form
        team2_strength = team2_rating * team2_form
        
        # Determine winner and confidence
        total_strength = team1_strength + team2_strength
        team1_probability = team1_strength / total_strength
        team2_probability = team2_strength / total_strength
        
        if team1_probability > team2_probability:
            winner = team1
            confidence = max(60, min(94, int(team1_probability * 100)))
        else:
            winner = team2
            confidence = max(60, min(94, int(team2_probability * 100)))
        
        # Generate realistic analysis
        analysis_points = [
            f"🏆 **Team Ratings**: {team1} ({team1_rating}) vs {team2} ({team2_rating})",
            f"📈 **Current Form**: {team1} ({team1_form:.1f}x) vs {team2} ({team2_form:.1f}x)",
            f"🎯 **Key Players**: {', '.join(team1_data['key_players'][:2])} vs {', '.join(team2_data['key_players'][:2])}",
            f"💪 **Team Strength**: {team1_data['strength']} vs {team2_data['strength']}",
            f"🏟️ **Match Conditions**: Pitch analysis favors {random.choice(['batting first', 'bowling first', 'balanced play'])}",
            f"🌦️ **Weather Impact**: {random.choice(['Clear skies', 'Slight humidity', 'Good conditions', 'Dew factor later'])}"
        ]
        
        # Shuffle and select 3-4 analysis points
        random.shuffle(analysis_points)
        selected_analysis = analysis_points[:random.randint(3, 4)]
        
        # Different prediction types for variety
        prediction_types = [
            f"{winner} to win",
            f"{winner} victory predicted", 
            f"{winner} expected to dominate",
            f"Strong chances for {winner}",
            f"{winner} favored to win",
            f"{winner} likely to emerge victorious",
            f"Better odds for {winner}",
            f"{winner} with higher winning probability"
        ]
        
        return {
            'prediction': random.choice(prediction_types),
            'confidence': confidence,
            'analysis': "\n".join(selected_analysis),
            'team_a': team1,
            'team_b': team2,
            'user_analysis': f"🤖 **AI Analysis**: Comprehensive analysis of team ratings ({team1_rating} vs {team2_rating}), current form, and match conditions suggests {winner} has stronger chances with {confidence}% confidence. Consider recent team performances and playing conditions."
        }
    
    def get_prediction(self):
        """Get a unique prediction each time from live matches"""
        matches = self.fetch_live_matches()
        
        if not matches:
            print("❌ No matches available, using fallback")
            fallback_match = random.choice(self.get_fallback_matches())
            return self.analyze_team_performance(fallback_match['team_a'], fallback_match['team_b'])
        
        # Filter out recently used matches
        available_matches = [m for m in matches if m['id'] not in self.used_matches]
        
        if not available_matches:
            # Reset used matches if all have been used
            print("🔄 Resetting used matches cache")
            self.used_matches.clear()
            available_matches = matches
        
        # Select a random match from available matches
        selected_match = random.choice(available_matches)
        
        # Mark this match as used
        self.used_matches.add(selected_match['id'])
        print(f"🎯 Selected match: {selected_match['team_a']} vs {selected_match['team_b']} (Used: {len(self.used_matches)} matches)")
        
        return self.analyze_team_performance(selected_match['team_a'], selected_match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== USER MANAGEMENT ====================
def get_user(user_id):
    if user_id not in users_storage:
        users_storage[user_id] = {
            'user_id': user_id,
            'language': 'en',
            'prediction_count': 0,
            'last_prediction_date': None,
            'player_id': None,
            'deposit_amount': 0,
            'is_registered': False,
            'registration_date': None
        }
    return users_storage[user_id]

def save_user(user_data):
    users_storage[user_data['user_id']] = user_data

def can_get_prediction(user_id):
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user['last_prediction_date'] != today:
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
    Real postback verification with 1Win system
    """
    time.sleep(2)  # Simulate API call
    
    # Check if player is in our registration records (from postback)
    if player_id in player_registrations:
        deposit_amount = player_deposits.get(player_id, 0)
        return {
            'registered': True,
            'deposit_amount': deposit_amount,
            'message': 'Player verified successfully'
        }
    else:
        return {
            'registered': False,
            'deposit_amount': 0,
            'message': 'Player not found in system'
        }

# ==================== TELEGRAM FUNCTIONS ====================
def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
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
        
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Edit message error: {e}")
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
        
        # Extract player data with ALL possible parameter names
        player_id = (data.get('player_id') or data.get('id') or 
                    data.get('user_id') or data.get('sub1') or 
                    data.get('sub2') or data.get('sub3'))
        
        status = data.get('status', '')
        
        # Deposit amount - multiple possible parameter names
        deposit_amount = 0
        amount_params = ['amount', 'fdp', 'dep_sum', 'fdp_usd', 'dep_sum_usd', 'sum']
        for param in amount_params:
            if data.get(param):
                try:
                    deposit_amount = float(data.get(param))
                    print(f"💰 Found deposit amount in {param}: ${deposit_amount}")
                    break
                except (ValueError, TypeError):
                    continue
        
        print(f"🔍 Final Extraction - Player: {player_id}, Status: {status}, Amount: ${deposit_amount}")
        
        if not player_id:
            print("❌ No player_id found in postback data")
            return jsonify({"status": "error", "message": "No player ID provided"})
        
        # Always mark as registered when ANY postback received
        player_registrations[player_id] = True
        print(f"✅ Player {player_id} marked as registered")
        
        # Handle different statuses
        if deposit_amount > 0:
            player_deposits[player_id] = deposit_amount
            print(f"💰 Player {player_id} deposit recorded: ${deposit_amount}")
        
        # Update all users with this player_id
        users_updated = 0
        for user_id, user_data in users_storage.items():
            if user_data.get('player_id') == player_id:
                user_data['deposit_amount'] = deposit_amount
                user_data['is_registered'] = True
                save_user(user_data)
                users_updated += 1
                print(f"✅ Updated user {user_id} with player {player_id}")
        
        # Send admin notification
        if deposit_amount > 0:
            send_admin_notification(f"💰 DEPOSIT: Player {player_id} - ${deposit_amount} (Status: {status}) | Users Updated: {users_updated}")
        else:
            send_admin_notification(f"📝 REGISTRATION: Player {player_id} (Status: {status}) | Users Updated: {users_updated}")
        
        return jsonify({
            "status": "success", 
            "player_id": player_id, 
            "deposit": deposit_amount,
            "postback_status": status,
            "users_updated": users_updated,
            "message": "Postback processed successfully"
        })
    
    except Exception as e:
        print(f"❌ Postback error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== MANUAL TESTING ENDPOINTS ====================
@app.route('/test-register/<player_id>', methods=['GET'])
def test_register_player(player_id):
    """Test endpoint to simulate player registration"""
    player_registrations[player_id] = True
    player_deposits[player_id] = 6.0  # Default test deposit
    
    # Update users with this player_id
    for user_id, user_data in users_storage.items():
        if user_data.get('player_id') == player_id:
            user_data['deposit_amount'] = 6.0
            user_data['is_registered'] = True
            save_user(user_data)
    
    return jsonify({
        "status": "success", 
        "player_id": player_id, 
        "deposit": 6.0,
        "message": "Test registration successful"
    })

@app.route('/test-deposit/<player_id>/<amount>', methods=['GET'])
def test_deposit(player_id, amount):
    """Test endpoint to simulate deposit"""
    try:
        deposit_amount = float(amount)
        player_registrations[player_id] = True
        player_deposits[player_id] = deposit_amount
        
        # Update users
        for user_id, user_data in users_storage.items():
            if user_data.get('player_id') == player_id:
                user_data['deposit_amount'] = deposit_amount
                user_data['is_registered'] = True
                save_user(user_data)
        
        return jsonify({
            "status": "success",
            "player_id": player_id,
            "deposit": deposit_amount,
            "message": f"Test deposit of ${deposit_amount} successful"
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid amount"})

# ==================== MAIN BOT HANDLER ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📥 Webhook received:", data)
        
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
                # User entered Player ID
                player_id = text
                user = get_user(user_id)
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                
                # Send loading message
                loading_msg = send_telegram_message(chat_id, msg_data['loading_registration'])
                
                # Verify player registration
                verification = verify_player_registration(player_id)
                
                if verification['registered']:
                    # Player is registered through our affiliate
                    user['player_id'] = player_id
                    user['is_registered'] = True
                    user['deposit_amount'] = verification['deposit_amount']
                    save_user(user)
                    
                    if verification['deposit_amount'] >= 6:
                        # User has deposited enough - show success with prediction button
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]
                            ]
                        }
                        message_text = msg_data['deposit_success'].replace('{amount}', str(verification['deposit_amount']))
                    else:
                        # Registered but no deposit or insufficient
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                            ]
                        }
                        message_text = msg_data['reg_success']
                    
                    # Edit loading message with result
                    if loading_msg and 'result' in loading_msg:
                        edit_telegram_message(chat_id, loading_msg['result']['message_id'], message_text, keyboard)
                    else:
                        send_telegram_message(chat_id, message_text, keyboard)
                else:
                    # Player not found in our system
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['register_btn'], 'url': 'https://mostbet-king.com/5rTs'}]
                        ]
                    }
                    
                    if loading_msg and 'result' in loading_msg:
                        edit_telegram_message(chat_id, loading_msg['result']['message_id'], msg_data['reg_not_found'], keyboard)
                    else:
                        send_telegram_message(chat_id, msg_data['reg_not_found'], keyboard)
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
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
                        [{'text': msg_data['register_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                        [{'text': msg_data['check_btn'], 'callback_data': 'check_registration'}]
                    ]
                }
                
                message_text = f"{msg_data['selected']}\n\n{msg_data['register_title']}\n\n{msg_data['account_new']}\n\n{msg_data['instruction1']}\n\n{msg_data['instruction2']}\n\n{msg_data['after_reg']}"
                edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'check_registration':
                edit_telegram_message(chat_id, message_id, msg_data['enter_player_id'])
            
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
                
                edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'get_prediction':
                if not can_get_prediction(user_id):
                    # 🎯 UPDATED: PREDICTION LIMIT REACHED - SHOW BOTH BUTTONS
                    keyboard = {
                        'inline_keyboard': [
                            [{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                            [{'text': msg_data['try_tomorrow_btn'], 'callback_data': 'try_tomorrow'}]
                        ]
                    }
                    edit_telegram_message(chat_id, message_id, msg_data['prediction_limit'], keyboard)
                else:
                    prediction = ai_predictor.get_prediction()
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
                    
                    edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'try_tomorrow':
                edit_telegram_message(chat_id, message_id, "⏳ Please try again tomorrow for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== BASIC ROUTES ====================
@app.route('/')
def home():
    return """
    <h1>🚀 Sports Prediction Bot</h1>
    <p>✅ Bot is running successfully!</p>
    <p>📊 Stats: <a href="/admin/stats">View Statistics</a></p>
    <p>🔧 Testing: <a href="/test-register/12345">Test Registration</a></p>
    <h3>🎯 1Win Postback URLs:</h3>
    <p>On Registration: https://sports-prediction-bot.vercel.app/1win-postback?player_id={id}&status=registration&amount=0</p>
    <p>On First Deposit: https://sports-prediction-bot.vercel.app/1win-postback?player_id={id}&status=fdp&amount={fdp}</p>
    <p>On Deposit Approval: https://sports-prediction-bot.vercel.app/1win-postback?player_id={id}&status=fd_approved&amount={fdp}</p>
    """

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{VERCEL_URL}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    
    return jsonify({
        "status": "success", 
        "webhook_url": webhook_url,
        "result": response.json()
    })

@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    total_users = len(users_storage)
    registered_users = len([u for u in users_storage.values() if u.get('is_registered')])
    deposited_users = len([u for u in users_storage.values() if u.get('deposit_amount', 0) >= 6])
    active_today = len([u for u in users_storage.values() if u.get('last_prediction_date') == datetime.now().strftime('%Y-%m-%d')])
    
    return jsonify({
        "total_users": total_users,
        "registered_users": registered_users,
        "deposited_users": deposited_users,
        "active_today": active_today,
        "player_registrations": len(player_registrations),
        "player_deposits": len(player_deposits),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)
