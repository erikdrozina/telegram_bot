import json
import logging
import requests
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

#   enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

#   needed for /covid_info conversation
COUNTRY = range(1)

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
            context.bot.send_message(chat_id=update.effective_chat.id, text='Covid stats for: '+jres['response'][0]['country']+', '+jres['response'][0]['continent']+' as '+jres['response'][0]['day']+'\n\nNew Cases: '+jres['response'][0]['cases']['new'].replace('+', '')+'\nActive Cases:'+str(jres['response'][0]['cases']['active'])+'\nCritical Cases: '+str(jres['response'][0]['cases']['critical'])+'\nTotal Recovered: '+str(jres['response'][0]['cases']['recovered'])+'\n\nNew Deaths: '+jres['response'][0]['deaths']['new'].replace('+','')+'\nTotal Deaths: '+str(jres['response'][0]['deaths']['total']))
            logger.info('User %s ENDED /covid_info searching "%s" with success', user.name, var_country)
        except:
            update.message.reply_text("Sorry, The selected country has issue with their data\nTry another coutry")
            logger.info('User %s ENDED /covid_info searching "%s" with error', user.name, var_country)
    else:
        update.message.reply_text('No result found, sowwy sar :(')
        logger.info('User %s ENDED /covid_info searching "%s" with error', user.name, var_country)

    return ConversationHandler.END

def cancel_covid(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text('OK, nevermind :)', reply_markup=ReplyKeyboardRemove())
    logger.info('User %s STOPPED /covid_info', user.name)
    return ConversationHandler.END

covid_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('covid_info', covid_inf)],
        states={
            COUNTRY: [MessageHandler(Filters.text & ~Filters.command, country)]
        },
        fallbacks=[CommandHandler('cancel', cancel_covid)],
    )
