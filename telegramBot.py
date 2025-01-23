import os
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Dictionary to store blocked words for each chat
blocked_words = {}

# Function to ask admin for blocked words
def set_blocked_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if update.effective_chat.get_member(user_id).status in ['administrator', 'creator']:
        update.message.reply_text('Please enter the words to block, separated by commas:')
        context.user_data['awaiting_words'] = True  # Set a flag to indicate awaiting words
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    else:
        update.message.reply_text('Only admins can set blocked words.')

# Custom filter function to check if awaiting words
def filter_awaiting_words(message):
    return message.from_user.id in message.bot_data.get('awaiting_words', [])

# Function to handle incoming messages for blocked words
def handle_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if context.user_data.get('awaiting_words'):
        words = update.message.text.split(',')
        blocked_words[chat_id] = [word.strip().lower() for word in words]
        update.message.reply_text(f'Blocked words set: {", ".join(blocked_words[chat_id])}')
        context.user_data['awaiting_words'] = False  # Reset the flag
        print(f'Admin set blocked words: {blocked_words[chat_id]} in chat {chat_id}')
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

# Function to monitor messages and block users
def monitor_chats(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    # Check for blocked words
    if chat_id in blocked_words:
        for word in blocked_words[chat_id]:
            if word in message_text:
                context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
                context.bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 7200, can_send_messages=False)
                context.bot.send_message(chat_id=chat_id, text=f'User {update.effective_user.first_name} has been blocked for 2 hours for using a blocked word: {word}')
                print(f'User {user_id} blocked for using word: {word} in chat {chat_id}')
                return

    # Check for links
    if 'http://' in message_text or 'https://' in message_text:
        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        context.bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 7200, can_send_messages=False)
        context.bot.send_message(chat_id=chat_id, text=f'User {update.effective_user.first_name} has been blocked for 2 hours for sharing a link.')
        print(f'User {user_id} blocked for sharing a link in chat {chat_id}')

# Define a function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your Telegram bot.')

# Define a function to handle the /help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('I am here to help you.')

# Main function to set up the bot
def main():
    # Replace with your actual Telegram Bot API token
    bot_token = '7256270773:AAGccvp6zUWHQaLzcaJKM6oYCGNnqebuHU0'
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setblockedwords", set_blocked_words))
    dispatcher.add_handler(MessageHandler(Filters.text & filter_awaiting_words, handle_words))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, monitor_chats))

    # Start the webhook to listen for messages
    updater.start_webhook(listen='0.0.0.0',
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=bot_token,
                          webhook_url=f'https://telegrambot-dvnr.onrender.com/{bot_token}')

    updater.idle()

if __name__ == '__main__':
    main()
