import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler

#   enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

#   needed for /msg conversation
ID, MESSAGE = range(2)

########################## SEND MESSAGE ##########################

def get_id(update: Update, context: CallbackContext)-> int:
    user = update.message.from_user
    logger.info('User %s started /msg', user.name)
    update.message.reply_text("Send the chat ID you want to send the message to\n\nType /cancel to exit")
    return ID

def get_msg(update: Update, context: CallbackContext)-> int:
    user = update.message.from_user
    txt = update.message.text
    logger.info('Chat id: %s by %s', txt, user.name)
    get_id.id = txt
    update.message.reply_text("Send the message you want to send\n\nType /cancel to exit")
    return MESSAGE

def send_msg(update: Update, context: CallbackContext)-> int:
    user = update.message.from_user
    txt = update.message.text    
    logger.info('Message: %s by %s', txt, user.name)
    send_msg.msg = txt
    try:
        context.bot.send_message(chat_id=get_id.id, text=send_msg.msg)
        logger.info('Message sent to user id %s', get_id.id)
        update.message.reply_text('Message sent')
        logger.info('User %s ENDED /msg with success', user.name)
    except:
        logger.info('Message NOT sent to user id %s', get_id.id)
        update.message.reply_text('Couldn\'t send the message\nThe user must start the bot or the chat id was wrong')
        logger.info('User %s ENDED /msg with error', user.name)
    return ConversationHandler.END

def cancel_msg(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text('OK, nevermind :)', reply_markup=ReplyKeyboardRemove())
    logger.info('User %s STOPPED /msg', user.name)
    return ConversationHandler.END


msg_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('msg', get_id)],
        states={
            ID: [MessageHandler(Filters.text & ~Filters.command, get_msg)],
            MESSAGE: [MessageHandler(Filters.text & ~Filters.command, send_msg)],
        },
        fallbacks=[CommandHandler('cancel', cancel_msg)],
    )