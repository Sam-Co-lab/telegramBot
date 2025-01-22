from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import os

# Flask app for webhook
app = Flask(__name__)

# Replace with your bot token from BotFather
BOT_TOKEN = os.environ.get("6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw")  # Use environment variable for security
WEBHOOK_URL = "https://telegrambot-dvnr.onrender.com/webhook"  # Replace with your Render URL

# Create the bot application
application = Application.builder().token("6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw").build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot has been started. How can I help you?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I can echo your messages. Try typing something!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Webhook route for Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Route to set the webhook
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    application.bot.set_webhook(WEBHOOK_URL)
    return "Webhook set!", 200

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port or default to 5000
    app.run(host="0.0.0.0", port=port)
