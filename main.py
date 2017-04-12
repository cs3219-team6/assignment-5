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
    """
    Github date parser.

    Args:
        input (str): date in format of yyy/mm/dd

    Returns:
        datetime.date: If correct format. None if otherwise.
    """
    try:
        return datetime.datetime.strptime(input, '%Y/%m/%d').date()
    except ValueError:
        return None

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!\nYou can use /top_three /top_contributor and /last_commit")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def top_three(bot, update, args):
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/top_three <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    # first argument is always the repo link
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    # check validity of credentials
    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    if len(args) == 1:
        res = gitguard.get_top_n_contributors(args[0], 3)
    else:
        res = gitguard.get_top_n_contributors(args[0], 3, args[1], args[2])

    #TODO(tjonganthony): change the message returned
    bot.sendMessage(chat_id=update.message.chat_id, text=str(map(lambda x: str(x['username']), res)))


top_three_handler = CommandHandler('top_three', top_three, pass_args=True)
dispatcher.add_handler(top_three_handler)

def top_contributor(bot, update, args):
    # check length. only repo name if length is 1, [since] if  2, [<username> <password>] if 3, all parameter if 4.
    # order of the 2 group optional parameter can be interchangable.
    if len(args) < 1 or len(args) > 4:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/top_contributor <repo_link> [since] [<username> <password]`", parse_mode='Markdown')
        return

    # check validity of repo
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    repo = args[0]
    since = datetime.datetime.today().date() - datetime.timedelta(days=3)
    username = password = None

    # if length is 2, then only since is supplied
    if len(args) == 2:
        if not parse_datetime(args[1]):
            bot.sendMessage(chat_id=update.message.chat_id, text="Wrong date format. Format must follow `yyyy/mm/dd`", parse_mode='Markdown')
            return
        since = parse_datetime(args[1])

    # if length is 3, then only github credentials is supplied
    if len(args) == 3:
        if not gitguard.is_user_valid(args[1], args[2]):
            bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
            return
        username, password = args[1:3]

    # if length is 4, all parameter is supplied
    if len(args) == 4:
        # if since in first parameter, then credentials in second and third.
        if parse_datetime(args[1]):
            if not gitguard.is_user_valid(args[2], args[3]):
                bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
                return
            since = parse_datetime(args[1])
            username, password = args[2:4]
        # if since in third parameter, then credentials in first and second.
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
    #TODO(tjonganthony): change output format
    bot.sendMessage(chat_id=update.message.chat_id, text=str(res['username']))


top_contributor_handler = CommandHandler('top_contributor', top_contributor, pass_args=True)
dispatcher.add_handler(top_contributor_handler)

def last_commit(bot, update, args):
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/last_commit <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    # first argument is always the repo link
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    # check validity of credentials
    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    if len(args) == 1:
        res = gitguard.get_latest_commit_summary(args[0])
    else:
        res = gitguard.get_latest_commit_summary(args[0], args[1], args[2])

    #TODO(tjonganthony): change output format
    bot.sendMessage(chat_id=update.message.chat_id, text=str(res))

last_commit_handler = CommandHandler('last_commit', last_commit, pass_args=True)
dispatcher.add_handler(last_commit_handler)

updater.start_polling()
