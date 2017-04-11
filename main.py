import logging
import settings_secret
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
                    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token= settings_secret.TELEGRAM_API_TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def git(bot, update, args):
    print(args)
    bot.sendMessage(chat_id=update.message.chat_id, text="Under Construction")

git_handler = CommandHandler('git', git, pass_args=True)
dispatcher.add_handler(git_handler)


def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)



updater.start_polling()
