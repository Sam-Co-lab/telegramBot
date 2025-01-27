import os
import time
import re
import requests
import base64
import pickle
from telegram import Update, Bot, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import BadRequest

GITHUB_TOKEN = os.environ.get('GitAccToken')
REPO_OWNER = "Sam-Co-lab"
REPO_NAME = "Data"
FILE_PATH = "blocked.pkl"


# Dictionary to store blocked words for each chat
blocked_words = {}
def update_blocked(new_data):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    
    # Get the current file content and its SHA
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    print("GET response status code:", response.status_code)  # Debug print
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info["sha"]
        print("Current SHA:", sha)  # Debug print
    else:
        print("Failed to fetch file info:", response.status_code, response.json())
        return
    
    # Encode the new data to Base64
    new_content = base64.b64encode(pickle.dumps(new_data)).decode("utf-8")
    print("Encoded new content:", new_content)  # Debug print
    
    # Prepare the request payload
    payload = {
        "message": "Updated blocked.pkl",
        "content": new_content,
        "sha": sha,  # Required to update the file
        "branch": "main"
    }
    print("Payload:", payload)  # Debug print
    
    # Make the PUT request to update the file
    response = requests.put(url, json=payload, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    print("PUT response status code:", response.status_code)  # Debug print
    if response.status_code == 200:
        print("File updated successfully!")
    else:
        print("Failed to update file:", response.status_code, response.json())

# Ensure read_blocked function updates the global blocked_words variable correctly
def read_blocked():
    global blocked_words
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    
    # Get the current file content
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    print("GET response status code (read_blocked):", response.status_code)  # Debug print
    if response.status_code == 200:
        file_info = response.json()
        encoded_content = file_info["content"]
        print("Encoded content fetched:", encoded_content)  # Debug print
        file_content = base64.b64decode(encoded_content)  # Decode Base64 content
        try:
            blocked_words = pickle.loads(file_content)  # Unpickle the data
            print("Blocked words (read_blocked):", blocked_words)  # Debug print
        except pickle.UnpicklingError as e:
            print("UnpicklingError:", e)  # Debug print
            blocked_words = {}
    else:
        print("Failed to fetch file info:", response.status_code, response.json())

    return blocked_words  # Ensure to return the blocked_words dictionary

# Function to delete specific messages
def delete_messages(context: CallbackContext, chat_id: int) -> None:
    try:
        if 'mess_to_del' in context.user_data:
            context.bot.delete_message(chat_id, context.user_data['mess_to_del'])
        if 'tagged_message_id' in context.user_data:
            context.bot.delete_message(chat_id, context.user_data['tagged_message_id'])
    except BadRequest as e:
        print(f"BadRequest error while deleting messages: {e.message}")

# Function to show blocked words
def show_blocked_words(update: Update, context: CallbackContext) -> None:
    blocked_words = read_blocked()
    chat_id = update.effective_chat.id
    if chat_id in blocked_words:
        update.message.reply_text(str(blocked_words[chat_id])[1:-1])
    else:
        update.message.reply_text("No word blacklisted YET...")



# Function to ask admin for blocked words
def set_blocked_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    context.user_data['mess_to_del'] = update.message.message_id
    if update.effective_chat.get_member(user_id).status in ['administrator', 'creator']:
        reply_message = update.message.reply_text('Please send the words to be blacklisted, separated by commas.')
        context.user_data['waiting_for_words'] = True
        context.user_data['reply_mess_to_del'] = reply_message.message_id
        context.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, update_blocked_words), group=1)
    else:
        update.message.reply_text('Only admins can blacklist words.')

# Function to update blocked words
def update_blocked_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    if context.user_data.get('waiting_for_words'):
        words = update.message.text.lower().split(',')
        words = [word.strip() for word in words]  # Ensure words are stripped of spaces
        context.bot.delete_message(chat_id, message_id)
        
        blocked_words = read_blocked()
        
        if chat_id not in blocked_words:
            blocked_words[chat_id] = words
        else:
            blocked_words[chat_id].extend(words)

        mess_to_del = context.user_data.get('mess_to_del')
        reply_mess_to_del = context.user_data.get('reply_mess_to_del')
        if mess_to_del:
            context.bot.delete_message(chat_id, mess_to_del)
            context.user_data['mess_to_del'] = None
        if reply_mess_to_del:
            context.bot.delete_message(chat_id, reply_mess_to_del)
            context.user_data['reply_mess_to_del'] = None

        update_blocked(blocked_words)

        try:
            update.message.reply_text(f'Blacklisted words: {", ".join(blocked_words[chat_id])}')
        except BadRequest as e:
            print(f"BadRequest error: {e.message}")

        print(f'Admin set blocked words: {blocked_words[chat_id]} in chat {chat_id}')
    context.user_data['waiting_for_words'] = False
    context.dispatcher.remove_handler(MessageHandler, group=1)

# Function to ask admin for blocked words to remove
def remove_blocked_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    context.user_data['mess_to_del'] = update.message.message_id
    if update.effective_chat.get_member(user_id).status in ['administrator', 'creator']:
        reply_message = update.message.reply_text('Please send the words to be unblocked, separated by commas.')
        context.user_data['waiting_for_words'] = True
        context.user_data['reply_mess_to_del'] = reply_message.message_id
        context.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, rupdate_blocked_words), group=1)
    else:
        update.message.reply_text('Only admins can unblock words.')

# Function to update blocked words by removing them
def rupdate_blocked_words(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    if context.user_data.get('waiting_for_words'):
        words = update.message.text.lower().split(',')
        words = [word.strip() for word in words]
        context.bot.delete_message(chat_id, message_id)
        
        blocked_words = read_blocked()
        
        if chat_id not in blocked_words:
            update.message.reply_text('No words blocked yet!')
        else:
            blocked_words[chat_id] = [word for word in blocked_words[chat_id] if word not in words]

        mess_to_del = context.user_data.get('mess_to_del')
        reply_mess_to_del = context.user_data.get('reply_mess_to_del')
        if mess_to_del:
            context.bot.delete_message(chat_id, mess_to_del)
            context.user_data['mess_to_del'] = None
        if reply_mess_to_del:
            context.bot.delete_message(chat_id, reply_mess_to_del)
            context.user_data['reply_mess_to_del'] = None

        update_blocked(blocked_words)

        try:
            update.message.reply_text(f'Updated blocked words: {", ".join(blocked_words.get(chat_id, []))}')
        except BadRequest as e:
            print(f"BadRequest error: {e.message}")

        print(f'Admin updated blocked words: {blocked_words[chat_id]} in chat {chat_id}')
    context.user_data['waiting_for_words'] = False
    context.dispatcher.remove_handler(MessageHandler, group=1)

# Function to monitor messages and block users
def monitor_chats(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message_text = update.message.text.lower()
    message_id = update.message.message_id

    blocked_words = read_blocked()

    permission = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False)

    # Check for blocked words
    if chat_id in blocked_words:
        for word in blocked_words[chat_id]:
            if word in message_text:
                member_status = context.bot.get_chat_member(chat_id, user_id).status
                if member_status in ['administrator', 'creator']:
                    return  # Ignore words used by administrator or creator
                context.bot.restrict_chat_member(chat_id, user_id, permissions=permission, until_date=time.time() + 300)
                context.bot.delete_message(chat_id, message_id)
                update.message.reply_text(f'User {update.effective_user.first_name} has been blocked for using a blacklisted word')
                print(f'User {user_id} blocked for using a black-listed word in chat {chat_id}')
                return

    # Check for links
    if 'http://' in message_text or 'https://' in message_text:
        member_status = context.bot.get_chat_member(chat_id, user_id).status
        if member_status in ['administrator', 'creator']:
            return  # Ignore links shared by administrator or creator
        context.bot.restrict_chat_member(chat_id, user_id, permissions=permission, until_date=time.time() + 300)
        update.message.reply_text(f'User {update.effective_user.first_name} has been blocked for sharing a link.')
        print(f'User {user_id} blocked for sharing a link in chat {chat_id}')

# Define a function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! \nI am LISA, your group manager bot.', allow_sending_without_reply=True)

# Define a function to handle the /help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('For any complaints or reports, contact developer')

# Main function to set up the bot
def main():
    # Replace with your actual Telegram Bot API token
    bot_token = '7256270773:AAGccvp6zUWHQaLzcaJKM6oYCGNnqebuHU0'
    updater = Updater(bot_token)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("blockwords", set_blocked_words))
    dispatcher.add_handler(CommandHandler("showblockedwords", show_blocked_words))
    dispatcher.add_handler(CommandHandler("unblockwords", remove_blocked_words))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, monitor_chats))

    # Start the webhook to listen for messages
    updater.start_webhook(listen='0.0.0.0',
                          port=int(os.environ.get('PORT', 5000)),
                          url_path=bot_token,
                          webhook_url=f'https://telegrambot-msio.onrender.com/{bot_token}')

    updater.idle()

if __name__ == '__main__':
    main()
