import yaml
import json
import logging
import requests
from doggo import doggoF
from pathlib import Path
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

#   retrive the bot token from the token.yaml file
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

#   needed for /covid_info conversation
COUNTRY = range(1)

#   needed for /msg conversation
ID, MESSAGE = range(2)

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
    update.message.reply_text('List of commands: \n\n- help\n- doggo\n- covid_info\n- msg')

#   respond to an unknown command
def unknown(update: Update, context: CallbackContext)-> None:
    user = update.message.from_user
    logger.info('User %s started unknow command: %s', user.name, update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command\nMe bot, me no pero like u :(')

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
        logger.info('Message: %s sent to user id %s', send_msg.msg, get_id.id)
        update.message.reply_text('Message sent')
        logger.info('User %s ENDED /msg with success', user.name)
    except:
        logger.info('Message: %s NOT sent to user id %s', send_msg.msg, get_id.id)
        update.message.reply_text('Couldn\'t send the message\nThe user must start the bot or the chat id was wrong')
        logger.info('User %s ENDED /msg with error', user.name)
    return ConversationHandler.END

def cancel_msg(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text('OK, nevermind :)', reply_markup=ReplyKeyboardRemove())
    logger.info('User %s STOPPED /msg', user.name)
    return ConversationHandler.END

########################### COVID INFO ###########################

def covid_url(countryname):
    url = "https://covid-193.p.rapidapi.com/statistics"
    querystring = {"country": countryname}

    headers = {
    'x-rapidapi-key': "0e312021bdmsha51edbc7e3eab41p124c7ajsn40c907167716",
    'x-rapidapi-host': "covid-193.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text

def covid_inf(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info('User %s started /covid_info', user.name)
    update.message.reply_text('Name of the country\n\nType /cancel to exit')
    return COUNTRY

def country(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    var_country = update.message.text
    logger.info('Country: %s by %s', var_country, user.name)
    update.message.reply_text('Loading data...')
    response = covid_url(var_country)
    if response != '{"get":"statistics","parameters":{"country":"'+var_country+'"},"errors":[],"results":0,"response":[]}':
        jres = json.loads(response)
        try:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Covid stats for: '+jres['response'][0]['country']+', '+jres['response'][0]['continent']+' as '+jres['response'][0]['day']+'\n\nNew Cases: '+jres['response'][0]['cases']['new'].replace('+', '')+'\nActive Cases:'+str(jres['response'][0]['cases']['active'])+'\nCritical Cases: '+str(jres['response'][0]['cases']['critical'])+'\nTotal Recovered: '+str(jres['response'][0]['cases']['recovered'])+'\n\nNew Deaths: '+jres['response'][0]['deaths']['new'].replace('+','')+'\nTtoal Deaths: '+str(jres['response'][0]['deaths']['total']))
            logger.info('User %s ENDED /covid_info searching "%s with success"', user.name, var_country)
        except:
            update.message.reply_text("Sorry, The selected country has issue with their data\nTry another coutry")
            logger.info('User %s ENDED /covid_info searching "%s with error"', user.name, var_country)
    else:
        update.message.reply_text('No result found, sowwy sar :(')
        logger.info('User %s ENDED /covid_info searching "%s with error"', user.name, var_country)

    return ConversationHandler.END

def cancel_covid(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text('OK, nevermind :)', reply_markup=ReplyKeyboardRemove())
    logger.info('User %s STOPPED /covid_info', user.name)
    return ConversationHandler.END

############################## MAIN ##############################

def main():
    print('Bot Started!\n')
    print('Bot link: http://t.me/erikd_test_bot\n\n')

    covid_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('covid_info', covid_inf)],
        states={
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country)]
        },
        fallbacks=[CommandHandler('cancel', cancel_covid)],
    )

    msg_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('msg', get_id)],
        states={
            ID: [MessageHandler(Filters.text & ~Filters.command, get_msg)],
            MESSAGE: [MessageHandler(Filters.text & ~Filters.command, send_msg)],
        },
        fallbacks=[CommandHandler('cancel', cancel_msg)],
    )
    updater = Updater(get_token(), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help_command))
    dp.add_handler(CommandHandler('doggo',doggoF))
    dp.add_handler(covid_conv_handler)
    dp.add_handler(msg_conv_handler)
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()

#   start
if __name__ == '__main__':
    main()
