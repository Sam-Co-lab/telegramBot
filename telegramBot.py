from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler

# Replace with your bot token
BOT_TOKEN = "6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw"

# Flask app
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

# Command handler function
async def start(update: Update, context):
    await update.message.reply_text("Hello! I am your Telegram bot. How can I help you?")

# Add handler to application
application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates."""
    if request.method == "POST":
        json_update = request.get_json()
        update = Update.de_json(json_update, application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200

if __name__ == "__main__":
    # Set the webhook URL
    webhook_url = "https://telegrambot-dvnr.onrender.com/webhook"
    application.bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
