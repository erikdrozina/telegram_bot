import yaml
from doggo import doggoF
from basic import start, help_command, unknown
from msg import msg_conv_handler
from covid import covid_conv_handler
from kang import kang
from pathlib import Path
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#   retrive the bot token from the token.yaml file
def get_token():
    full_file_path = Path(__file__).parent.joinpath('token.yaml')
    with open(full_file_path) as token:
        token_data = yaml.load(token, Loader=yaml.Loader)
    return token_data

############################## MAIN ##############################

def main():
    print('Bot Started!\n')
    print('Bot link: http://t.me/erikd_test_bot\n\n')

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
