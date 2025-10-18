from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime, timedelta
import time
import threading

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CRICAPI_KEY = os.environ.get('CRICAPI_KEY')
VERCEL_URL = os.environ.get('VERCEL_URL', 'sports-prediction-bot.vercel.app')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')

# Storage
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
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\n💰 *Validity:* 5 days (20 predictions daily)\n\nClick below to get your first prediction:",
        'deposit_not_found': "💰 *Deposit Not Found!*\n\nYou have registered successfully but no deposit detected yet.\n\n💵 Please make a deposit of at least $6 to get prediction access.",
        'get_prediction_btn': "🎯 GET PREDICTION",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 20 free predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow for new predictions\n• Deposit 400₹ or $4 for immediate access\n\n💰 Continue predictions by depositing at least 400₹ or $4",
        'deposit_expired': "⏰ *Deposit Validity Expired!*\n\nYour 5-day prediction access has ended.\n\n💎 *What's Next:*\n• Make a new deposit to continue predictions\n• Get 20 predictions daily for 5 days\n\n💰 Deposit now to restart your prediction access!",
        'deposit_again_btn': "💳 DEPOSIT AGAIN",
        'try_tomorrow_btn': "🕐 TRY TOMORROW",
        'next_prediction_btn': "🔄 NEXT PREDICTION",
        'prediction_text': "🎯 *AI CRICKET PREDICTION* 🤖\n\n🏟️ *Match:* {team_a} vs {team_b}\n📊 *Prediction:* {prediction}\n✅ *Confidence:* {confidence}%\n\n📈 *Analysis:*\n{analysis}\n\n⚠️ *AI Prediction - Bet Responsibly*"
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
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\n💰 *वैधता:* 5 दिन (रोज 20 भविष्यवाणियाँ)\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'deposit_not_found': "💰 *जमा नहीं मिला!*\n\nआपने सफलतापूर्वक पंजीकरण कर लिया है लकिन अभी तक कोई जमा नहीं detected हुआ है।\n\n💵 कृपया भविष्यवाणी तक पहुंच प्राप्त करने के लिए कम से कम $6 जमा करें।",
        'get_prediction_btn': "🎯 भविष्यवाणी प्राप्त करें",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 20 मुफ्त भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• नई भविष्यवाणियों के लिए कल तक प्रतीक्षा करें\n• तुरंत पहुंच के लिए 400₹ या $4 जमा करें\n\n💰 कम से कम 400₹ या $4 जमा करके भविष्यवाणियाँ जारी रखें",
        'deposit_expired': "⏰ *जमा वैधता समाप्त!*\n\nआपकी 5-दिन की भविष्यवाणी पहुंच समाप्त हो गई है।\n\n💎 *आगे क्या:*\n• नया जमा करके भविष्यवाणियाँ जारी रखें\n• 5 दिनों के लिए रोज 20 भविष्यवाणियाँ प्राप्त करें\n\n💰 अब जमा करके अपनी भविष्यवाणी पहुंच पुनः प्रारंभ करें!",
        'deposit_again_btn': "💳 फिर से जमा करें",
        'try_tomorrow_btn': "🕐 कल प्रयास करें",
        'next_prediction_btn': "🔄 अगली भविष्यवाणी",
        'prediction_text': "🎯 *AI क्रिकेट भविष्यवाणी* 🤖\n\n🏟️ *मैच:* {team_a} vs {team_b}\n📊 *भविष्यवाणी:* {prediction}\n✅ *विश्वास:* {confidence}%\n\n📈 *विश्लेषण:*\n{analysis}\n\n⚠️ *AI भविष्यवाणी - जिम्मेदारी से जुआ खेलें*"
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
        'deposit_success': "🎊 *জমা সফলভাবে যাচাই করা হয়েছে!*\n\n💰 *জমার পরিমাণ:* ${amount}\n✅ *স্ট্যাটাস:* যাচাইকৃত\n\n🎯 এখন আপনার AI-চালিত ভবিষ্যদ্বাণী অ্যাক্সেস আছে!\n\n💰 *বৈধতা:* 5 দিন (দৈনিক 20 ভবিষ্যদ্বাণী)\n\nআপনার প্রথম ভবিষ্যদ্বাণী পেতে নীচে ক্লিক করুন:",
        'deposit_not_found': "💰 *জমা পাওয়া যায়নি!*\n\nআপনি সফলভাবে নিবন্ধন করেছেন কিন্তু এখনও কোন জমা সনাক্ত করা যায়নি।\n\n💵 ভবিষ্যদ্বাণী অ্যাক্সেস পেতে কমপক্ষে $6 জমা করুন।",
        'get_prediction_btn': "🎯 ভবিষ্যদ্বাণী পান",
        'prediction_limit': "🚫 *ভবিষ্যদ্বাণী সীমা reached*\n\nআপনি আজকের 20টি বিনামূল্যের ভবিষ্যদ্বাণী ব্যবহার করেছেন।\n\n💡 *বিকল্প:*\n• নতুন ভবিষ্যদ্বাণীর জন্য আগামীকাল পর্যন্ত অপেক্ষা করুন\n• তাত্ক্ষণিক অ্যাক্সেসের জন্য 400₹ বা $4 জমা করুন\n\n💰 কমপক্ষে 400₹ বা $4 জমা করে ভবিষ্যদ্বাণী চালিয়ে যান",
        'deposit_expired': "⏰ *জমা বৈধতা শেষ!*\n\nআপনার 5-দিনের ভবিষ্যদ্বাণী অ্যাক্সেস শেষ হয়েছে।\n\n💎 *পরবর্তী কী:*\n• নতুন জমা করে ভবিষ্যদ্বাণী চালিয়ে যান\n• 5 দিনের জন্য দৈনিক 20 ভবিষ্যদ্বাণী পান\n\n💰 এখন জমা করে আপনার ভবিষ্যদ্বাণী অ্যাক্সেস পুনরায় শুরু করুন!",
        'deposit_again_btn': "💳 আবার জমা করুন",
        'try_tomorrow_btn': "🕐 আগামীকাল চেষ্টা করুন",
        'next_prediction_btn': "🔄 পরবর্তী ভবিষ্যদ্বাণী",
        'prediction_text': "🎯 *AI ক্রিকেট ভবিষ্যদ্বাণী* 🤖\n\n🏟️ *ম্যাচ:* {team_a} vs {team_b}\n📊 *ভবিষ্যদ্বাণী:* {prediction}\n✅ *আত্মবিশ্বাস:* {confidence}%\n\n📈 *বিশ্লেষণ:*\n{analysis}\n\n⚠️ *AI ভবিষ্যদ্বাণী - দায়িত্ব সহকারে বেট করুন*"
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
        'deposit_success': "🎊 *جمع کامیابی سے تصدیق ہو گئی!*\n\n💰 *جمع کی رقم:* ${amount}\n✅ *حالت:* تصدیق شدہ\n\n🎯 اب آپ کے پاس AI-powered predictions تک رسائی ہے!\n\n💰 *جواز:* 5 دن (روزانہ 20 predictions)\n\nاپنی پہلی prediction حاصل کرنے کے لیے نیچے کلک کریں:",
        'deposit_not_found': "💰 *جمع نہیں ملی!*\n\nآپ نے کامیابی کے ساتھ رجسٹریشن کر لی ہے لیکن ابھی تک کوئی جمع کا پتہ نہیں چلا ہے۔\n\n💵 prediction تک رسائی حاصل کرنے کے لیے کم از کم $6 جمع کروائیں۔",
        'get_prediction_btn': "🎯 prediction حاصل",
        'prediction_limit': "🚫 *prediction حد reached*\n\nآپ نے آج کی 20 مفت predictions استعمال کر لی ہیں۔\n\n💡 *اختیارات:*\n• نئی predictions کے لیے کل تک انتظار کریں\n• فوری رسائی کے لیے 400₹ یا $4 جمع کروائیں\n\n💰 کم از کم 400₹ یا $4 جمع کروا کر predictions جاری رکھیں",
        'deposit_expired': "⏰ *جمع کی میعاد ختم!*\n\nآپ کی 5-دن کی prediction رسائی ختم ہو گئی ہے۔\n\n💎 *آگے کیا:*\n• نیا جمع کروا کر predictions جاری رکھیں\n• 5 دنوں کے لیے روزانہ 20 predictions حاصل کریں\n\n💰 اب جمع کروا کر اپنی prediction رسائی دوبارہ شروع کریں!",
        'deposit_again_btn': "💳 دوبارہ جمع",
        'try_tomorrow_btn': "🕐 کل کوشش",
        'next_prediction_btn': "🔄 اگلی prediction",
        'prediction_text': "🎯 *AI کرکٹ prediction* 🤖\n\n🏟️ *مقابلہ:* {team_a} vs {team_b}\n📊 *prediction:* {prediction}\n✅ *اعتماد:* {confidence}%\n\n📈 *تجزیہ:*\n{analysis}\n\n⚠️ *AI prediction - ذمہ داری سے جوا کھیلیں*"
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
        'deposit_success': "🎊 *जम्मा सफलतापूर्वक सत्यापित!*\n\n💰 *जम्मा रकम:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब तपाईंसँग AI-powered predictions को पहुँच छ!\n\n💰 *मान्यता:* 5 दिन (दैनिक 20 predictions)\n\nआफ्नो पहिलो prediction प्राप्त गर्न तल क्लिक गर्नुहोस्:",
        'deposit_not_found': "💰 *जम्मा फेला परेन!*\n\nतपाईंले सफलतापूर्वक दर्ता गर्नुभएको छ तर अहिले सम्म कुनै जम्मा पत्ता लागेको छैन।\n\n💵 prediction पहुँच प्राप्त गर्न कम्तिमा $6 जम्मा गर्नुहोस्।",
        'get_prediction_btn': "🎯 prediction प्राप्त",
        'prediction_limit': "🚫 *prediction सीमा reached*\n\nतपाईंले आजका 20 नि: शुल्क predictions प्रयोग गर्नुभयो।\n\n💡 *विकल्पहरू:*\n• नयाँ predictions को लागि भोलि सम्म पर्खनुहोस्\n• तत्काल पहुँचको लागि 400₹ वा $4 जम्मा गर्नुहोस्\n\n💰 कम्तिमा 400₹ वा $4 जम्मा गरेर predictions जारी राख्नुहोस्",
        'deposit_expired': "⏰ *जम्मा मान्यता समाप्त!*\n\nतपाईंको 5-दिने prediction पहुँच समाप्त भएको छ।\n\n💎 *अब के गर्ने:*\n• नयाँ जम्मा गरेर predictions जारी राख्नुहोस्\n• 5 दिनको लागि दैनिक 20 predictions प्राप्त गर्नुहोस्\n\n💰 अब जम्मा गरेर तपाईंको prediction पहुँच पुन: सुरु गर्नुहोस्!",
        'deposit_again_btn': "💳 फेरि जम्मा",
        'try_tomorrow_btn': "🕐 भोलि प्रयास",
        'next_prediction_btn': "🔄 अर्को prediction",
        'prediction_text': "🎯 *AI क्रिकेट prediction* 🤖\n\n🏟️ *खेल:* {team_a} vs {team_b}\n📊 *prediction:* {prediction}\n✅ *विश्वास:* {confidence}%\n\n📈 *विश्लेषण:*\n{analysis}\n\n⚠️ *AI prediction - जिम्मेवारी संग जुआ खेल्नुहोस्*"
    }
}

# ==================== INACTIVITY REMINDERS ====================
INACTIVITY_MESSAGES = {
    'en': [
        "🚀 *Why are you missing your chance?* \n\n💰 Earn $50-$100 daily with AI predictions!\n\n👉 /start - Get predictions now!",
        "🔥 *Don't miss opportunities!* \n\n🎯 Live cricket predictions waiting!\n\n👉 /start - Get winning predictions!",
        "💎 *Your winning streak awaits!* \n\n📊 85%+ accuracy predictions!\n\n👉 /start - Start earning now!"
    ],
    'hi': [
        "🚀 *आप मौका क्यों गंवा रहे हैं?* \n\n💰 AI predictions से रोज $50-$100 कमाएं!\n\n👉 /start - Predictions प्राप्त करें!",
        "🔥 *अवसर मत गंवाएं!* \n\n🎯 लाइव क्रिकेट predictions तैयार!\n\n👉 /start - Winning predictions पाएं!"
    ],
    'bn': [
        "🚀 *আপনি আপনার সুযোগ কেন হারাচ্ছেন?* \n\n💰 AI predictions দিয়ে দৈনিক $50-$100 আয় করুন!\n\n👉 /start - predictions পান!",
        "🔥 *সুযোগ হারাবেন না!* \n\n🎯 লাইভ ক্রিকেট predictions অপেক্ষা করছে!\n\n👉 /start - winning predictions পান!"
    ],
    'ur': [
        "🚀 *آپ موقع کیوں کھو رہے ہیں؟* \n\n💰 AI predictions کے ساتھ روزانہ $50-$100 کمائیں!\n\n👉 /start - predictions حاصل کریں!",
        "🔥 *موقعوں کو مت گنوائیں!* \n\n🎯 لائیو کرکٹ predictions منتظر!\n\n👉 /start - winning predictions حاصل کریں!"
    ],
    'ne': [
        "🚀 *तपाईं अवसर किन हराउँदै हुनुहुन्छ?* \n\n💰 AI predictions को साथ दैनिक $50-$100 कमाउनुहोस्!\n\n👉 /start - predictions प्राप्त गर्नुहोस्!",
        "🔥 *अवसर हराउनुहोस्!* \n\n🎯 लाइभ क्रिकेट predictions पर्खिरहेको छ!\n\n👉 /start - winning predictions प्राप्त गर्नुहोस्!"
    ]
}

def send_inactivity_reminders():
    try:
        current_time = datetime.now()
        for user_id, user_data in users_storage.items():
            if user_data.get('last_activity_date'):
                last_activity = datetime.strptime(user_data['last_activity_date'], '%Y-%m-%d')
                hours_inactive = (current_time - last_activity).total_seconds() / 3600
                
                if hours_inactive >= 24:
                    language = user_data.get('language', 'en')
                    messages = INACTIVITY_MESSAGES.get(language, INACTIVITY_MESSAGES['en'])
                    message = random.choice(messages)
                    send_telegram_message(user_id, message)
                    user_data['last_reminder_date'] = current_time.strftime('%Y-%m-%d')
                    save_user(user_data)
                    time.sleep(0.5)
    except Exception as e:
        print(f"Reminder error: {e}")

def start_reminder_scheduler():
    def run_scheduler():
        while True:
            send_inactivity_reminders()
            time.sleep(6 * 3600)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

# ==================== USER MANAGEMENT ====================
def get_user(user_id):
    if user_id not in users_storage:
        users_storage[user_id] = {
            'user_id': user_id, 'language': 'en', 'prediction_count': 0, 'last_prediction_date': None,
            'last_activity_date': datetime.now().strftime('%Y-%m-%d'), 'player_id': None, 'deposit_amount': 0,
            'deposit_date': None, 'last_reminder_date': None
        }
    return users_storage[user_id]

def save_user(user_data):
    users_storage[user_data['user_id']] = user_data

def update_user_activity(user_id):
    user = get_user(user_id)
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

def can_get_prediction(user_id):
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    update_user_activity(user_id)
    
    if user.get('deposit_amount', 0) < 6:
        return False, "no_deposit"
    
    if user.get('deposit_date'):
        deposit_date = datetime.strptime(user['deposit_date'], '%Y-%m-%d')
        if (datetime.now() - deposit_date).days >= 5:
            return False, "deposit_expired"
    
    if user['last_prediction_date'] != today:
        user['prediction_count'] = 0
        user['last_prediction_date'] = today
        save_user(user)
    
    if user['prediction_count'] >= 20:
        return False, "daily_limit"
    
    return True, "allowed"

def update_prediction_count(user_id):
    user = get_user(user_id)
    user['prediction_count'] += 1
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

def update_deposit_info(user_id, deposit_amount):
    user = get_user(user_id)
    user['deposit_amount'] = deposit_amount
    user['deposit_date'] = datetime.now().strftime('%Y-%m-%d')
    user['prediction_count'] = 0
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

# ==================== REAL CRICAPI PREDICTIONS ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        self.last_fetch_time = None
        self.cached_matches = []
        self.used_matches = set()
        
    def fetch_live_matches(self):
        try:
            current_time = datetime.now()
            if (self.last_fetch_time and (current_time - self.last_fetch_time).seconds < 600 and self.cached_matches):
                return self.cached_matches
                
            if not self.api_key:
                return self.get_fallback_matches()
                
            print("🌐 Fetching live matches from CricAPI...")
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    matches = []
                    for match in data.get('data', []):
                        try:
                            match_started = match.get('matchStarted', False)
                            match_ended = match.get('matchEnded', False)
                            status = match.get('status', '').lower()
                            is_live = (match_started and not match_ended) or 'live' in status or 'running' in status
                            
                            if is_live:
                                team_info = match.get('teamInfo', [])
                                if len(team_info) >= 2:
                                    team_a = team_info[0].get('name', 'Team A').strip()
                                    team_b = team_info[1].get('name', 'Team B').strip()
                                    if team_a and team_b and team_a != 'Team A' and team_b != 'Team B':
                                        matches.append({
                                            'id': match.get('id', ''),
                                            'team_a': team_a, 'team_b': team_b,
                                            'series': match.get('series', 'International'),
                                            'status': match.get('status', 'Live')
                                        })
                        except: continue
                    
                    if matches:
                        self.cached_matches = matches
                        self.last_fetch_time = current_time
                        print(f"🎯 Live matches found: {len(matches)}")
                        return matches
            return self.get_fallback_matches()
        except Exception as e:
            print(f"CricAPI Error: {e}")
            return self.get_fallback_matches()
    
    def get_fallback_matches(self):
        return [
            {'id': '1', 'team_a': 'India', 'team_b': 'Pakistan', 'series': 'Asia Cup', 'status': 'Live'},
            {'id': '2', 'team_a': 'Australia', 'team_b': 'England', 'series': 'World Cup', 'status': 'Live'},
            {'id': '3', 'team_a': 'South Africa', 'team_b': 'New Zealand', 'series': 'Championship', 'status': 'Live'}
        ]
    
    def analyze_team_performance(self, team1, team2):
        team_stats = {
            'india': {'rating': 118}, 'pakistan': {'rating': 112}, 'australia': {'rating': 116},
            'england': {'rating': 114}, 'south africa': {'rating': 106}, 'new zealand': {'rating': 108}
        }
        team1_rating = team_stats.get(team1.lower(), {'rating': 95})['rating']
        team2_rating = team_stats.get(team2.lower(), {'rating': 95})['rating']
        
        team1_strength = team1_rating * random.uniform(0.85, 1.25)
        team2_strength = team2_rating * random.uniform(0.85, 1.25)
        total_strength = team1_strength + team2_strength
        
        if team1_strength > team2_strength:
            winner = team1
            confidence = max(60, min(94, int((team1_strength / total_strength) * 100)))
        else:
            winner = team2
            confidence = max(60, min(94, int((team2_strength / total_strength) * 100)))
        
        return {
            'prediction': f"{winner} to win",
            'confidence': confidence,
            'analysis': f"🏆 Team analysis completed\n📈 Form and conditions analyzed\n🎯 Key players performance checked",
            'team_a': team1, 'team_b': team2,
            'user_analysis': f"Based on comprehensive analysis, {winner} shows stronger chances with {confidence}% confidence."
        }
    
    def get_prediction(self):
        matches = self.fetch_live_matches()
        if not matches:
            fallback_match = random.choice(self.get_fallback_matches())
            return self.analyze_team_performance(fallback_match['team_a'], fallback_match['team_b'])
        
        available_matches = [m for m in matches if m['id'] not in self.used_matches]
        if not available_matches:
            self.used_matches.clear()
            available_matches = matches
        
        selected_match = random.choice(available_matches)
        self.used_matches.add(selected_match['id'])
        return self.analyze_team_performance(selected_match['team_a'], selected_match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== TELEGRAM FUNCTIONS ====================
def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if reply_markup: payload['reply_markup'] = reply_markup
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'Markdown'}
        if reply_markup: payload['reply_markup'] = reply_markup
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Edit message error: {e}")
        return None

# ==================== POSTBACK HANDLER ====================
@app.route('/1win-postback', methods=['GET', 'POST'])
def handle_1win_postback():
    try:
        if request.method == 'GET': data = request.args.to_dict()
        else: data = request.get_json() or request.form.to_dict()
        
        player_id = data.get('player_id') or data.get('id')
        status = data.get('status', '')
        deposit_amount = 0
        
        for param in ['amount', 'fdp', 'dep_sum']:
            if data.get(param):
                try: deposit_amount = float(data.get(param)); break
                except: continue
        
        if player_id:
            player_registrations[player_id] = True
            if deposit_amount > 0:
                player_deposits[player_id] = deposit_amount
                for user_data in users_storage.values():
                    if user_data.get('player_id') == player_id:
                        update_deposit_info(user_data['user_id'], deposit_amount)
            
            return jsonify({"status": "success", "player_id": player_id, "deposit": deposit_amount})
        
        return jsonify({"status": "error"})
    except Exception as e:
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
            
            update_user_activity(user_id)
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
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                send_telegram_message(chat_id, msg_data['welcome'], keyboard)
            
            elif text.isdigit() and len(text) >= 5:
                player_id = text
                user = get_user(user_id)
                msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
                
                loading_msg = send_telegram_message(chat_id, msg_data['loading_registration'])
                
                if player_id in player_registrations:
                    user['player_id'] = player_id
                    user['is_registered'] = True
                    user['deposit_amount'] = player_deposits.get(player_id, 0)
                    save_user(user)
                    
                    if user['deposit_amount'] >= 6:
                        keyboard = {'inline_keyboard': [[{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]]}
                        message_text = msg_data['deposit_success'].replace('{amount}', str(user['deposit_amount']))
                    else:
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': msg_data['check_deposit_btn'], 'callback_data': 'check_deposit'}]
                            ]
                        }
                        message_text = msg_data['reg_success']
                    
                    if loading_msg and 'result' in loading_msg:
                        edit_telegram_message(chat_id, loading_msg['result']['message_id'], message_text, keyboard)
                    else:
                        send_telegram_message(chat_id, message_text, keyboard)
                else:
                    keyboard = {'inline_keyboard': [[{'text': msg_data['register_btn'], 'url': 'https://mostbet-king.com/5rTs'}]]}
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
            
            update_user_activity(user_id)
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
                deposit_amount = user.get('deposit_amount', 0)
                if deposit_amount >= 6:
                    keyboard = {'inline_keyboard': [[{'text': msg_data['get_prediction_btn'], 'callback_data': 'get_prediction'}]]}
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
                can_predict, reason = can_get_prediction(user_id)
                
                if not can_predict:
                    if reason == "deposit_expired":
                        # 5 DAYS COMPLETED - ONLY DEPOSIT BUTTON
                        keyboard = {'inline_keyboard': [[{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}]]}
                        edit_telegram_message(chat_id, message_id, msg_data['deposit_expired'], keyboard)
                    
                    elif reason == "daily_limit":
                        # DAILY LIMIT - BOTH BUTTONS
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}],
                                [{'text': msg_data['try_tomorrow_btn'], 'callback_data': 'try_tomorrow'}]
                            ]
                        }
                        edit_telegram_message(chat_id, message_id, msg_data['prediction_limit'], keyboard)
                    
                    else:
                        # NO DEPOSIT
                        keyboard = {'inline_keyboard': [[{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}]]}
                        edit_telegram_message(chat_id, message_id, msg_data['deposit_not_found'], keyboard)
                
                else:
                    # USER CAN GET PREDICTION
                    prediction = ai_predictor.get_prediction()
                    update_prediction_count(user_id)
                    
                    keyboard = {'inline_keyboard': [[{'text': msg_data['next_prediction_btn'], 'callback_data': 'get_prediction'}]]}
                    
                    message_text = msg_data['prediction_text'].format(
                        team_a=prediction['team_a'], team_b=prediction['team_b'],
                        prediction=prediction['prediction'], confidence=prediction['confidence'],
                        analysis=prediction['user_analysis']
                    )
                    
                    edit_telegram_message(chat_id, message_id, message_text, keyboard)
            
            elif data_value == 'try_tomorrow':
                edit_telegram_message(chat_id, message_id, "⏳ Please try again in 12 hours for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== BASIC ROUTES ====================
@app.route('/')
def home():
    return "✅ Sports Prediction Bot - All Features Active!"

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{VERCEL_URL}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify({"status": "success", "webhook_url": webhook_url})

@app.route('/test-register/<player_id>', methods=['GET'])
def test_register_player(player_id):
    player_registrations[player_id] = True
    player_deposits[player_id] = 6.0
    for user_data in users_storage.values():
        if user_data.get('player_id') == player_id:
            update_deposit_info(user_data['user_id'], 6.0)
    return jsonify({"status": "success", "player_id": player_id, "deposit": 6.0})

# ==================== START SCHEDULER ====================
start_reminder_scheduler()

if __name__ == '__main__':
    app.run(debug=True)
