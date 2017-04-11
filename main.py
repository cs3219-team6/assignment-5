import datetime
import gitguard
import logging
import settings_secret
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
                    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token= settings_secret.TELEGRAM_API_TOKEN)
dispatcher = updater.dispatcher

def parse_datetime(input):
    try:
        return datetime.datetime.strptime(input, '%Y/%m/%d').date()
    except ValueError:
        return None

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

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

def top_contributor(bot, update, args):
    if len(args) < 1 or len(args) > 4:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/top_contributor <repo_link> [since] [<username> <password]`", parse_mode='Markdown')
        return

    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    repo = args[0]
    since = datetime.datetime.today().date() - datetime.timedelta(days=3)
    username = password = None

    if len(args) == 2:
        if not parse_datetime(args[1]):
            bot.sendMessage(chat_id=update.message.chat_id, text="Wrong date format. Format must follow `yyyy/mm/dd`", parse_mode='Markdown')
            return
        since = parse_datetime(args[1])

    if len(args) == 3:
        if not gitguard.is_user_valid(args[1], args[2]):
            bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
            return
        username, password = args[1:3]


    if len(args) == 4:
        if parse_datetime(args[1]):
            if not gitguard.is_user_valid(args[2], args[3]):
                bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
                return
            since = parse_datetime(args[1])
            username, password = args[2:4]
        elif parse_datetime(args[3]):
            if not gitguard.is_user_valid(args[1], args[2]):
                bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
                return
            since = parse_datetime(args[3])
            username, password = args[1:3]
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Wrong date format. Format must follow `yyyy/mm/dd`", parse_mode='Markdown')
            return

    res = gitguard.get_latest_top_contributor(repo, since, username, password)
    bot.sendMessage(chat_id=update.message.chat_id, text=str(res['username']))


top_contributor_handler = CommandHandler('top_contributor', top_contributor, pass_args=True)
dispatcher.add_handler(top_contributor_handler)

updater.start_polling()
