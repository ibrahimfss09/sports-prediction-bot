from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime, timedelta
import time
import json
import threading

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

# ==================== COMPLETE MULTI-LANGUAGE INACTIVITY MESSAGES ====================
INACTIVITY_MESSAGES = {
    'en': [
        "🚀 *Why are you missing your chance?* \n\n💰 You could be earning $50-$100 daily with our AI predictions!\n\n👉 Click /start to get predictions now!",
        "🔥 *Don't let opportunities slip away!* \n\n🎯 Live cricket predictions are waiting for you!\n\n👉 /start - Get your winning predictions!",
        "💎 *Your winning streak is waiting!* \n\n📊 AI-powered cricket predictions with 85%+ accuracy!\n\n👉 /start - Start earning now!",
        "⚡ *Time is money, don't waste it!* \n\n🏏 Live matches are happening with great odds!\n\n👉 /start - Get instant predictions!",
        "🎯 *Perfect predictions are ready!* \n\n💰 Your path to daily earnings starts here!\n\n👉 /start - Don't miss out!",
        "🚨 *Alert: High-confidence predictions available!* \n\n🔥 Today's matches have great winning potential!\n\n👉 /start - Claim your predictions!",
        "💵 *Money-making opportunity waiting!* \n\n🏆 Professional AI predictions for today's matches!\n\n👉 /start - Start earning now!",
        "🌟 *Your success story starts today!* \n\n📈 Join thousands winning with our predictions!\n\n👉 /start - Begin your journey!"
    ],
    'hi': [
        "🚀 *आप अपना मौका क्यों गंवा रहे हैं?* \n\n💰 आप हमारे AI predictions के साथ रोज $50-$100 कमा सकते हैं!\n\n👉 Predictions पाने के लिए /start क्लिक करें!",
        "🔥 *अवसरों को हाथ से न जाने दें!* \n\n🎯 आपके लिए लाइव क्रिकेट predictions तैयार हैं!\n\n👉 /start - अपनी winning predictions प्राप्त करें!",
        "💎 *आपकी winning streak आपका इंतज़ार कर रही है!* \n\n📊 85%+ accuracy के साथ AI-powered cricket predictions!\n\n👉 /start - अब कमाई शुरू करें!",
        "⚡ *समय पैसा है, इसे बर्बाद न करें!* \n\n🏏 लाइव मैच्स बेहतरीन odds के साथ चल रहे हैं!\n\n👉 /start - तुरंत predictions प्राप्त करें!",
        "🎯 *बिल्कुल सही predictions तैयार हैं!* \n\n💰 आपकी दैनिक कमाई का रास्ता यहाँ से शुरू होता है!\n\n👉 /start - मौका न चूकें!",
        "🚨 *अलर्ट: High-confidence predictions उपलब्ध!* \n\n🔥 आज के मैचों में great winning potential है!\n\n👉 /start - अपनी predictions प्राप्त करें!",
        "💵 *पैसा कमाने का अवसर इंतज़ार कर रहा है!* \n\n🏆 आज के मैचों के लिए professional AI predictions!\n\n👉 /start - अब कमाई शुरू करें!",
        "🌟 *आपकी सफलता की कहानी आज से शुरू होती है!* \n\n📈 हजारों लोगों के साथ जुड़ें जो हमारे predictions से जीत रहे हैं!\n\n👉 /start - अपनी यात्रा शुरू करें!"
    ],
    'bn': [
        "🚀 *আপনি আপনার সুযোগ কেন হারাচ্ছেন?* \n\n💰 আপনি আমাদের AI predictions দিয়ে দৈনিক $50-$100 আয় করতে পারেন!\n\n👉 predictions পেতে /start ক্লিক করুন!",
        "🔥 *সুযোগ হাতছাড়া করবেন না!* \n\n🎯 আপনার জন্য লাইভ ক্রিকেট predictions অপেক্ষা করছে!\n\n👉 /start - আপনার winning predictions পান!",
        "💎 *আপনার winning streak আপনার জন্য অপেক্ষা করছে!* \n\n📊 85%+ accuracy সহ AI-powered cricket predictions!\n\n👉 /start - এখনই আয় শুরু করুন!",
        "⚡ *সময়就是 টাকা, এটি নষ্ট করবেন না!* \n\n🏏 লাইভ ম্যাচগুলি দুর্দান্ত odds নিয়ে চলছে!\n\n👉 /start - তাত্ক্ষণিক predictions পান!",
        "🎯 *নিখুঁত predictions প্রস্তুত!* \n\n💰 আপনার দৈনিক আয়ের পথ এখান থেকে শুরু হয়!\n\n👉 /start - সুযোগ হারাবেন না!",
        "🚨 *সতর্কতা: উচ্চ-আত্মবিশ্বাসের predictions উপলব্ধ!* \n\n🔥 আজকের ম্যাচগুলিতে দুর্দান্ত জয়ের সম্ভাবনা রয়েছে!\n\n👉 /start - আপনার predictions দাবি করুন!",
        "💵 *টাকা উপার্জনের সুযোগ অপেক্ষা করছে!* \n\n🏆 আজকের ম্যাচগুলির জন্য পেশাদার AI predictions!\n\n👉 /start - এখনই আয় শুরু করুন!",
        "🌟 *আপনার সাফল্যের গল্প আজ শুরু হয়!* \n\n📈 হাজারো মানুষের সাথে যোগ দিন যারা আমাদের predictions দিয়ে জিতছে!\n\n👉 /start - আপনার যাত্রা শুরু করুন!"
    ],
    'ur': [
        "🚀 *آپ اپنا موقع کیوں کھو رہے ہیں؟* \n\n💰 آپ ہمارے AI predictions کے ساتھ روزانہ $50-$100 کما سکتے ہیں!\n\n👉 predictions حاصل کرنے کے لیے /start کلک کریں!",
        "🔥 *موقعوں کو ہاتھ سے نہ جانے دیں!* \n\n🎯 آپ کے لیے لائیو کرکٹ predictions منتظر ہیں!\n\n👉 /start - اپنی winning predictions حاصل کریں!",
        "💎 *آپ کی winning streak آپ کا انتظار کر رہی ہے!* \n\n📊 85%+ accuracy کے ساتھ AI-powered cricket predictions!\n\n👉 /start - اب کمائی شروع کریں!",
        "⚡ *وقت پیسہ ہے، اسے ضائع نہ کریں!* \n\n🏏 لائیو میچز بہترین odds کے ساتھ چل رہے ہیں!\n\n👉 /start - فوری predictions حاصل کریں!",
        "🎯 *بالکل صحیح predictions تیار ہیں!* \n\n💰 آپ کی روزانہ کمائی کا راستہ یہاں سے شروع ہوتا ہے!\n\n👉 /start - موقع نہ چھوڑیں!",
        "🚨 *الرٹ: اعلی اعتماد predictions دستیاب!* \n\n🔥 آج کے میچوں میں بہترین جیتنے کی صلاحیت ہے!\n\n👉 /start - اپنی predictions حاصل کریں!",
        "💵 *پیسہ کمانے کا موقع انتظار کر رہا ہے!* \n\n🏆 آج کے میچوں کے لیے پیشہ ورانہ AI predictions!\n\n👉 /start - اب کمائی شروع کریں!",
        "🌟 *آپ کی کامیابی کی کہانی آج سے شروع ہوتی ہے!* \n\n📈 ہزاروں لوگوں کے ساتھ شامل ہوں جو ہمارے predictions سے جیت رہے ہیں!\n\n👉 /start - اپنا سفر شروع کریں!"
    ],
    'ne': [
        "🚀 *तपाईं आफ्नो अवसर किन हराउँदै हुनुहुन्छ?* \n\n💰 तपाईं हाम्रो AI predictions को साथ दैनिक $50-$100 कमाउन सक्नुहुन्छ!\n\n👉 predictions प्राप्त गर्न /start क्लिक गर्नुहोस्!",
        "🔥 *अवसरहरू हात नबाट जान दिनुहोस्!* \n\n🎯 तपाईंको लागि लाइभ क्रिकेट predictions पर्खिरहेका छन्!\n\n👉 /start - आफ्नो winning predictions प्राप्त गर्नुहोस्!",
        "💎 *तपाईंको winning streak ले तपाईंको पर्खाइ गर्दैछ!* \n\n📊 85%+ accuracy सहित AI-powered cricket predictions!\n\n👉 /start - अब कमाउनी सुरु गर्नुहोस्!",
        "⚡ *समय पैसा हो, यसलाई बर्बाद नगर्नुहोस्!* \n\n🏏 लाइभ म्याचहरू राम्रो odds सहित चलिरहेका छन्!\n\n👉 /start - तत्काल predictions प्राप्त गर्नुहोस्!",
        "🎯 *उत्तम predictions तयार छन्!* \n\n💰 तपाईंको दैनिक आम्दानीको बाटो यहाँबाट सुरु हुन्छ!\n\n👉 /start - अवसर नगुमाउनुहोस्!",
        "🚨 *अलर्ट: उच्च-विश्वास predictions उपलब्ध!* \n\n🔥 आजका म्याचहरूमा राम्रो जित्ने सम्भावना छ!\n\n👉 /start - आफ्ना predictions दावी गर्नुहोस्!",
        "💵 *पैसा कमाउने अवसर पर्खिरहेको छ!* \n\n🏆 आजका म्याचहरूका लागि पेशेवर AI predictions!\n\n👉 /start - अब कमाउनी सुरु गर्नुहोस्!",
        "🌟 *तपाईंको सफलताको कथा आजबाट सुरु हुन्छ!* \n\n📈 हजारौं मानिसहरूसँग सामेल हुनुहोस् जो हाम्रो predictions सँग जितिरहेका छन्!\n\n👉 /start - आफ्नो यात्रा सुरु गर्नुहोस्!"
    ]
}

# ==================== SCHEDULED REMINDER SYSTEM ====================
def send_inactivity_reminders():
    """Send reminders to inactive users every 24 hours in their selected language"""
    try:
        print("🔔 Checking for inactive users...")
        current_time = datetime.now()
        inactive_users = []
        
        for user_id, user_data in users_storage.items():
            if user_data.get('last_activity_date'):
                last_activity = datetime.strptime(user_data['last_activity_date'], '%Y-%m-%d')
                hours_since_activity = (current_time - last_activity).total_seconds() / 3600
                
                # Send reminder if inactive for 24-48 hours (to avoid spamming)
                if 24 <= hours_since_activity <= 48:
                    # Check if we already sent reminder today
                    last_reminder = user_data.get('last_reminder_date')
                    if last_reminder != current_time.strftime('%Y-%m-%d'):
                        inactive_users.append(user_data)
        
        print(f"📨 Sending reminders to {len(inactive_users)} inactive users")
        
        for user in inactive_users:
            try:
                language = user.get('language', 'en')
                messages = INACTIVITY_MESSAGES.get(language, INACTIVITY_MESSAGES['en'])
                message = random.choice(messages)
                
                send_telegram_message(user['user_id'], message)
                print(f"✅ Sent {language} reminder to user {user['user_id']}")
                
                # Update last reminder time to avoid duplicate sends
                user['last_reminder_date'] = current_time.strftime('%Y-%m-%d')
                save_user(user)
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Failed to send reminder to user {user['user_id']}: {e}")
                
    except Exception as e:
        print(f"❌ Error in reminder system: {e}")

def start_reminder_scheduler():
    """Start the background scheduler for reminders"""
    def run_scheduler():
        while True:
            try:
                send_inactivity_reminders()
                # Run every 6 hours to catch users at different times
                time.sleep(6 * 3600)  # 6 hours
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(3600)  # Wait 1 hour on error
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("✅ Inactivity reminder scheduler started")

# ==================== ENHANCED USER MANAGEMENT ====================
def get_user(user_id):
    if user_id not in users_storage:
        users_storage[user_id] = {
            'user_id': user_id,
            'language': 'en',
            'prediction_count': 0,
            'last_prediction_date': None,
            'last_activity_date': datetime.now().strftime('%Y-%m-%d'),
            'player_id': None,
            'deposit_amount': 0,
            'is_registered': False,
            'registration_date': None,
            'deposit_date': None,
            'deposit_used_days': 0,
            'total_predictions_used': 0,
            'last_reminder_date': None
        }
    return users_storage[user_id]

def save_user(user_data):
    users_storage[user_data['user_id']] = user_data

def update_user_activity(user_id):
    """Update user's last activity timestamp"""
    user = get_user(user_id)
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

def can_get_prediction(user_id):
    """Check if user can get prediction with 5-day limit"""
    user = get_user(user_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Update activity
    update_user_activity(user_id)
    
    # Check if user has deposited at least $6
    if user.get('deposit_amount', 0) < 6:
        return False, "no_deposit"
    
    # Check if deposit is still valid (5 days limit)
    if user.get('deposit_date'):
        deposit_date = datetime.strptime(user['deposit_date'], '%Y-%m-%d')
        days_since_deposit = (datetime.now() - deposit_date).days
        if days_since_deposit >= 5:
            return False, "deposit_expired"
    
    # Reset daily count if new day
    if user['last_prediction_date'] != today:
        user['prediction_count'] = 0
        user['last_prediction_date'] = today
        save_user(user)
    
    # Check daily limit
    if user['prediction_count'] >= 20:
        return False, "daily_limit"
    
    return True, "allowed"

def update_prediction_count(user_id):
    user = get_user(user_id)
    user['prediction_count'] += 1
    user['total_predictions_used'] = user.get('total_predictions_used', 0) + 1
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

def update_deposit_info(user_id, deposit_amount):
    """Update user deposit information"""
    user = get_user(user_id)
    user['deposit_amount'] = deposit_amount
    user['deposit_date'] = datetime.now().strftime('%Y-%m-%d')
    user['deposit_used_days'] = 0
    user['prediction_count'] = 0
    user['last_prediction_date'] = datetime.now().strftime('%Y-%m-%d')
    user['last_activity_date'] = datetime.now().strftime('%Y-%m-%d')
    save_user(user)

# ==================== ENHANCED AI PREDICTION WITH CRICAPI ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        self.last_fetch_time = None
        self.cached_matches = []
        self.used_matches = set()
        
    def fetch_live_matches(self):
        try:
            # Cache matches for 10 minutes
            current_time = datetime.now()
            if (self.last_fetch_time and 
                (current_time - self.last_fetch_time).seconds < 600 and 
                self.cached_matches):
                return self.cached_matches
                
            if not self.api_key:
                return self.get_fallback_matches()
                
            print("🌐 Fetching live matches from CricAPI...")
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 API Response Status: {data.get('status')}")
                
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
                                        match_data = {
                                            'id': match.get('id', ''),
                                            'team_a': team_a,
                                            'team_b': team_b,
                                            'date': match.get('date', ''),
                                            'series': match.get('series', 'International'),
                                            'status': match.get('status', 'Live'),
                                            'venue': match.get('venue', 'Unknown')
                                        }
                                        matches.append(match_data)
                                        print(f"✅ Found live match: {team_a} vs {team_b}")
                        except Exception as e:
                            continue
                    
                    if matches:
                        self.cached_matches = matches
                        self.last_fetch_time = current_time
                        print(f"🎯 Total live matches found: {len(matches)}")
                        return matches
                    else:
                        print("❌ No live matches found, using fallback")
                        return self.get_fallback_matches()
                else:
                    return self.get_fallback_matches()
            else:
                return self.get_fallback_matches()
                
        except Exception as e:
            print(f"❌ CricAPI Error: {e}")
            return self.get_fallback_matches()
    
    def get_fallback_matches(self):
        today = datetime.now()
        fallback_matches = [
            {'id': '1', 'team_a': 'India', 'team_b': 'Pakistan', 'series': 'Asia Cup', 'status': 'Live'},
            {'id': '2', 'team_a': 'Australia', 'team_b': 'England', 'series': 'World Cup', 'status': 'Live'},
            {'id': '3', 'team_a': 'South Africa', 'team_b': 'New Zealand', 'series': 'Championship', 'status': 'Live'},
            {'id': '4', 'team_a': 'West Indies', 'team_b': 'Sri Lanka', 'series': 'Caribbean Cup', 'status': 'Live'}
        ]
        return fallback_matches
    
    def analyze_team_performance(self, team1, team2):
        team_stats = {
            'india': {'rating': 118, 'key_players': ['Kohli', 'Sharma', 'Bumrah']},
            'pakistan': {'rating': 112, 'key_players': ['Babar', 'Rizwan', 'Afridi']},
            'australia': {'rating': 116, 'key_players': ['Smith', 'Warner', 'Cummins']},
            'england': {'rating': 114, 'key_players': ['Root', 'Buttler', 'Stokes']},
            'south africa': {'rating': 106, 'key_players': ['Markram', 'Rabada', 'Miller']},
            'new zealand': {'rating': 108, 'key_players': ['Williamson', 'Boult', 'Conway']},
            'west indies': {'rating': 92, 'key_players': ['Hope', 'Joseph', 'Holder']},
            'sri lanka': {'rating': 90, 'key_players': ['Mendis', 'Theekshana', 'Shanaka']}
        }
        
        team1_data = team_stats.get(team1.lower(), {'rating': 95, 'key_players': ['Key Players']})
        team2_data = team_stats.get(team2.lower(), {'rating': 95, 'key_players': ['Key Players']})
        
        team1_rating = team1_data['rating']
        team2_rating = team2_data['rating']
        
        team1_form = random.uniform(0.85, 1.25)
        team2_form = random.uniform(0.85, 1.25)
        
        team1_strength = team1_rating * team1_form
        team2_strength = team2_rating * team2_form
        
        total_strength = team1_strength + team2_strength
        team1_probability = team1_strength / total_strength
        
        if team1_probability > 0.5:
            winner = team1
            confidence = max(60, min(94, int(team1_probability * 100)))
        else:
            winner = team2
            confidence = max(60, min(94, int((1 - team1_probability) * 100)))
        
        analysis_points = [
            f"🏆 **Team Ratings**: {team1} ({team1_rating}) vs {team2} ({team2_rating})",
            f"📈 **Current Form**: {team1} ({team1_form:.1f}x) vs {team2} ({team2_form:.1f}x)",
            f"🎯 **Key Players**: {', '.join(team1_data['key_players'][:2])} vs {', '.join(team2_data['key_players'][:2])}",
            f"🏟️ **Match Conditions**: Pitch favors {random.choice(['batting', 'bowling'])}",
            f"🌦️ **Weather**: {random.choice(['Clear', 'Humid', 'Good for cricket'])}"
        ]
        
        random.shuffle(analysis_points)
        selected_analysis = analysis_points[:3]
        
        prediction_types = [
            f"{winner} to win",
            f"{winner} victory predicted", 
            f"{winner} expected to dominate",
            f"Strong chances for {winner}"
        ]
        
        return {
            'prediction': random.choice(prediction_types),
            'confidence': confidence,
            'analysis': "\n".join(selected_analysis),
            'team_a': team1,
            'team_b': team2,
            'user_analysis': f"Based on comprehensive analysis of team ratings and current form, {winner} shows stronger chances with {confidence}% confidence."
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
        
        print(f"🎯 Selected match: {selected_match['team_a']} vs {selected_match['team_b']}")
        return self.analyze_team_performance(selected_match['team_a'], selected_match['team_b'])

ai_predictor = CricketAIPredictor()

# ==================== LANGUAGE MESSAGES (Updated for 5-day limit) ====================
LANGUAGE_MESSAGES = {
    'en': {
        # ... existing messages ...
        'deposit_success': "🎊 *Deposit Verified Successfully!*\n\n💰 *Deposit Amount:* ${amount}\n✅ *Status:* Verified\n\n🎯 You now have access to AI-powered predictions!\n\n💰 *Validity:* 5 days (20 predictions daily)\n\nClick below to get your first prediction:",
        'deposit_expired': "⏰ *Deposit Validity Expired!*\n\nYour 5-day prediction access has ended.\n\n💎 Make a new deposit to continue predictions!\n\n💰 Deposit now to restart your prediction access!",
        'prediction_limit': "🚫 *Prediction Limit Reached*\n\nYou've used all 20 predictions for today.\n\n💡 *Options:*\n• Wait until tomorrow (12 hours)\n• Make another deposit for immediate access\n\n💰 Continue with a new deposit!",
        # ... other messages same as before ...
    },
    'hi': {
        'deposit_success': "🎊 *जमा सफलतापूर्वक सत्यापित!*\n\n💰 *जमा राशि:* ${amount}\n✅ *स्थिति:* सत्यापित\n\n🎯 अब आपके पास AI-पावर्ड भविष्यवाणियों तक पहुंच है!\n\n💰 *वैधता:* 5 दिन (रोज 20 भविष्यवाणियाँ)\n\nअपनी पहली भविष्यवाणी प्राप्त करने के लिए नीचे क्लिक करें:",
        'deposit_expired': "⏰ *जमा वैधता समाप्त!*\n\nआपकी 5-दिन की भविष्यवाणी पहुंच समाप्त हो गई है।\n\n💎 नया जमा करके भविष्यवाणियाँ जारी रखें!\n\n💰 अब जमा करके अपनी भविष्यवाणी पहुंच पुनः प्रारंभ करें!",
        'prediction_limit': "🚫 *भविष्यवाणी सीमा पूर्ण*\n\nआपने आज की सभी 20 भविष्यवाणियों का उपयोग कर लिया है।\n\n💡 *विकल्प:*\n• कल तक प्रतीक्षा करें (12 घंटे)\n• तुरंत पहुंच के लिए दूसरा जमा करें\n\n💰 नए जमा के साथ जारी रखें!",
        # ... other languages similarly updated ...
    }
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

# ==================== WEBHOOK HANDLER WITH 5-DAY LIMIT ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_id = message['from']['id']
            
            # Update user activity for ANY message
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
                update_user_activity(user_id)
                # ... player ID handling code ...
        
        elif 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            data_value = callback['data']
            user_id = callback['from']['id']
            
            update_user_activity(user_id)
            user = get_user(user_id)
            msg_data = LANGUAGE_MESSAGES.get(user['language'], LANGUAGE_MESSAGES['en'])
            
            if data_value == 'get_prediction':
                can_predict, reason = can_get_prediction(user_id)
                
                if not can_predict:
                    if reason == "deposit_expired":
                        # 5 DAYS COMPLETED - ONLY DEPOSIT BUTTON
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_again_btn'], 'url': 'https://mostbet-king.com/5rTs'}]
                            ]
                        }
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
                        keyboard = {
                            'inline_keyboard': [
                                [{'text': msg_data['deposit_btn'], 'url': 'https://mostbet-king.com/5rTs'}]
                            ]
                        }
                        edit_telegram_message(chat_id, message_id, msg_data['deposit_not_found'], keyboard)
                
                else:
                    # USER CAN GET PREDICTION
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
                edit_telegram_message(chat_id, message_id, "⏳ Please try again in 12 hours for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== START SCHEDULER ====================
start_reminder_scheduler()

# Rest of your routes remain the same...
@app.route('/')
def home():
    return "✅ Sports Prediction Bot - 5 Day Limit & 24h Reminders Active!"

if __name__ == '__main__':
    app.run(debug=True)
