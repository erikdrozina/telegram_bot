import os
import math
import yaml
import json
import logging
import requests
from doggo import doggoF
from pathlib import Path
from PIL import Image
from typing import List
from telegram import Update, ReplyKeyboardRemove, TelegramError, ParseMode, Bot, InlineKeyboardMarkup, InlineKeyboardButton
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
    update.message.reply_text('List of commands: \n\n- help\n- doggo\n- covid_info\n- msg\n- kang')

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

############################## KANG ##############################

def kang(update: Update, context: CallbackContext) -> int:
    bot = context.bot
    msg= update.message
    user = update.effective_user
    usermsg = update.message.from_user
    packnum = 0
    packname = "a" + str(user.id) + "_by_"+bot.username
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    packname = "a" + str(packnum) + "_" + str(user.id) + "_by_"+bot.username
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1
    kangsticker = "kangsticker.png"
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yea, I can't kang that.")
        kang_file = bot.get_file(file_id)
        kang_file.download('kangsticker.png')
        sticker_emoji = "🤔"
        try:
            im = Image.open(kangsticker)
            maxsize = (512, 512)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512/size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512/size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                im.thumbnail(maxsize)
            if not msg.reply_to_message.sticker:
                im.save(kangsticker, "PNG")
            bot.add_sticker_to_set(user_id=user.id, name=packname,
                                    png_sticker=open('kangsticker.png', 'rb'), emojis=sticker_emoji)
            msg.reply_text(f"Sticker successfully added to [pack](t.me/addstickers/{packname})", parse_mode=ParseMode.MARKDOWN)
            logger.info('User %s ENDED /kang with success', usermsg.name)
        except OSError as e:
            msg.reply_text("I can only kang images m8.")
            logger.info('User %s ENDED /kang with error', usermsg.name)
            print(e)
            return
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                makepack_internal(msg, user, open('kangsticker.png', 'rb'), sticker_emoji, bot, packname, packnum)
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "PNG")
                bot.add_sticker_to_set(user_id=user.id, name=packname,
                                        png_sticker=open('kangsticker.png', 'rb'), emojis=sticker_emoji)
                msg.reply_text(f"Sticker successfully added to [pack](t.me/addstickers/{packname})", parse_mode=ParseMode.MARKDOWN)
                logger.info('User %s ENDED /kang with success', usermsg.name)
            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")
                logger.info('User %s ENDED /kang with error', usermsg.name)
            elif e.message == "Stickers_too_much":
                msg.reply_text("Max packsize reached. Press F to pay respecc.")
                logger.info('User %s ENDED /kang with error', usermsg.name)
            elif e.message == "Internal Server Error: sticker set not found (500)":
                msg.reply_text("Sticker successfully added to [pack](t.me/addstickers/%s)" % packname, parse_mode=ParseMode.MARKDOWN)
                logger.info('User %s ENDED /kang with success', usermsg.name)
            print(e)
    else:
        packs = "Please reply to a sticker, or image to kang it!\nOh, by the way. here are your packs:\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + "_by_"+bot.username
            for i in range(0, packnum + 1):
                if i == 0:
                    packs += f"[pack](t.me/addstickers/{firstpackname})\n"
                else:
                    packs += f"[pack{i}](t.me/addstickers/{packname})\n"
        else:
            packs += f"[pack](t.me/addstickers/{packname})"
        msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)
    if os.path.isfile("kangsticker.png"):
        os.remove("kangsticker.png")

def makepack_internal(msg, user, png_sticker, emoji, bot, packname, packnum):
    name = user.first_name
    name = name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        success = bot.create_new_sticker_set(user.id, packname, f"{name}s kang pack" + extra_version,
                                             png_sticker=png_sticker,
                                             emojis=emoji)
    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            msg.reply_text("Your pack can be found [here](t.me/addstickers/%s)" % packname,
                           parse_mode=ParseMode.MARKDOWN)
        elif e.message == "Peer_id_invalid":
            msg.reply_text("Contact me in PM first.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                text="Start", url=f"t.me/{bot.username}")]]))
        elif e.message == "Internal Server Error: created sticker set not found (500)":
                msg.reply_text("Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname,
                       parse_mode=ParseMode.MARKDOWN)
        return

    if success:
        msg.reply_text("Sticker pack successfully created. Get it [here](t.me/addstickers/%s)" % packname,
                       parse_mode=ParseMode.MARKDOWN)
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")

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
    dp.add_handler(CommandHandler('kang', kang))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()

#   start
if __name__ == '__main__':
    main()
