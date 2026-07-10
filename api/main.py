import os
import logging
import requests
from flask import Flask, request, jsonify
import telebot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENHANDS_API_KEY = os.getenv('OPENHANDS_API_KEY')
OPENHANDS_BASE_URL = os.getenv('OPENHANDS_BASE_URL', 'https://app.all-hands.dev')

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- Telegram Bot Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome to Open-hand Bot!\n\n"
        f"Your Chat ID is: `{message.chat.id}`\n\n"
        "Commands:\n"
        "/list - List your OpenHands conversations\n"
        "/help - Show this message"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['list'])
def list_conversations(message):
    if not OPENHANDS_API_KEY:
        bot.reply_to(message, "❌ OpenHands API Key is not set in Vercel environment variables.")
        return

    try:
        headers = {'X-Session-API-Key': OPENHANDS_API_KEY}
        response = requests.get(f"{OPENHANDS_BASE_URL}/api/v1/app-conversations", headers=headers)
        
        if response.status_code == 200:
            conversations = response.json()
            if not conversations:
                bot.reply_to(message, "📭 No conversations found.")
                return
            
            text = "📂 *Your OpenHands Conversations:*\n\n"
            # Adjust based on actual API response structure if needed
            items = conversations if isinstance(conversations, list) else conversations.get('results', [])
            
            for conv in items[:10]:
                title = conv.get('title', 'Untitled')
                conv_id = conv.get('id', 'N/A')
                status = conv.get('status', 'unknown')
                text += f"• *{title}*\n  ID: `{conv_id}`\n  Status: {status}\n\n"
            
            bot.reply_to(message, text, parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ Failed to fetch conversations. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

@bot.message_handler(commands=['help'])
def send_help(message):
    send_welcome(message)

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    return "OpenHands Notification Bot is active!", 200

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        if update and (update.message or update.callback_query):
            bot.process_new_updates([update])
            return '', 200
        
        data = request.json
        if data and 'message' in data:
            msg = data.get('message', 'OpenHands task finished!')
            cid = data.get('chat_id')
            if cid:
                try:
                    bot.send_message(cid, msg)
                    return jsonify({"status": "success"}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            return jsonify({"error": "chat_id required"}), 400

    return "Invalid request", 400

# Vercel needs 'app'
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
