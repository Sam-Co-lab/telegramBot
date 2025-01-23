import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info(f"Received /start command from user {update.effective_user.id}")
        await update.message.reply_text("Hello! I am your Telegram bot. How can I help you?")
    except Exception as e:
        logger.error(f"Error in /start handler: {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_message = update.message.text
        logger.info(f"User said: {user_message}")
        await update.message.reply_text(f"You said: {user_message}")
    except Exception as e:
        logger.error(f"Error in echo handler: {e}")

# Add handlers to application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

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

            # Schedule the update processing asynchronously
            asyncio.create_task(application.update_queue.put(update))

            logger.info(f"Update added to queue for user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Error processing update: {e}")
        return "OK", 200

def run_flask():
    """Run the Flask application."""
    app.run(host="0.0.0.0", port=5000)

async def main():
    """Set up the bot and webhook."""
    try:
        # Set the webhook URL
        webhook_url = "https://telegrambot-dvnr.onrender.com/webhook"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook successfully set to {webhook_url}")

        # Start the Flask app in a separate thread
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, run_flask)

        # Initialize and run the bot application
        await application.initialize()
        await application.start()
    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
