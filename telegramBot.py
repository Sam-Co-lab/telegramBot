from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, Dispatcher

# Flask app for the webhook
app = Flask(__name__)

with open('cred.txt', 'r') as f:
    token = f.read()
    f.close()

# Replace with your bot token
BOT_TOKEN = token
WEBHOOK_URL = "https://your-render-url.onrender.com/webhook"  # Replace with your Render URL

# Initialize the Telegram Bot application
application = Application.builder().token(BOT_TOKEN).build()

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your webhook-based bot.")

# Define the /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I respond to /start and /help commands. Try sending me something!")

# Define a message handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")

# Set up the command and message handlers
dispatcher = Dispatcher(application.bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Webhook endpoint for Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    dispatcher.process_update(update)
    return "OK", 200

# Main function to set the webhook
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    application.bot.set_webhook(WEBHOOK_URL)
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
