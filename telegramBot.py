import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define a function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your Telegram bot.')

# Define a function to handle the /help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('I am here to help you.')

# Main function to set up the bot
def main():
    # Replace with your actual Telegram Bot API token
    bot_token = '7256270773:AAEqR_2IJFCj9nvLZWvIWlOe-BEQrR7-rT0'
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the webhook to listen for messages
    updater.start_webhook(listen='0.0.0.0',
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=bot_token,
                          webhook_url=f'https://telegrambot-dvnr.onrender.com/{bot_token}')

    updater.idle()

if __name__ == '__main__':
    main()
