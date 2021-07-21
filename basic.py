import logging
from typing import List
from telegram import Update
from telegram.ext import CallbackContext

#   enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

#   respond to /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info('User %s started /start', user.name)
    user = update.effective_user
    update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}, How can I help you?')
    update.message.reply_text('Type /help to view all available commands')

#   respond to /help
def help_command(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info('User %s started /help', user.name)
    update.message.reply_text('List of commands: \n\n- help\n- doggo\n- covid_info\n- msg\n- kang')

#   respond to an unknown command
def unknown(update: Update, context: CallbackContext)-> None:
    user = update.message.from_user
    logger.info('User %s started unknow command: %s', user.name, update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command\nMe bot, me no pero like u :(')