import os
import logging
from flask import Flask, request, jsonify
import telebot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Default CHAT_ID can be set in environment variables
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "OpenHands Notification Bot is running! Use /webhook to send notifications.", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint for OpenHands or other services to send notifications.
    Expected JSON: {"message": "Task finished!", "chat_id": "optional_id"}
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    message = data.get('message', 'OpenHands task finished!')
    target_chat_id = data.get('chat_id', CHAT_ID)
    
    if not target_chat_id:
        return jsonify({"error": "No chat_id provided and no default TELEGRAM_CHAT_ID set"}), 400
    
    try:
        bot.send_message(target_chat_id, message)
        logger.info(f"Notification sent to {target_chat_id}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": str(e)}), 500

# Vercel needs the 'app' object to be available at the module level.
# This block is for local testing.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
