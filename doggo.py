from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import requests
import re

#   enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

#   get the doggo image API
def dogg_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']

        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

#   respond to /doggo
def doggoF(update, context):
    user = update.message.from_user
    logger.info('User %s started /doggo', user.name)
    url = dogg_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)