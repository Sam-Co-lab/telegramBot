from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# Replace with your bot token
BOT_TOKEN = "6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw"

# Flask app
app = Flask(__name__)

# Telegram Bot
bot = Bot(token=BOT_TOKEN)

# Dispatcher to handle bot updates
dispatcher = Dispatcher(bot, None, use_context=True)

# Command handler function
def start(update: Update, context):
    update.message.reply_text("Hello! I am your Telegram bot. How can I help you?")

# Add handler to dispatcher
dispatcher.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200

if __name__ == "__main__":
    # Set the webhook URL
    webhook_url = "https://telegrambot-dvnr.onrender.com/webhook"
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
