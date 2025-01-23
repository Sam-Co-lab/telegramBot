from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
import logging

# Replace with your bot token
BOT_TOKEN = "6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

# Command handler function
async def start(update: Update, context):
    try:
        logger.info(f"Received /start command from user {update.effective_user.id}")
        await update.message.reply_text("Hello! I am your Telegram bot. How can I help you?")
    except Exception as e:
        logger.error(f"Error in /start handler: {e}")

# Add handler to application
application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates."""
    if request.method == "POST":
        try:
            # Get the incoming update
            json_update = request.get_json()
            logger.info(f"Incoming update: {json_update}")

            # Convert JSON to Update object
            update = Update.de_json(json_update, application.bot)

            # Process the update
            application.update_queue.put_nowait(update)
        except Exception as e:
            logger.error(f"Error processing update: {e}")
        return "OK", 200

if __name__ == "__main__":
    try:
        # Set the webhook URL
        webhook_url = "https://telegrambot-dvnr.onrender.com/webhook"
        application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook successfully set to {webhook_url}")

        # Run the Flask app
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")
