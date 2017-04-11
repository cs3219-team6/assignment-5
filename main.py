import gitguard
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

def top_three(bot, update, args):
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/top_three <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    if len(args) == 1:
        res = gitguard.get_top_n_contributors(args[0], 3)
    else:
        res = gitguard.get_top_n_contributors(args[0], 3, args[1], args[2])

    bot.sendMessage(chat_id=update.message.chat_id, text=str(map(lambda x: str(x['username']), res)))


top_three_handler = CommandHandler('top_three', top_three, pass_args=True)
dispatcher.add_handler(top_three_handler)

updater.start_polling()
