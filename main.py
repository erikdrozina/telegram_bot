import yaml
import logging
from doggo import doggoF
from pathlib import Path
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def get_token():
    full_file_path = Path(__file__).parent.joinpath('token.yaml')
    with open(full_file_path) as token:
        token_data = yaml.load(token, Loader=yaml.Loader)
    return token_data

#   enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

########################### BASIC COMM ###########################

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
    update.message.reply_text('List of commands: \n\n- help\n- doggo')

def main():
    print('Bot Started!\n')
    print('Bot link: http://t.me/erikd_test_bot\n\n')

    updater = Updater(get_token(), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help_command))
    dp.add_handler(CommandHandler('doggo',doggoF))

    updater.start_polling()
    updater.idle()

#   start
if __name__ == '__main__':
    main()
