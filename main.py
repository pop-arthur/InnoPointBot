import datetime
from typing import Final

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, Updater
import json

from parser import Parser

TOKEN: Final = "6795680740:AAFYO-89HJSZU3TvARdDQyv5snvafTgaXjA"
BOT_USERNAME: Final = "@InnoVolunteerBot"
BOT_NAME: Final = "Inno Volunteer Bot"


# Commands
async def start_command(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    with open("chats.json", "r") as file:
        data = json.loads(file.read())
    if str(update.message.chat.id) not in data:
        data.append(str(update.message.chat.id))
    with open("chats.json", "w") as file:
        file.write(json.dumps(data, indent=4))

    await update.message.reply_text("Now you will get notifications about new volunteer events in Innopolis!")


async def help_command(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""You can use following commands:
    /start
    /help""")


async def get_current_events_command(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(parser.get_events_to_str(parser.get_current_events()))


# Responses
def handle_response(text: str) -> str:
    return "Please, use commands"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print(f"Bot: {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


async def check_updates(context: CallbackContext):
    print(f"Processing at {datetime.datetime.now()}...")
    response = parser.get_updates()
    if response == "No new events":
        return

    with open("chats.json", "r") as file:
        chats = json.loads(file.read())

    for chat in chats:
        await bot.sendMessage(chat, response)


if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()
    bot = telegram.Bot(TOKEN)

    # Parser
    parser = Parser()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('get_current_events', get_current_events_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Schedule
    job_queue = app.job_queue
    job_queue.run_repeating(check_updates, 60 * 60, first=0)

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=3)
