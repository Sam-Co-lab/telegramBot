import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)

# Define bot token and webhook URL
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_URL')}/webhook"

# Function to handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot has been started")

# Function to handle /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I can respond to messages and echo them back! Try sending me something.")

# Function to echo all text messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# Set webhook to Render URL
def set_webhook():
    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(webhook_url)
    print(f"Webhook set response: {response.json()}")

# Define Flask route to handle webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, application.bot)
    application.update_queue.put(update)
    return "OK", 200

# Main function to run the bot
def main():
    # Set webhook
    set_webhook()

    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Register message handler to echo text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start polling and webhook on the same app
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 10000)), url_path='webhook')

if __name__ == "__main__":
    main()
