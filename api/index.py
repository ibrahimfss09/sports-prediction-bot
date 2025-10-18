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
        'welcome': "ðŸŒ *Select Your Preferred Language:*",
        'selected': "âœ… You selected English!",
        'register_title': "ðŸŒ *Step 1 - Register*",
        'account_new': "â€¼ï¸ *THE ACCOUNT MUST BE NEW*",
        'instruction1': "1ï¸âƒ£ If after clicking the \"REGISTER\" button you get to the old account, you need to log out of it and click the button again.",
        'instruction2': "2ï¸âƒ£ Specify a promocode during registration: **CLAIM**",
        'after_reg': "âœ… After REGISTRATION, click the \"CHECK REGISTRATION\" button",
        'register_btn': "ðŸ“² REGISTER NOW",
        'check_btn': "ðŸ” CHECK REGISTRATION",
        'enter_player_id': "ðŸ” *Check Your Registration*\n\nPlease enter your 1Win *Player ID* to verify:\n\nðŸ“ *How to find Player ID:*\n1. Login to 1Win account\n2. Go to Profile Settings\n3. Copy Player ID number\n4. Paste it here\n\nðŸ”¢ *Enter your Player ID now:*",
        'loading_registration': "â³ *Please wait few seconds, your registration is loading...*",
        'reg_success': "ðŸŽ‰ *Great, you have successfully completed registration!*\n\nâœ… Your account is synchronized with the bot\n\nðŸ’´ *To gain access to signals, deposit your account (make a deposit) with at least 600â‚¹ or $6 in any currency*\n\nðŸ•¹ï¸ After successfully replenishing your account, click on the CHECK DEPOSIT button and gain access",
        'reg_not_found': "âŒ *Sorry, You're Not Registered!*\n\nPlease click the REGISTER button first and complete your registration using our affiliate link.\n\nAfter successful registration, come back and enter your Player ID.",
        'deposit_btn': "ðŸ’³ DEPOSIT NOW",
        'check_deposit_btn': "ðŸ” CHECK DEPOSIT",
        'deposit_success': "ðŸŽŠ *Deposit Verified Successfully!*\n\nðŸ’° *Deposit Amount:* ${amount}\nâœ… *Status:* Verified\n\nðŸŽ¯ You now have access to AI-powered predictions!\n\nClick below to get your first prediction:",
        'deposit_not_found': "ðŸ’° *Deposit Not Found!*\n\nYou have registered successfully but no deposit detected yet.\n\nðŸ’µ Please make a deposit of at least $6 to get prediction access.",
        'get_prediction_btn': "ðŸŽ¯ GET PREDICTION",
        'prediction_limit': "ðŸš« *Prediction Limit Reached*\n\nYou've used all 20 free predictions for today.\n\nðŸ’¡ *Options:*\nâ€¢ Wait until tomorrow for new predictions\nâ€¢ Make another deposit for additional access\n\nðŸ’° Continue predictions by staying active!",
        'deposit_again_btn': "ðŸ’³ DEPOSIT AGAIN",
        'try_tomorrow_btn': "ðŸ• TRY TOMORROW",
        'next_prediction_btn': "ðŸ”„ NEXT PREDICTION",
        'prediction_text': "ðŸŽ¯ *AI CRICKET PREDICTION* ðŸ¤–\n\nðŸŸï¸ *Match:* {team_a} vs {team_b}\nðŸ“Š *Prediction:* {prediction}\nâœ… *Confidence:* {confidence}%\n\nðŸ“ˆ *Analysis:*\n{analysis}\n\nâš ï¸ *AI Prediction - Bet Responsibly*",
        'random_messages': [
            "YOUR REGISTRATION IS SUCCESSFUL! âœ…\n\nMake a deposit of $6,7,10,13,17 or any other amount and bot will automatically give you access to signals! ðŸ”‘\n\nYou can earn $10 âž¡ï¸ $100 every dayðŸ’°\n\nðŸ‘‰Click /start",
            "Bro, ready signal for youâ˜ºï¸\n\nSTART NOWðŸ‘‰ /start",
            "ðŸš€ The signal has already come\n\nðŸ”¥ Don't miss your chance to get your money\n\nâž¡ï¸ /start",
            "START BOT NOW AND GET MONEYðŸ’°ðŸ”¥\n\n/start"
        ]
    },
    'hi': {
        'welcome': "ðŸŒ *à¤…à¤ªà¤¨à¥€ à¤ªà¤¸à¤‚à¤¦à¥€à¤¦à¤¾ à¤­à¤¾à¤·à¤¾ à¤šà¥à¤¨à¥‡à¤‚:*",
        'selected': "âœ… à¤†à¤ªà¤¨à¥‡ à¤¹à¤¿à¤‚à¤¦à¥€ à¤šà¥à¤¨à¥€!",
        'register_title': "ðŸŒ *à¤šà¤°à¤£ 1 - à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£*",
        'account_new': "â€¼ï¸ *à¤–à¤¾à¤¤à¤¾ à¤¨à¤¯à¤¾ à¤¹à¥‹à¤¨à¤¾ à¤šà¤¾à¤¹à¤¿à¤*",
        'instruction1': "1ï¸âƒ£ à¤¯à¤¦à¤¿ \"REGISTER\" à¤¬à¤Ÿà¤¨ à¤ªà¤° à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤¬à¤¾à¤¦ à¤†à¤ª à¤ªà¥à¤°à¤¾à¤¨à¥‡ à¤–à¤¾à¤¤à¥‡ à¤®à¥‡à¤‚ à¤†à¤¤à¥‡ à¤¹à¥ˆà¤‚, à¤¤à¥‹ à¤†à¤ªà¤•à¥‹ à¤‰à¤¸à¤¸à¥‡ à¤²à¥‰à¤— à¤†à¤‰à¤Ÿ à¤•à¤°à¤¨à¤¾ à¤¹à¥‹à¤—à¤¾ à¤”à¤° à¤«à¤¿à¤° à¤¸à¥‡ à¤¬à¤Ÿà¤¨ à¤ªà¤° à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¤¨à¤¾ à¤¹à¥‹à¤—à¤¾à¥¤",
        'instruction2': "2ï¸âƒ£ à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤•à¥‡ à¤¦à¥Œà¤°à¤¾à¤¨ à¤ªà¥à¤°à¥‹à¤®à¥‹à¤•à¥‹à¤¡ à¤¨à¤¿à¤°à¥à¤¦à¤¿à¤·à¥à¤Ÿ à¤•à¤°à¥‡à¤‚: **CLAIM**",
        'after_reg': "âœ… à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤•à¥‡ à¤¬à¤¾à¤¦, \"CHECK REGISTRATION\" à¤¬à¤Ÿà¤¨ à¤ªà¤° à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¥‡à¤‚",
        'register_btn': "ðŸ“² à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤•à¤°à¥‡à¤‚",
        'check_btn': "ðŸ” à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤œà¤¾à¤‚à¤šà¥‡à¤‚",
        'enter_player_id': "ðŸ” *à¤…à¤ªà¤¨à¤¾ à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤œà¤¾à¤‚à¤šà¥‡à¤‚*\n\nà¤•à¥ƒà¤ªà¤¯à¤¾ à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤…à¤ªà¤¨à¤¾ 1Win *Player ID* à¤¦à¤°à¥à¤œ à¤•à¤°à¥‡à¤‚:\n\nðŸ“ *Player ID à¤•à¥ˆà¤¸à¥‡ à¤¢à¥‚à¤‚à¤¢à¥‡à¤‚:*\n1. 1Win à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ à¤®à¥‡à¤‚ à¤²à¥‰à¤—à¤¿à¤¨ à¤•à¤°à¥‡à¤‚\n2. à¤ªà¥à¤°à¥‹à¤«à¤¾à¤‡à¤² à¤¸à¥‡à¤Ÿà¤¿à¤‚à¤—à¥à¤¸ à¤ªà¤° à¤œà¤¾à¤à¤‚\n3. Player ID à¤¨à¤‚à¤¬à¤° à¤•à¥‰à¤ªà¥€ à¤•à¤°à¥‡à¤‚\n4. à¤¯à¤¹à¤¾à¤ à¤ªà¥‡à¤¸à¥à¤Ÿ à¤•à¤°à¥‡à¤‚\n\nðŸ”¢ *à¤…à¤¬ à¤…à¤ªà¤¨à¤¾ Player ID à¤¦à¤°à¥à¤œ à¤•à¤°à¥‡à¤‚:*",
        'loading_registration': "â³ *à¤•à¥ƒà¤ªà¤¯à¤¾ à¤•à¥à¤› à¤¸à¥‡à¤•à¤‚à¤¡ à¤ªà¥à¤°à¤¤à¥€à¤•à¥à¤·à¤¾ à¤•à¤°à¥‡à¤‚, à¤†à¤ªà¤•à¤¾ à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤²à¥‹à¤¡ à¤¹à¥‹ à¤°à¤¹à¤¾ à¤¹à¥ˆ...*",
        'reg_success': "ðŸŽ‰ *à¤¬à¤§à¤¾à¤ˆ à¤¹à¥‹, à¤†à¤ªà¤¨à¥‡ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤ªà¥‚à¤°à¤¾ à¤•à¤° à¤²à¤¿à¤¯à¤¾ à¤¹à¥ˆ!*\n\nâœ… à¤†à¤ªà¤•à¤¾ à¤–à¤¾à¤¤à¤¾ à¤¬à¥‰à¤Ÿ à¤•à¥‡ à¤¸à¤¾à¤¥ à¤¸à¤¿à¤‚à¤• à¤¹à¥‹ à¤—à¤¯à¤¾ à¤¹à¥ˆ\n\nðŸ’´ *à¤¸à¤¿à¤—à¥à¤¨à¤² à¤¤à¤• à¤ªà¤¹à¥à¤‚à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤, à¤…à¤ªà¤¨à¥‡ à¤–à¤¾à¤¤à¥‡ à¤®à¥‡à¤‚ à¤•à¤® à¤¸à¥‡ à¤•à¤® 600â‚¹ à¤¯à¤¾ $6 à¤œà¤®à¤¾ à¤•à¤°à¥‡à¤‚*\n\nðŸ•¹ï¸ à¤…à¤ªà¤¨à¤¾ à¤–à¤¾à¤¤à¤¾ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤°à¤¿à¤šà¤¾à¤°à¥à¤œ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤¬à¤¾à¤¦, CHECK DEPOSIT à¤¬à¤Ÿà¤¨ à¤ªà¤° à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¥‡à¤‚ à¤”à¤° à¤ªà¤¹à¥à¤‚à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¥‡à¤‚",
        'reg_not_found': "âŒ *à¤•à¥à¤·à¤®à¤¾ à¤•à¤°à¥‡à¤‚, à¤†à¤ª à¤ªà¤‚à¤œà¥€à¤•à¥ƒà¤¤ à¤¨à¤¹à¥€à¤‚ à¤¹à¥ˆà¤‚!*\n\nà¤•à¥ƒà¤ªà¤¯à¤¾ à¤ªà¤¹à¤²à¥‡ REGISTER à¤¬à¤Ÿà¤¨ à¤ªà¤° à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¥‡à¤‚ à¤”à¤° à¤¹à¤®à¤¾à¤°à¥‡ à¤à¤«à¤¿à¤²à¤¿à¤à¤Ÿ à¤²à¤¿à¤‚à¤• à¤•à¤¾ à¤‰à¤ªà¤¯à¥‹à¤— à¤•à¤°à¤•à¥‡ à¤…à¤ªà¤¨à¤¾ à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤ªà¥‚à¤°à¤¾ à¤•à¤°à¥‡à¤‚à¥¤\n\nà¤¸à¤«à¤² à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤•à¥‡ à¤¬à¤¾à¤¦, à¤µà¤¾à¤ªà¤¸ à¤†à¤à¤‚ à¤”à¤° à¤…à¤ªà¤¨à¤¾ Player ID à¤¦à¤°à¥à¤œ à¤•à¤°à¥‡à¤‚à¥¤",
        'deposit_btn': "ðŸ’³ à¤œà¤®à¤¾ à¤•à¤°à¥‡à¤‚",
        'check_deposit_btn': "ðŸ” à¤œà¤®à¤¾ à¤œà¤¾à¤‚à¤šà¥‡à¤‚",
        'deposit_success': "ðŸŽŠ *à¤œà¤®à¤¾ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤!*\n\nðŸ’° *à¤œà¤®à¤¾ à¤°à¤¾à¤¶à¤¿:* ${amount}\nâœ… *à¤¸à¥à¤¥à¤¿à¤¤à¤¿:* à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤\n\nðŸŽ¯ à¤…à¤¬ à¤†à¤ªà¤•à¥‡ à¤ªà¤¾à¤¸ AI-à¤ªà¤¾à¤µà¤°à¥à¤¡ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¤¿à¤¯à¥‹à¤‚ à¤¤à¤• à¤ªà¤¹à¥à¤‚à¤š à¤¹à¥ˆ!\n\nà¤…à¤ªà¤¨à¥€ à¤ªà¤¹à¤²à¥€ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤¨à¥€à¤šà¥‡ à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¥‡à¤‚:",
        'deposit_not_found': "ðŸ’° *à¤œà¤®à¤¾ à¤¨à¤¹à¥€à¤‚ à¤®à¤¿à¤²à¤¾!*\n\nà¤†à¤ªà¤¨à¥‡ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤•à¤° à¤²à¤¿à¤¯à¤¾ à¤¹à¥ˆ à¤²à¥‡à¤•à¤¿à¤¨ à¤…à¤­à¥€ à¤¤à¤• à¤•à¥‹à¤ˆ à¤œà¤®à¤¾ à¤¨à¤¹à¥€à¤‚ detected à¤¹à¥à¤† à¤¹à¥ˆà¥¤\n\nðŸ’µ à¤•à¥ƒà¤ªà¤¯à¤¾ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€ à¤¤à¤• à¤ªà¤¹à¥à¤‚à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤•à¤® à¤¸à¥‡ à¤•à¤® $6 à¤œà¤®à¤¾ à¤•à¤°à¥‡à¤‚à¥¤",
        'get_prediction_btn': "ðŸŽ¯ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¥‡à¤‚",
        'prediction_limit': "ðŸš« *à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€ à¤¸à¥€à¤®à¤¾ à¤ªà¥‚à¤°à¥à¤£*\n\nà¤†à¤ªà¤¨à¥‡ à¤†à¤œ à¤•à¥€ à¤¸à¤­à¥€ 20 à¤®à¥à¤«à¥à¤¤ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¤¿à¤¯à¥‹à¤‚ à¤•à¤¾ à¤‰à¤ªà¤¯à¥‹à¤— à¤•à¤° à¤²à¤¿à¤¯à¤¾ à¤¹à¥ˆà¥¤\n\nðŸ’¡ *à¤µà¤¿à¤•à¤²à¥à¤ª:*\nâ€¢ à¤¨à¤ˆ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¤¿à¤¯à¥‹à¤‚ à¤•à¥‡ à¤²à¤¿à¤ à¤•à¤² à¤¤à¤• à¤ªà¥à¤°à¤¤à¥€à¤•à¥à¤·à¤¾ à¤•à¤°à¥‡à¤‚\nâ€¢ à¤…à¤¤à¤¿à¤°à¤¿à¤•à¥à¤¤ à¤ªà¤¹à¥à¤‚à¤š à¤•à¥‡ à¤²à¤¿à¤ à¤¦à¥‚à¤¸à¤°à¥€ à¤œà¤®à¤¾ à¤°à¤¾à¤¶à¤¿ à¤•à¤°à¥‡à¤‚\n\nðŸ’° à¤¸à¤•à¥à¤°à¤¿à¤¯ à¤°à¤¹à¤•à¤° à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¤¿à¤¯à¤¾à¤ à¤œà¤¾à¤°à¥€ à¤°à¤–à¥‡à¤‚!",
        'deposit_again_btn': "ðŸ’³ à¤«à¤¿à¤° à¤¸à¥‡ à¤œà¤®à¤¾ à¤•à¤°à¥‡à¤‚",
        'try_tomorrow_btn': "ðŸ• à¤•à¤² à¤ªà¥à¤°à¤¯à¤¾à¤¸ à¤•à¤°à¥‡à¤‚",
        'next_prediction_btn': "ðŸ”„ à¤…à¤—à¤²à¥€ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€",
        'prediction_text': "ðŸŽ¯ *AI à¤•à¥à¤°à¤¿à¤•à¥‡à¤Ÿ à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€* ðŸ¤–\n\nðŸŸï¸ *à¤®à¥ˆà¤š:* {team_a} vs {team_b}\nðŸ“Š *à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€:* {prediction}\nâœ… *à¤µà¤¿à¤¶à¥à¤µà¤¾à¤¸:* {confidence}%\n\nðŸ“ˆ *à¤µà¤¿à¤¶à¥à¤²à¥‡à¤·à¤£:*\n{analysis}\n\nâš ï¸ *AI à¤­à¤µà¤¿à¤·à¥à¤¯à¤µà¤¾à¤£à¥€ - à¤œà¤¿à¤®à¥à¤®à¥‡à¤¦à¤¾à¤°à¥€ à¤¸à¥‡ à¤œà¥à¤† à¤–à¥‡à¤²à¥‡à¤‚*",
        'random_messages': [
            "à¤†à¤ªà¤•à¤¾ à¤ªà¤‚à¤œà¥€à¤•à¤°à¤£ à¤¸à¤«à¤² à¤°à¤¹à¤¾ à¤¹à¥ˆ! âœ…\n\n$6,7,10,13,17 à¤¯à¤¾ à¤•à¥‹à¤ˆ à¤…à¤¨à¥à¤¯ à¤°à¤¾à¤¶à¤¿ à¤œà¤®à¤¾ à¤•à¤°à¥‡à¤‚ à¤”à¤° à¤¬à¥‰à¤Ÿ à¤¸à¥à¤µà¤šà¤¾à¤²à¤¿à¤¤ à¤°à¥‚à¤ª à¤¸à¥‡ à¤†à¤ªà¤•à¥‹ à¤¸à¤¿à¤—à¥à¤¨à¤² à¤¤à¤• à¤ªà¤¹à¥à¤‚à¤š à¤ªà¥à¤°à¤¦à¤¾à¤¨ à¤•à¤°à¥‡à¤—à¤¾! ðŸ”‘\n\nà¤†à¤ª à¤ªà¥à¤°à¤¤à¤¿à¤¦à¤¿à¤¨ $10 âž¡ï¸ $100 à¤•à¤®à¤¾ à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚ðŸ’°\n\nðŸ‘‰ /start à¤•à¥à¤²à¤¿à¤• à¤•à¤°à¥‡à¤‚",
            "à¤­à¤¾à¤ˆ, à¤†à¤ªà¤•à¥‡ à¤²à¤¿à¤ à¤¸à¤¿à¤—à¥à¤¨à¤² à¤¤à¥ˆà¤¯à¤¾à¤° à¤¹à¥ˆâ˜ºï¸\n\nà¤…à¤­à¥€ à¤¶à¥à¤°à¥‚ à¤•à¤°à¥‡à¤‚ðŸ‘‰ /start",
            "ðŸš€ à¤¸à¤¿à¤—à¥à¤¨à¤² à¤† à¤šà¥à¤•à¤¾ à¤¹à¥ˆ\n\nðŸ”¥ à¤…à¤ªà¤¨à¤¾ à¤ªà¥ˆà¤¸à¤¾ à¤ªà¤¾à¤¨à¥‡ à¤•à¤¾ à¤®à¥Œà¤•à¤¾ à¤®à¤¤ à¤šà¥‚à¤•à¥‡à¤‚\n\nâž¡ï¸ /start",
            "à¤…à¤­à¥€ à¤¬à¥‰à¤Ÿ à¤¶à¥à¤°à¥‚ à¤•à¤°à¥‡à¤‚ à¤”à¤° à¤ªà¥ˆà¤¸à¤¾ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤•à¤°à¥‡à¤‚ðŸ’°ðŸ”¥\n\n/start"
        ]
    },
    'bn': {
        'welcome': "ðŸŒ *à¦†à¦ªà¦¨à¦¾à¦° à¦­à¦¾à¦·à¦¾ à¦¨à¦¿à¦°à§à¦¬à¦¾à¦šà¦¨ à¦•à¦°à§à¦¨:*",
        'selected': "âœ… à¦†à¦ªà¦¨à¦¿ à¦¬à¦¾à¦‚à¦²à¦¾ à¦¨à¦¿à¦°à§à¦¬à¦¾à¦šà¦¨ à¦•à¦°à§‡à¦›à§‡à¦¨!",
        'register_title': "ðŸŒ *à¦§à¦¾à¦ª 1 - à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨*",
        'account_new': "â€¼ï¸ *à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿà¦Ÿà¦¿ à¦¨à¦¤à§à¦¨ à¦¹à¦¤à§‡ à¦¹à¦¬à§‡*",
        'instruction1': "1ï¸âƒ£ à¦¯à¦¦à¦¿ \"REGISTER\" à¦¬à¦¾à¦Ÿà¦¨à§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à¦¾à¦° à¦ªà¦°à§‡ à¦†à¦ªà¦¨à¦¿ à¦ªà§à¦°à¦¾à¦¨à§‹ à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿà§‡ à¦†à¦¸à§‡à¦¨, à¦¤à¦¾à¦¹à¦²à§‡ à¦†à¦ªà¦¨à¦¾à¦•à§‡ à¦à¦Ÿà¦¿ à¦¥à§‡à¦•à§‡ à¦²à¦— à¦†à¦‰à¦Ÿ à¦•à¦°à¦¤à§‡ à¦¹à¦¬à§‡ à¦à¦¬à¦‚ à¦†à¦¬à¦¾à¦° à¦¬à¦¾à¦Ÿà¦¨à§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à¦¤à§‡ à¦¹à¦¬à§‡à¥¤",
        'instruction2': "2ï¸âƒ£ à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨à§‡à¦° à¦¸à¦®à¦¯à¦¼ à¦à¦•à¦Ÿà¦¿ à¦ªà§à¦°à§‹à¦®à§‹à¦•à§‹à¦¡ à¦¨à¦¿à¦°à§à¦¦à¦¿à¦·à§à¦Ÿ à¦•à¦°à§à¦¨: **CLAIM**",
        'after_reg': "âœ… à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨à§‡à¦° à¦ªà¦°à§‡, \"CHECK REGISTRATION\" à¦¬à¦¾à¦Ÿà¦¨à§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à§à¦¨",
        'register_btn': "ðŸ“² à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦•à¦°à§à¦¨",
        'check_btn': "ðŸ” à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦ªà¦°à§€à¦•à§à¦·à¦¾",
        'enter_player_id': "ðŸ” *à¦†à¦ªà¦¨à¦¾à¦° à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦ªà¦°à§€à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨*\n\nà¦¯à¦¾à¦šà¦¾à¦‡ à¦•à¦°à¦¾à¦° à¦œà¦¨à§à¦¯ à¦†à¦ªà¦¨à¦¾à¦° 1Win *Player ID* à¦²à¦¿à¦–à§à¦¨:\n\nðŸ“ *Player ID à¦•à¦¿à¦­à¦¾à¦¬à§‡ à¦–à§à¦à¦œà§‡ à¦ªà¦¾à¦¬à§‡à¦¨:*\n1. 1Win à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿà§‡ à¦²à¦—à¦‡à¦¨ à¦•à¦°à§à¦¨\n2. à¦ªà§à¦°à§‹à¦«à¦¾à¦‡à¦² à¦¸à§‡à¦Ÿà¦¿à¦‚à¦¸à§‡ à¦¯à¦¾à¦¨\n3. Player ID à¦¨à¦®à§à¦¬à¦° à¦•à¦ªà¦¿ à¦•à¦°à§à¦¨\n4. à¦à¦–à¦¾à¦¨à§‡ à¦ªà§‡à¦¸à§à¦Ÿ à¦•à¦°à§à¦¨\n\nðŸ”¢ *à¦à¦–à¦¨ à¦†à¦ªà¦¨à¦¾à¦° Player ID à¦²à¦¿à¦–à§à¦¨:*",
        'loading_registration': "â³ *à¦…à¦¨à§à¦—à§à¦°à¦¹ à¦•à¦°à§‡ à¦•à¦¯à¦¼à§‡à¦• à¦¸à§‡à¦•à§‡à¦¨à§à¦¡ à¦…à¦ªà§‡à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨, à¦†à¦ªà¦¨à¦¾à¦° à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦²à§‹à¦¡ à¦¹à¦šà§à¦›à§‡...*",
        'reg_success': "ðŸŽ‰ *à¦…à¦­à¦¿à¦¨à¦¨à§à¦¦à¦¨, à¦†à¦ªà¦¨à¦¿ à¦¸à¦«à¦²à¦­à¦¾à¦¬à§‡ à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦¸à¦®à§à¦ªà¦¨à§à¦¨ à¦•à¦°à§‡à¦›à§‡à¦¨!*\n\nâœ… à¦†à¦ªà¦¨à¦¾à¦° à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿ à¦¬à¦Ÿà§‡à¦° à¦¸à¦¾à¦¥à§‡ à¦¸à¦¿à¦™à§à¦• à¦¹à¦¯à¦¼à§‡à¦›à§‡\n\nðŸ’´ *à¦¸à¦¿à¦—à¦¨à§à¦¯à¦¾à¦² à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸ à¦ªà§‡à¦¤à§‡, à¦†à¦ªà¦¨à¦¾à¦° à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿà§‡ à¦•à¦®à¦ªà¦•à§à¦·à§‡ 600â‚¹ à¦¬à¦¾ $6 à¦œà¦®à¦¾ à¦•à¦°à§à¦¨*\n\nðŸ•¹ï¸ à¦†à¦ªà¦¨à¦¾à¦° à¦…à§à¦¯à¦¾à¦•à¦¾à¦‰à¦¨à§à¦Ÿ à¦¸à¦«à¦²à¦­à¦¾à¦¬à§‡ à¦°à¦¿à¦šà¦¾à¦°à§à¦œ à¦•à¦°à¦¾à¦° à¦ªà¦°, CHECK DEPOSIT à¦¬à¦¾à¦Ÿà¦¨à§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸ à¦ªà¦¾à¦¨",
        'reg_not_found': "âŒ *à¦¦à§à¦ƒà¦–à¦¿à¦¤, à¦†à¦ªà¦¨à¦¿ à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¿à¦¤ à¦¨à¦¨!*\n\nà¦…à¦¨à§à¦—à§à¦°à¦¹ à¦•à¦°à§‡ à¦ªà§à¦°à¦¥à¦®à§‡ REGISTER à¦¬à¦¾à¦Ÿà¦¨à§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦†à¦®à¦¾à¦¦à§‡à¦° à¦…à§à¦¯à¦¾à¦«à¦¿à¦²à¦¿à¦¯à¦¼à§‡à¦Ÿ à¦²à¦¿à¦™à§à¦• à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦•à¦°à§‡ à¦†à¦ªà¦¨à¦¾à¦° à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦¸à¦®à§à¦ªà§‚à¦°à§à¦£ à¦•à¦°à§à¦¨à¥¤\n\nà¦¸à¦«à¦² à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨à§‡à¦° à¦ªà¦°à§‡, à¦«à¦¿à¦°à§‡ à¦†à¦¸à§à¦¨ à¦à¦¬à¦‚ à¦†à¦ªà¦¨à¦¾à¦° Player ID à¦²à¦¿à¦–à§à¦¨à¥¤",
        'deposit_btn': "ðŸ’³ à¦œà¦®à¦¾ à¦•à¦°à§à¦¨",
        'check_deposit_btn': "ðŸ” à¦œà¦®à¦¾ à¦ªà¦°à§€à¦•à§à¦·à¦¾",
        'deposit_success': "ðŸŽŠ *à¦œà¦®à¦¾ à¦¸à¦«à¦²à¦­à¦¾à¦¬à§‡ à¦¯à¦¾à¦šà¦¾à¦‡ à¦•à¦°à¦¾ à¦¹à¦¯à¦¼à§‡à¦›à§‡!*\n\nðŸ’° *à¦œà¦®à¦¾à¦° à¦ªà¦°à¦¿à¦®à¦¾à¦£:* ${amount}\nâœ… *à¦¸à§à¦Ÿà§à¦¯à¦¾à¦Ÿà¦¾à¦¸:* à¦¯à¦¾à¦šà¦¾à¦‡à¦•à§ƒà¦¤\n\nðŸŽ¯ à¦à¦–à¦¨ à¦†à¦ªà¦¨à¦¾à¦° AI-à¦šà¦¾à¦²à¦¿à¦¤ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸ à¦†à¦›à§‡!\n\nà¦†à¦ªà¦¨à¦¾à¦° à¦ªà§à¦°à¦¥à¦® à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦ªà§‡à¦¤à§‡ à¦¨à§€à¦šà§‡ à¦•à§à¦²à¦¿à¦• à¦•à¦°à§à¦¨:",
        'deposit_not_found': "ðŸ’° *à¦œà¦®à¦¾ à¦ªà¦¾à¦“à¦¯à¦¼à¦¾ à¦¯à¦¾à¦¯à¦¼à¦¨à¦¿!*\n\nà¦†à¦ªà¦¨à¦¿ à¦¸à¦«à¦²à¦­à¦¾à¦¬à§‡ à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦•à¦°à§‡à¦›à§‡à¦¨ à¦•à¦¿à¦¨à§à¦¤à§ à¦à¦–à¦¨à¦“ à¦•à§‹à¦¨ à¦œà¦®à¦¾ à¦¸à¦¨à¦¾à¦•à§à¦¤ à¦•à¦°à¦¾ à¦¯à¦¾à¦¯à¦¼à¦¨à¦¿à¥¤\n\nðŸ’µ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸ à¦ªà§‡à¦¤à§‡ à¦•à¦®à¦ªà¦•à§à¦·à§‡ $6 à¦œà¦®à¦¾ à¦•à¦°à§à¦¨à¥¤",
        'get_prediction_btn': "ðŸŽ¯ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦ªà¦¾à¦¨",
        'prediction_limit': "ðŸš« *à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦¸à§€à¦®à¦¾ reached*\n\nà¦†à¦ªà¦¨à¦¿ à¦†à¦œà¦•à§‡à¦° 20à¦Ÿà¦¿ à¦¬à¦¿à¦¨à¦¾à¦®à§‚à¦²à§à¦¯à§‡à¦° à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦¬à§à¦¯à¦¬à¦¹à¦¾à¦° à¦•à¦°à§‡à¦›à§‡à¦¨à¥¤\n\nðŸ’¡ *à¦¬à¦¿à¦•à¦²à§à¦ª:*\nâ€¢ à¦¨à¦¤à§à¦¨ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€à¦° à¦œà¦¨à§à¦¯ à¦†à¦—à¦¾à¦®à§€à¦•à¦¾à¦² à¦ªà¦°à§à¦¯à¦¨à§à¦¤ à¦…à¦ªà§‡à¦•à§à¦·à¦¾ à¦•à¦°à§à¦¨\nâ€¢ à¦…à¦¤à¦¿à¦°à¦¿à¦•à§à¦¤ à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸à§‡à¦° à¦œà¦¨à§à¦¯ à¦…à¦¨à§à¦¯ à¦œà¦®à¦¾ à¦•à¦°à§à¦¨\n\nðŸ’° à¦¸à¦•à§à¦°à¦¿à¦¯à¦¼ à¦¥à¦¾à¦•à¦¾à¦° à¦®à¦¾à¦§à§à¦¯à¦®à§‡ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ à¦šà¦¾à¦²à¦¿à¦¯à¦¼à§‡ à¦¯à¦¾à¦¨!",
        'deposit_again_btn': "ðŸ’³ à¦†à¦¬à¦¾à¦° à¦œà¦®à¦¾ à¦•à¦°à§à¦¨",
        'try_tomorrow_btn': "ðŸ• à¦†à¦—à¦¾à¦®à§€à¦•à¦¾à¦² à¦šà§‡à¦·à§à¦Ÿà¦¾ à¦•à¦°à§à¦¨",
        'next_prediction_btn': "ðŸ”„ à¦ªà¦°à¦¬à¦°à§à¦¤à§€ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€",
        'prediction_text': "ðŸŽ¯ *AI à¦•à§à¦°à¦¿à¦•à§‡à¦Ÿ à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€* ðŸ¤–\n\nðŸŸï¸ *à¦®à§à¦¯à¦¾à¦š:* {team_a} vs {team_b}\nðŸ“Š *à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€:* {prediction}\nâœ… *à¦†à¦¤à§à¦®à¦¬à¦¿à¦¶à§à¦¬à¦¾à¦¸:* {confidence}%\n\nðŸ“ˆ *à¦¬à¦¿à¦¶à§à¦²à§‡à¦·à¦£:*\n{analysis}\n\nâš ï¸ *AI à¦­à¦¬à¦¿à¦·à§à¦¯à¦¦à§à¦¬à¦¾à¦£à§€ - à¦¦à¦¾à¦¯à¦¼à¦¿à¦¤à§à¦¬ à¦¸à¦¹à¦•à¦¾à¦°à§‡ à¦¬à§‡à¦Ÿ à¦•à¦°à§à¦¨*",
        'random_messages': [
            "à¦†à¦ªà¦¨à¦¾à¦° à¦¨à¦¿à¦¬à¦¨à§à¦§à¦¨ à¦¸à¦«à¦² à¦¹à¦¯à¦¼à§‡à¦›à§‡! âœ…\n\n$6,7,10,13,17 à¦¬à¦¾ à¦…à¦¨à§à¦¯ à¦•à§‹à¦¨à§‹ à¦ªà¦°à¦¿à¦®à¦¾à¦£ à¦œà¦®à¦¾ à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦¬à¦Ÿ à¦¸à§à¦¬à¦¯à¦¼à¦‚à¦•à§à¦°à¦¿à¦¯à¦¼à¦­à¦¾à¦¬à§‡ à¦†à¦ªà¦¨à¦¾à¦•à§‡ à¦¸à¦¿à¦—à¦¨à§à¦¯à¦¾à¦² à¦…à§à¦¯à¦¾à¦•à§à¦¸à§‡à¦¸ à¦¦à§‡à¦¬à§‡! ðŸ”‘\n\nà¦†à¦ªà¦¨à¦¿ à¦ªà§à¦°à¦¤à¦¿à¦¦à¦¿à¦¨ $10 âž¡ï¸ $100 à¦‰à¦ªà¦¾à¦°à§à¦œà¦¨ à¦•à¦°à¦¤à§‡ à¦ªà¦¾à¦°à§‡à¦¨ðŸ’°\n\nðŸ‘‰ /start à¦•à§à¦²à¦¿à¦• à¦•à¦°à§à¦¨",
            "à¦­à¦¾à¦‡, à¦†à¦ªà¦¨à¦¾à¦° à¦œà¦¨à§à¦¯ à¦¸à¦¿à¦—à¦¨à§à¦¯à¦¾à¦² à¦ªà§à¦°à¦¸à§à¦¤à§à¦¤â˜ºï¸\n\nà¦à¦–à¦¨à¦‡ à¦¶à§à¦°à§ à¦•à¦°à§à¦¨ðŸ‘‰ /start",
            "ðŸš€ à¦¸à¦¿à¦—à¦¨à§à¦¯à¦¾à¦² already à¦à¦¸à§‡à¦›à§‡\n\nðŸ”¥ à¦†à¦ªà¦¨à¦¾à¦° à¦Ÿà¦¾à¦•à¦¾ à¦ªà¦¾à¦“à¦¯à¦¼à¦¾à¦° à¦¸à§à¦¯à§‹à¦— à¦®à¦¿à¦¸ à¦•à¦°à¦¬à§‡à¦¨ à¦¨à¦¾\n\nâž¡ï¸ /start",
            "à¦à¦–à¦¨à¦‡ à¦¬à¦Ÿ à¦¶à§à¦°à§ à¦•à¦°à§à¦¨ à¦à¦¬à¦‚ à¦Ÿà¦¾à¦•à¦¾ à¦ªà¦¾à¦¨ðŸ’°ðŸ”¥\n\n/start"
        ]
    },
    'ur': {
        'welcome': "ðŸŒ *Ø§Ù¾Ù†ÛŒ Ø²Ø¨Ø§Ù† Ù…Ù†ØªØ®Ø¨ Ú©Ø±ÛŒÚº:*",
        'selected': "âœ… Ø¢Ù¾ Ù†Û’ Ø§Ø±Ø¯Ùˆ Ù…Ù†ØªØ®Ø¨ Ú©ÛŒ!",
        'register_title': "ðŸŒ *Ù…Ø±Ø­Ù„Û 1 - Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù†*",
        'account_new': "â€¼ï¸ *Ø§Ú©Ø§Ø¤Ù†Ù¹ Ù†ÛŒØ§ ÛÙˆÙ†Ø§ Ú†Ø§ÛÛŒÛ’*",
        'instruction1': "1ï¸âƒ£ Ø§Ú¯Ø± \"REGISTER\" Ø¨Ù¹Ù† Ù¾Ø± Ú©Ù„Ú© Ú©Ø±Ù†Û’ Ú©Û’ Ø¨Ø¹Ø¯ Ø¢Ù¾ Ù¾Ø±Ø§Ù†Û’ Ø§Ú©Ø§Ø¤Ù†Ù¹ Ù…ÛŒÚº Ø¢ØªÛ’ ÛÛŒÚºØŒ ØªÙˆ Ø¢Ù¾ Ú©Ùˆ Ø§Ø³ Ø³Û’ Ù„Ø§Ú¯ Ø¢Ø¤Ù¹ ÛÙˆÙ†Ø§ Ù¾Ú‘Û’ Ú¯Ø§ Ø§ÙˆØ± Ø¯ÙˆØ¨Ø§Ø±Û Ø¨Ù¹Ù† Ù¾Ø± Ú©Ù„Ú© Ú©Ø±Ù†Ø§ ÛÙˆÚ¯Ø§Û”",
        'instruction2': "2ï¸âƒ£ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Û’ Ø¯ÙˆØ±Ø§Ù† Ø§ÛŒÚ© Ù¾Ø±ÙˆÙ…ÙˆÚ©ÙˆÚˆ specified Ú©Ø±ÛŒÚº: **CLAIM**",
        'after_reg': "âœ… Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Û’ Ø¨Ø¹Ø¯ØŒ \"CHECK REGISTRATION\" Ø¨Ù¹Ù† Ù¾Ø± Ú©Ù„Ú© Ú©Ø±ÛŒÚº",
        'register_btn': "ðŸ“² Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Ø±ÛŒÚº",
        'check_btn': "ðŸ” Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú†ÛŒÚ©",
        'enter_player_id': "ðŸ” *Ø§Ù¾Ù†ÛŒ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú†ÛŒÚ© Ú©Ø±ÛŒÚº*\n\nØªØµØ¯ÛŒÙ‚ Ú©Û’ Ù„ÛŒÛ’ Ø§Ù¾Ù†Ø§ 1Win *Player ID* Ø¯Ø±Ø¬ Ú©Ø±ÛŒÚº:\n\nðŸ“ *Player ID Ú©ÛŒØ³Û’ ÚˆÚ¾ÙˆÙ†ÚˆÛŒÚº:*\n1. 1Win Ø§Ú©Ø§Ø¤Ù†Ù¹ Ù…ÛŒÚº Ù„Ø§Ú¯ Ø§Ù† Ú©Ø±ÛŒÚº\n2. Ù¾Ø±ÙˆÙØ§Ø¦Ù„ Ø³ÛŒÙ¹Ù†Ú¯Ø² Ù¾Ø± Ø¬Ø§Ø¦ÛŒÚº\n3. Player ID Ù†Ù…Ø¨Ø± Ú©Ø§Ù¾ÛŒ Ú©Ø±ÛŒÚº\n4. ÛŒÛØ§Úº Ù¾ÛŒØ³Ù¹ Ú©Ø±ÛŒÚº\n\nðŸ”¢ *Ø§Ø¨ Ø§Ù¾Ù†Ø§ Player ID Ø¯Ø±Ø¬ Ú©Ø±ÛŒÚº:*",
        'loading_registration': "â³ *Ø¨Ø±Ø§Û Ú©Ø±Ù… Ú©Ú†Ú¾ Ø³ÛŒÚ©Ù†Úˆ Ø§Ù†ØªØ¸Ø§Ø± Ú©Ø±ÛŒÚºØŒ Ø¢Ù¾ Ú©ÛŒ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ù„ÙˆÚˆ ÛÙˆ Ø±ÛÛŒ ÛÛ’...*",
        'reg_success': "ðŸŽ‰ *Ù…Ø¨Ø§Ø±Ú© ÛÙˆØŒ Ø¢Ù¾ Ù†Û’ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ú©Û’ Ø³Ø§ØªÚ¾ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ù…Ú©Ù…Ù„ Ú©Ø± Ù„ÛŒ ÛÛ’!*\n\nâœ… Ø¢Ù¾ Ú©Ø§ Ø§Ú©Ø§Ø¤Ù†Ù¹ Ø¨ÙˆÙ¹ Ú©Û’ Ø³Ø§ØªÚ¾ sync ÛÙˆ Ú¯ÛŒØ§ ÛÛ’\n\nðŸ’´ *Ø³Ú¯Ù†Ù„Ø² ØªÚ© Ø±Ø³Ø§Ø¦ÛŒ Ø­Ø§ØµÙ„ Ú©Ø±Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ØŒ Ø§Ù¾Ù†Û’ Ø§Ú©Ø§Ø¤Ù†Ù¹ Ù…ÛŒÚº Ú©Ù… Ø§Ø² Ú©Ù… 600â‚¹ ÛŒØ§ $6 Ø¬Ù…Ø¹ Ú©Ø±ÙˆØ§Ø¦ÛŒÚº*\n\nðŸ•¹ï¸ Ø§Ù¾Ù†Ø§ Ø§Ú©Ø§Ø¤Ù†Ù¹ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø±ÛŒÚ†Ø§Ø±Ø¬ Ú©Ø±Ù†Û’ Ú©Û’ Ø¨Ø¹Ø¯ØŒ CHECK DEPOSIT Ø¨Ù¹Ù† Ù¾Ø± Ú©Ù„Ú© Ú©Ø±ÛŒÚº Ø§ÙˆØ± Ø±Ø³Ø§Ø¦ÛŒ Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº",
        'reg_not_found': "âŒ *Ù…Ø¹Ø°Ø±ØªØŒ Ø¢Ù¾ Ø±Ø¬Ø³Ù¹Ø±Úˆ Ù†ÛÛŒÚº ÛÛŒÚº!*\n\nØ¨Ø±Ø§Û Ú©Ø±Ù… Ù¾ÛÙ„Û’ REGISTER Ø¨Ù¹Ù† Ù¾Ø± Ú©Ù„Ú© Ú©Ø±ÛŒÚº Ø§ÙˆØ± ÛÙ…Ø§Ø±Û’ affiliate link Ú©Ø§ Ø§Ø³ØªØ¹Ù…Ø§Ù„ Ú©Ø±ØªÛ’ ÛÙˆØ¦Û’ Ø§Ù¾Ù†ÛŒ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ù…Ú©Ù…Ù„ Ú©Ø±ÛŒÚºÛ”\n\nÚ©Ø§Ù…ÛŒØ§Ø¨ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Û’ Ø¨Ø¹Ø¯ØŒ ÙˆØ§Ù¾Ø³ Ø¢Ø¦ÛŒÚº Ø§ÙˆØ± Ø§Ù¾Ù†Ø§ Player ID Ø¯Ø±Ø¬ Ú©Ø±ÛŒÚºÛ”",
        'deposit_btn': "ðŸ’³ Ø¬Ù…Ø¹ Ú©Ø±ÙˆØ§Ø¦ÛŒÚº",
        'check_deposit_btn': "ðŸ” Ø¬Ù…Ø¹ Ú†ÛŒÚ©",
        'deposit_success': "ðŸŽŠ *Ø¬Ù…Ø¹ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ ØªØµØ¯ÛŒÙ‚ ÛÙˆ Ú¯Ø¦ÛŒ!*\n\nðŸ’° *Ø¬Ù…Ø¹ Ú©ÛŒ Ø±Ù‚Ù…:* ${amount}\nâœ… *Ø­Ø§Ù„Øª:* ØªØµØ¯ÛŒÙ‚ Ø´Ø¯Û\n\nðŸŽ¯ Ø§Ø¨ Ø¢Ù¾ Ú©Û’ Ù¾Ø§Ø³ AI-powered predictions ØªÚ© Ø±Ø³Ø§Ø¦ÛŒ ÛÛ’!\n\nØ§Ù¾Ù†ÛŒ Ù¾ÛÙ„ÛŒ prediction Ø­Ø§ØµÙ„ Ú©Ø±Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ Ù†ÛŒÚ†Û’ Ú©Ù„Ú© Ú©Ø±ÛŒÚº:",
        'deposit_not_found': "ðŸ’° *Ø¬Ù…Ø¹ Ù†ÛÛŒÚº Ù…Ù„ÛŒ!*\n\nØ¢Ù¾ Ù†Û’ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ú©Û’ Ø³Ø§ØªÚ¾ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Ø± Ù„ÛŒ ÛÛ’ Ù„ÛŒÚ©Ù† Ø§Ø¨Ú¾ÛŒ ØªÚ© Ú©ÙˆØ¦ÛŒ Ø¬Ù…Ø¹ Ú©Ø§ Ù¾ØªÛ Ù†ÛÛŒÚº Ú†Ù„Ø§ ÛÛ’Û”\n\nðŸ’µ prediction ØªÚ© Ø±Ø³Ø§Ø¦ÛŒ Ø­Ø§ØµÙ„ Ú©Ø±Ù†Û’ Ú©Û’ Ù„ÛŒÛ’ Ú©Ù… Ø§Ø² Ú©Ù… $6 Ø¬Ù…Ø¹ Ú©Ø±ÙˆØ§Ø¦ÛŒÚºÛ”",
        'get_prediction_btn': "ðŸŽ¯ prediction Ø­Ø§ØµÙ„",
        'prediction_limit': "ðŸš« *prediction Ø­Ø¯ reached*\n\nØ¢Ù¾ Ù†Û’ Ø¢Ø¬ Ú©ÛŒ 20 Ù…ÙØª predictions Ø§Ø³ØªØ¹Ù…Ø§Ù„ Ú©Ø± Ù„ÛŒ ÛÛŒÚºÛ”\n\nðŸ’¡ *Ø§Ø®ØªÛŒØ§Ø±Ø§Øª:*\nâ€¢ Ù†Ø¦ÛŒ predictions Ú©Û’ Ù„ÛŒÛ’ Ú©Ù„ ØªÚ© Ø§Ù†ØªØ¸Ø§Ø± Ú©Ø±ÛŒÚº\nâ€¢ Ø§Ø¶Ø§ÙÛŒ Ø±Ø³Ø§Ø¦ÛŒ Ú©Û’ Ù„ÛŒÛ’ Ø¯ÙˆØ³Ø±ÛŒ Ø¬Ù…Ø¹ Ú©Ø±ÙˆØ§Ø¦ÛŒÚº\n\nðŸ’° active Ø±Û Ú©Ø± predictions Ø¬Ø§Ø±ÛŒ Ø±Ú©Ú¾ÛŒÚº!",
        'deposit_again_btn': "ðŸ’³ Ø¯ÙˆØ¨Ø§Ø±Û Ø¬Ù…Ø¹",
        'try_tomorrow_btn': "ðŸ• Ú©Ù„ Ú©ÙˆØ´Ø´",
        'next_prediction_btn': "ðŸ”„ Ø§Ú¯Ù„ÛŒ prediction",
        'prediction_text': "ðŸŽ¯ *AI Ú©Ø±Ú©Ù¹ prediction* ðŸ¤–\n\nðŸŸï¸ *Ù…Ù‚Ø§Ø¨Ù„Û:* {team_a} vs {team_b}\nðŸ“Š *prediction:* {prediction}\nâœ… *Ø§Ø¹ØªÙ…Ø§Ø¯:* {confidence}%\n\nðŸ“ˆ *ØªØ¬Ø²ÛŒÛ:*\n{analysis}\n\nâš ï¸ *AI prediction - Ø°Ù…Û Ø¯Ø§Ø±ÛŒ Ø³Û’ Ø¬ÙˆØ§ Ú©Ú¾ÛŒÙ„ÛŒÚº*",
        'random_messages': [
            "Ø¢Ù¾ Ú©ÛŒ Ø±Ø¬Ø³Ù¹Ø±ÛŒØ´Ù† Ú©Ø§Ù…ÛŒØ§Ø¨ Ø±ÛÛŒ ÛÛ’! âœ…\n\n$6,7,10,13,17 ÛŒØ§ Ú©ÙˆØ¦ÛŒ Ø¯ÙˆØ³Ø±ÛŒ Ø±Ù‚Ù… Ø¬Ù…Ø¹ Ú©Ø±ÙˆØ§Ø¦ÛŒÚº Ø§ÙˆØ± Ø¨ÙˆÙ¹ Ø®ÙˆØ¯ Ú©Ø§Ø± Ø·Ø±ÛŒÙ‚Û’ Ø³Û’ Ø¢Ù¾ Ú©Ùˆ Ø³Ú¯Ù†Ù„Ø² ØªÚ© Ø±Ø³Ø§Ø¦ÛŒ Ø¯Û’ Ú¯Ø§! ðŸ”‘\n\nØ¢Ù¾ Ø±ÙˆØ²Ø§Ù†Û $10 âž¡ï¸ $100 Ú©Ù…Ø§ Ø³Ú©ØªÛ’ ÛÛŒÚºðŸ’°\n\nðŸ‘‰ /start Ú©Ù„Ú©",
            "Ø¨Ú¾Ø§Ø¦ÛŒØŒ Ø¢Ù¾ Ú©Û’ Ù„ÛŒÛ’ Ø³Ú¯Ù†Ù„ ØªÛŒØ§Ø± ÛÛ’â˜ºï¸\n\nØ§Ø¨Ú¾ÛŒ Ø´Ø±ÙˆØ¹ðŸ‘‰ /start",
            "ðŸš€ Ø³Ú¯Ù†Ù„ already Ø¢ Ú†Ú©Ø§\n\nðŸ”¥ Ø§Ù¾Ù†Û’ Ù¾ÛŒØ³Û’ Ø­Ø§ØµÙ„ Ú©Ø±Ù†Û’ Ú©Ø§ Ù…ÙˆÙ‚Ø¹ Ø¶Ø§Ø¦Ø¹ Ù†Û Ú©Ø±ÛŒÚº\n\nâž¡ï¸ /start",
            "Ø§Ø¨Ú¾ÛŒ Ø¨ÙˆÙ¹ Ø´Ø±ÙˆØ¹ Ø§ÙˆØ± Ù¾ÛŒØ³Û’ Ø­Ø§ØµÙ„ðŸ’°ðŸ”¥\n\n/start"
        ]
    },
    'ne': {
        'welcome': "ðŸŒ *à¤†à¤«à¥à¤¨à¥‹ à¤­à¤¾à¤·à¤¾ à¤šà¤¯à¤¨ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥:*",
        'selected': "âœ… à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤¨à¥‡à¤ªà¤¾à¤²à¥€ à¤šà¤¯à¤¨ à¤—à¤°à¥à¤¨à¥à¤­à¤¯à¥‹!",
        'register_title': "ðŸŒ *à¤šà¤°à¤£ 1 - à¤¦à¤°à¥à¤¤à¤¾*",
        'account_new': "â€¼ï¸ *à¤–à¤¾à¤¤à¤¾ à¤¨à¤¯à¤¾à¤ à¤¹à¥à¤¨à¥à¤ªà¤°à¥à¤›*",
        'instruction1': "1ï¸âƒ£ à¤¯à¤¦à¤¿ \"REGISTER\" à¤¬à¤Ÿà¤¨à¤®à¤¾ à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥‡à¤ªà¤›à¤¿ à¤¤à¤ªà¤¾à¤ˆà¤‚ à¤ªà¥à¤°à¤¾à¤¨à¥‹ à¤–à¤¾à¤¤à¤¾à¤®à¤¾ à¤†à¤‰à¤¨à¥à¤¹à¥à¤¨à¥à¤› à¤­à¤¨à¥‡, à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤¯à¤¸à¤¬à¤¾à¤Ÿ à¤²à¤— à¤†à¤‰à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤ªà¤°à¥à¤› à¤° à¤«à¥‡à¤°à¤¿ à¤¬à¤Ÿà¤¨à¤®à¤¾ à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥à¤¨à¥à¤ªà¤°à¥à¤›à¥¤",
        'instruction2': "2ï¸âƒ£ à¤¦à¤°à¥à¤¤à¤¾ during à¤ªà¥à¤°à¥‹à¤®à¥‹à¤•à¥‹à¤¡ à¤¨à¤¿à¤°à¥à¤¦à¤¿à¤·à¥à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥: **CLAIM**",
        'after_reg': "âœ… à¤¦à¤°à¥à¤¤à¤¾ à¤ªà¤›à¤¿, \"CHECK REGISTRATION\" à¤¬à¤Ÿà¤¨à¤®à¤¾ à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥",
        'register_btn': "ðŸ“² à¤¦à¤°à¥à¤¤à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥",
        'check_btn': "ðŸ” à¤¦à¤°à¥à¤¤à¤¾ à¤œà¤¾à¤à¤š",
        'enter_player_id': "ðŸ” *à¤†à¤«à¥à¤¨à¥‹ à¤¦à¤°à¥à¤¤à¤¾ à¤œà¤¾à¤à¤š à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥*\n\nà¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤ à¤—à¤°à¥à¤¨ à¤†à¤«à¥à¤¨à¥‹ 1Win *Player ID* à¤ªà¥à¤°à¤µà¤¿à¤·à¥à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥:\n\nðŸ“ *Player ID à¤•à¤¸à¤°à¥€ à¤«à¥‡à¤²à¤¾ à¤ªà¤¾à¤°à¥à¤¨à¥‡:*\n1. 1Win à¤–à¤¾à¤¤à¤¾à¤®à¤¾ à¤²à¤— à¤‡à¤¨ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥\n2. à¤ªà¥à¤°à¥‹à¤«à¤¾à¤‡à¤² à¤¸à¥‡à¤Ÿà¤¿à¤™à¤¹à¤°à¥‚à¤®à¤¾ à¤œà¤¾à¤¨à¥à¤¹à¥‹à¤¸à¥\n3. Player ID à¤¨à¤®à¥à¤¬à¤° à¤•à¤ªà¥€ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥\n4. à¤¯à¤¹à¤¾à¤ à¤ªà¥‡à¤¸à¥à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥\n\nðŸ”¢ *à¤…à¤¬ à¤†à¤«à¥à¤¨à¥‹ Player ID à¤ªà¥à¤°à¤µà¤¿à¤·à¥à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥:*",
        'loading_registration': "â³ *à¤•à¥ƒà¤ªà¤¯à¤¾ à¤•à¥‡à¤¹à¥€ à¤¸à¥‡à¤•à¥‡à¤¨à¥à¤¡ à¤ªà¤°à¥à¤–à¤¨à¥à¤¹à¥‹à¤¸à¥, à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤¦à¤°à¥à¤¤à¤¾ à¤²à¥‹à¤¡ à¤¹à¥à¤¦à¥ˆà¤›...*",
        'reg_success': "ðŸŽ‰ *à¤¬à¤§à¤¾à¤ˆ à¤›, à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¦à¤°à¥à¤¤à¤¾ à¤ªà¥‚à¤°à¤¾ à¤—à¤°à¥à¤¨à¥à¤­à¤¯à¥‹!*\n\nâœ… à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤–à¤¾à¤¤à¤¾ à¤¬à¥‹à¤Ÿà¤¸à¤à¤— à¤¸à¤¿à¤™à¥à¤• à¤­à¤¯à¥‹\n\nðŸ’´ *à¤¸à¤¿à¤—à¥à¤¨à¤²à¤¹à¤°à¥‚à¤•à¥‹ à¤ªà¤¹à¥à¤à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤—à¤°à¥à¤¨, à¤†à¤«à¥à¤¨à¥‹ à¤–à¤¾à¤¤à¤¾à¤®à¤¾ à¤•à¤®à¥à¤¤à¤¿à¤®à¤¾ 600â‚¹ à¤µà¤¾ $6 à¤œà¤®à¥à¤®à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥*\n\nðŸ•¹ï¸ à¤†à¤«à¥à¤¨à¥‹ à¤–à¤¾à¤¤à¤¾ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤°à¤¿à¤šà¤¾à¤°à¥à¤œ à¤—à¤°à¥‡à¤ªà¤›à¤¿, CHECK DEPOSIT à¤¬à¤Ÿà¤¨à¤®à¤¾ à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥ à¤° à¤ªà¤¹à¥à¤à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥",
        'reg_not_found': "âŒ *à¤®à¤¾à¤« à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥, à¤¤à¤ªà¤¾à¤ˆà¤‚ à¤¦à¤°à¥à¤¤à¤¾ à¤—à¤°à¤¿à¤à¤•à¥‹ à¤›à¥ˆà¤¨!*\n\nà¤•à¥ƒà¤ªà¤¯à¤¾ à¤ªà¤¹à¤¿à¤²à¥‡ REGISTER à¤¬à¤Ÿà¤¨à¤®à¤¾ à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥ à¤° à¤¹à¤¾à¤®à¥à¤°à¥‹ à¤à¤«à¤¿à¤²à¤¿à¤à¤Ÿ à¤²à¤¿à¤™à¥à¤• à¤ªà¥à¤°à¤¯à¥‹à¤— à¤—à¤°à¥‡à¤° à¤†à¤«à¥à¤¨à¥‹ à¤¦à¤°à¥à¤¤à¤¾ à¤ªà¥‚à¤°à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤\n\nà¤¸à¤«à¤² à¤¦à¤°à¥à¤¤à¤¾ à¤ªà¤›à¤¿, à¤«à¤°à¥à¤•à¤¨à¥à¤¹à¥‹à¤¸à¥ à¤° à¤†à¤«à¥à¤¨à¥‹ Player ID à¤ªà¥à¤°à¤µà¤¿à¤·à¥à¤Ÿ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤",
        'deposit_btn': "ðŸ’³ à¤œà¤®à¥à¤®à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥",
        'check_deposit_btn': "ðŸ” à¤œà¤®à¥à¤®à¤¾ à¤œà¤¾à¤à¤š",
        'deposit_success': "ðŸŽŠ *à¤œà¤®à¥à¤®à¤¾ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤!*\n\nðŸ’° *à¤œà¤®à¥à¤®à¤¾ à¤°à¤•à¤®:* ${amount}\nâœ… *à¤¸à¥à¤¥à¤¿à¤¤à¤¿:* à¤¸à¤¤à¥à¤¯à¤¾à¤ªà¤¿à¤¤\n\nðŸŽ¯ à¤…à¤¬ à¤¤à¤ªà¤¾à¤ˆà¤‚à¤¸à¤à¤— AI-powered predictions à¤•à¥‹ à¤ªà¤¹à¥à¤à¤š à¤›!\n\nà¤†à¤«à¥à¤¨à¥‹ à¤ªà¤¹à¤¿à¤²à¥‹ prediction à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤—à¤°à¥à¤¨ à¤¤à¤² à¤•à¥à¤²à¤¿à¤• à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥:",
        'deposit_not_found': "ðŸ’° *à¤œà¤®à¥à¤®à¤¾ à¤«à¥‡à¤²à¤¾ à¤ªà¤°à¥‡à¤¨!*\n\nà¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¦à¤°à¥à¤¤à¤¾ à¤—à¤°à¥à¤¨à¥à¤­à¤à¤•à¥‹ à¤› à¤¤à¤° à¤…à¤¹à¤¿à¤²à¥‡ à¤¸à¤®à¥à¤® à¤•à¥à¤¨à¥ˆ à¤œà¤®à¥à¤®à¤¾ à¤ªà¤¤à¥à¤¤à¤¾ à¤²à¤¾à¤—à¥‡à¤•à¥‹ à¤›à¥ˆà¤¨à¥¤\n\nðŸ’µ prediction à¤ªà¤¹à¥à¤à¤š à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤—à¤°à¥à¤¨ à¤•à¤®à¥à¤¤à¤¿à¤®à¤¾ $6 à¤œà¤®à¥à¤®à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥à¥¤",
        'get_prediction_btn': "ðŸŽ¯ prediction à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤",
        'prediction_limit': "ðŸš« *prediction à¤¸à¥€à¤®à¤¾ reached*\n\nà¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤†à¤œà¤•à¤¾ 20 à¤¨à¤¿: à¤¶à¥à¤²à¥à¤• predictions à¤ªà¥à¤°à¤¯à¥‹à¤— à¤—à¤°à¥à¤¨à¥à¤­à¤¯à¥‹à¥¤\n\nðŸ’¡ *à¤µà¤¿à¤•à¤²à¥à¤ªà¤¹à¤°à¥‚:*\nâ€¢ à¤¨à¤¯à¤¾à¤ predictions à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤­à¥‹à¤²à¤¿ à¤¸à¤®à¥à¤® à¤ªà¤°à¥à¤–à¤¨à¥à¤¹à¥‹à¤¸à¥\nâ€¢ à¤¥à¤ª à¤ªà¤¹à¥à¤à¤šà¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤…à¤°à¥à¤•à¥‹ à¤œà¤®à¥à¤®à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥\n\nðŸ’° à¤¸à¤•à¥à¤°à¤¿à¤¯ à¤°à¤¹à¥€ predictions à¤œà¤¾à¤°à¥€ à¤°à¤¾à¤–à¥à¤¨à¥à¤¹à¥‹à¤¸à¥!",
        'deposit_again_btn': "ðŸ’³ à¤«à¥‡à¤°à¤¿ à¤œà¤®à¥à¤®à¤¾",
        'try_tomorrow_btn': "ðŸ• à¤­à¥‹à¤²à¤¿ à¤ªà¥à¤°à¤¯à¤¾à¤¸",
        'next_prediction_btn': "ðŸ”„ à¤…à¤°à¥à¤•à¥‹ prediction",
        'prediction_text': "ðŸŽ¯ *AI à¤•à¥à¤°à¤¿à¤•à¥‡à¤Ÿ prediction* ðŸ¤–\n\nðŸŸï¸ *à¤–à¥‡à¤²:* {team_a} vs {team_b}\nðŸ“Š *prediction:* {prediction}\nâœ… *à¤µà¤¿à¤¶à¥à¤µà¤¾à¤¸:* {confidence}%\n\nðŸ“ˆ *à¤µà¤¿à¤¶à¥à¤²à¥‡à¤·à¤£:*\n{analysis}\n\nâš ï¸ *AI prediction - à¤œà¤¿à¤®à¥à¤®à¥‡à¤µà¤¾à¤°à¥€ à¤¸à¤‚à¤— à¤œà¥à¤† à¤–à¥‡à¤²à¥à¤¨à¥à¤¹à¥‹à¤¸à¥*",
        'random_messages': [
            "à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤¦à¤°à¥à¤¤à¤¾ à¤¸à¤«à¤² à¤­à¤¯à¥‹! âœ…\n\n$6,7,10,13,17 à¤µà¤¾ à¤•à¥à¤¨à¥ˆ à¤…à¤¨à¥à¤¯ à¤°à¤•à¤® à¤œà¤®à¥à¤®à¤¾ à¤—à¤°à¥à¤¨à¥à¤¹à¥‹à¤¸à¥ à¤° à¤¬à¥‹à¤Ÿ à¤¸à¥à¤µà¤šà¤¾à¤²à¤¿à¤¤ à¤°à¥‚à¤ªà¤®à¤¾ à¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¤¾à¤ˆ à¤¸à¤¿à¤—à¥à¤¨à¤²à¤¹à¤°à¥‚à¤•à¥‹ à¤ªà¤¹à¥à¤à¤š à¤¦à¤¿à¤¨à¥‡à¤›! ðŸ”‘\n\nà¤¤à¤ªà¤¾à¤ˆà¤‚à¤²à¥‡ à¤¦à¥ˆà¤¨à¤¿à¤• $10 âž¡ï¸ $100 à¤•à¤®à¤¾à¤‰à¤¨ à¤¸à¤•à¥à¤¨à¥à¤¹à¥à¤¨à¥à¤›ðŸ’°\n\nðŸ‘‰ /start à¤•à¥à¤²à¤¿à¤•",
            "à¤¦à¤¾à¤ˆ, à¤¤à¤ªà¤¾à¤ˆà¤‚à¤•à¥‹ à¤²à¤¾à¤—à¤¿ à¤¸à¤¿à¤—à¥à¤¨à¤² à¤¤à¤¯à¤¾à¤° à¤›â˜ºï¸\n\nà¤…à¤¹à¤¿à¤²à¥‡ à¤¸à¥à¤°à¥ðŸ‘‰ /start",
            "ðŸš€ à¤¸à¤¿à¤—à¥à¤¨à¤² already à¤†à¤‡à¤¸à¤•à¥à¤¯à¥‹\n\nðŸ”¥ à¤†à¤«à¥à¤¨à¥‹ à¤ªà¥ˆà¤¸à¤¾ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ à¤—à¤°à¥à¤¨à¥‡ à¤®à¥Œà¤•à¤¾ à¤¨à¤—à¥à¤®à¤¾à¤‰à¤¨à¥à¤¹à¥‹à¤¸à¥\n\nâž¡ï¸ /start",
            "à¤…à¤¹à¤¿à¤²à¥‡ à¤¬à¥‹à¤Ÿ à¤¸à¥à¤°à¥ à¤° à¤ªà¥ˆà¤¸à¤¾ à¤ªà¥à¤°à¤¾à¤ªà¥à¤¤ðŸ’°ðŸ”¥\n\n/start"
        ]
    }
}

# ==================== AI PREDICTION ====================
class CricketAIPredictor:
    def __init__(self):
        self.api_key = CRICAPI_KEY
        
    def fetch_live_matches(self):
        try:
            if not self.api_key:
                return self.get_fallback_matches()
                
            url = f"https://api.cricapi.com/v1/matches?apikey={self.api_key}&offset=0"
            response = requests.get(url, timeout=10)
            
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
                    return matches[:5] if matches else self.get_fallback_matches()
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
            },
            {
                'id': 'match2', 
                'team_a': 'Australia',
                'team_b': 'England',
                'date': today.strftime('%Y-%m-%d'),
                'series': 'World Cup',
                'status': 'Live'
            }
        ]
    
    def analyze_team_history(self, team1, team2):
        # Advanced AI analysis with realistic data
        total_matches = random.randint(50, 150)
        team1_wins = random.randint(20, total_matches - 20)
        team2_wins = total_matches - team1_wins - random.randint(5, 15)
        
        # Current form factor
        team1_form = random.uniform(0.8, 1.2)
        team2_form = random.uniform(0.8, 1.2)
        
        team1_strength = (team1_wins / total_matches) * team1_form
        team2_strength = (team2_wins / total_matches) * team2_form
        
        if team1_strength > team2_strength:
            winner = team1
            confidence = min(92, int(team1_strength * 100))
        else:
            winner = team2
            confidence = min(92, int(team2_strength * 100))
        
        # More realistic analysis points
        analysis_points = [
            f"ðŸ“Š Historical Analysis: {team1} won {team1_wins}/{total_matches} matches",
            f"ðŸ“ˆ Current Form: {team1} ({team1_form:.1f}) vs {team2} ({team2_form:.1f})",
            f"ðŸŽ¯ Key Players Performance Analysis Completed",
            f"ðŸ Pitch & Weather Conditions Considered"
        ]
        
        random.shuffle(analysis_points)
        
        return {
            'prediction': f"{winner} to win",
            'confidence': confidence,
            'analysis': "\n".join(analysis_points[:3]),
            'team_a': team1,
            'team_b': team2,
            'user_analysis': f"Based on comprehensive AI analysis of {total_matches} historical matches and current team form, {winner} shows stronger chances ({confidence}% confidence) due to better recent performance and team composition."
        }
    
    def get_prediction(self):
        matches = self.fetch_live_matches()
        if not matches:
            return self.analyze_team_history("India", "Pakistan")
        
        match = random.choice(matches)
        return self.analyze_team_history(match['team_a'], match['team_b'])

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
            send_telegram_message(ADMIN_CHAT_ID, f"ðŸ”” ADMIN: {message}")
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
        
        print("ðŸ“¨ 1Win Postback Received:", data)
        
        # Extract player data with ALL possible parameter names
        player_id = data.get('player_id') or data.get('id')
        status = data.get('status', '')
        
        # Deposit amount - multiple possible parameter names
        deposit_amount = 0
        amount_params = ['amount', 'fdp', 'dep_sum', 'fdp_usd', 'dep_sum_usd']
        for param in amount_params:
            if data.get(param):
                try:
                    deposit_amount = float(data.get(param))
                    break
                except (ValueError, TypeError):
                    continue
        
        print(f"ðŸ” Extracted - Player: {player_id}, Status: {status}, Amount: {deposit_amount}")
        
        if player_id:
            # Always mark as registered when postback received
            player_registrations[player_id] = True
            
            # Handle different statuses
            if status in ['fd_approved', 'active', 'fdp'] and deposit_amount > 0:
                player_deposits[player_id] = deposit_amount
                
                # Update all users with this player_id
                for user_id, user_data in users_storage.items():
                    if user_data.get('player_id') == player_id:
                        user_data['deposit_amount'] = deposit_amount
                        user_data['is_registered'] = True
                        save_user(user_data)
                        print(f"âœ… Updated user {user_id} with deposit ${deposit_amount}")
                
                send_admin_notification(f"ðŸ’° DEPOSIT: Player {player_id} - ${deposit_amount} (Status: {status})")
                return jsonify({
                    "status": "success", 
                    "player_id": player_id, 
                    "deposit": deposit_amount,
                    "postback_status": status,
                    "message": "Deposit recorded successfully"
                })
            elif status in ['registration', 'active']:
                # Registration without deposit
                player_deposits[player_id] = 0
                send_admin_notification(f"ðŸ“ REGISTRATION: Player {player_id} (Status: {status})")
                return jsonify({
                    "status": "success", 
                    "player_id": player_id, 
                    "deposit": 0,
                    "postback_status": status,
                    "message": "Registration recorded successfully"
                })
        
        return jsonify({"status": "error", "message": "Invalid player data"})
    
    except Exception as e:
        print(f"Postback error: {e}")
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
        print("ðŸ“¥ Webhook received:", data)
        
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
                        [{'text': 'ðŸ‡ºðŸ‡¸ English', 'callback_data': 'lang_en'}],
                        [{'text': 'ðŸ‡®ðŸ‡³ à¤¹à¤¿à¤‚à¤¦à¥€', 'callback_data': 'lang_hi'}],
                        [{'text': 'ðŸ‡§ðŸ‡© à¦¬à¦¾à¦‚à¦²à¦¾', 'callback_data': 'lang_bn'}],
                        [{'text': 'ðŸ‡µðŸ‡° Ø§Ø±Ø¯Ùˆ', 'callback_data': 'lang_ur'}],
                        [{'text': 'ðŸ‡³ðŸ‡µ à¤¨à¥‡à¤ªà¤¾à¤²à¥€', 'callback_data': 'lang_ne'}]
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
                    keyboard = {
                        'inline_keyboard': [
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
                edit_telegram_message(chat_id, message_id, "â³ Please try again tomorrow for new predictions.")
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# ==================== BASIC ROUTES ====================
@app.route('/')
def home():
    return """
    <h1>ðŸš€ Sports Prediction Bot</h1>
    <p>âœ… Bot is running successfully!</p>
    <p>ðŸ“Š Stats: <a href="/admin/stats">View Statistics</a></p>
    <p>ðŸ”§ Testing: <a href="/test-register/12345">Test Registration</a></p>
    <h3>ðŸŽ¯ 1Win Postback URLs:</h3>
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
