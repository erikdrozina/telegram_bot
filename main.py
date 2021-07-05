from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = ""

#   respond to /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}, How can I help you?'
    )

def main():
    print('Bot Started!\n')
    print('Bot link: http://t.me/erikd_test_bot\n\n')

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))

    updater.start_polling()
    updater.idle()

#   start
if __name__ == '__main__':
    main()