import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Define the bot token and webhook URL
BOT_TOKEN = os.environ.get("6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw")
WEBHOOK_URL = "https://telegrambot-dvnr.onrender.com/webhook"

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot has been started")

# Function to handle the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I can respond to messages and echo them back! Try sending me something.")

# Function to handle all text messages (echoes them back)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# Set the webhook to the desired URL
def set_webhook():
    webhook_url = f"https://api.telegram.org/bot6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(webhook_url)
    print(f"Webhook set response: {response.json()}")

# Main function to run the bot
def main():
    # Set the webhook before starting the bot
    set_webhook()

    # Initialize the bot application
    application = Application.builder().token("6227369198:AAHgS6-0A8tJaSRLrgE1gaq4z93AEbB-SMw").build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Register a message handler to echo all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
