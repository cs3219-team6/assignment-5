import datetime
import gitguard
import visualizer
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
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!\nYou can use /top_three /top_contributor /commit_history /team_contribution /team_lines_contribution and /last_commit")

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
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/top_contributor <repo_link> [<username> <password]`", parse_mode='Markdown')
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
        res = gitguard.get_top_contributor_in_past_week(args[0])
    else:
        res = gitguard.get_top_contributor_in_past_week(args[0], args[1], args[2])

    #TODO(tjonganthony): change the message returned
    bot.sendMessage(chat_id=update.message.chat_id, text=str(res))


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

def commit_history(bot, update, args):
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/commit_history <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    # first argument is always the repo link
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    # check validity of credentials
    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    viz_file = 'tmp.png'
    if len(args) == 1:
        visualizer.get_team_commit_history(args[0], viz_file)
    else:
        visualizer.get_team_commit_history(args[0], viz_file, username=args[1], password=args[2])

    #TODO(tjonganthony): change the message returned
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(viz_file, 'rb'))

commit_history_handler = CommandHandler('commit_history', commit_history, pass_args=True)
dispatcher.add_handler(commit_history_handler)

def team_contribution(bot, update, args):
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/team_contribution <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    # first argument is always the repo link
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    # check validity of credentials
    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    viz_file = 'tmp.png'
    if len(args) == 1:
        visualizer.get_team_contribution_summary(args[0], viz_file)
    else:
        visualizer.get_team_contribution_summary(args[0], viz_file, username=args[1], password=args[2])

    #TODO(tjonganthony): change the message returned
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(viz_file, 'rb'))

team_contribution_handler = CommandHandler('team_contribution', team_contribution, pass_args=True)
dispatcher.add_handler(team_contribution_handler)

def team_lines_contribution(bot, update, args):
    # check length of argument. 3 if username and credentials is given, 1 if otherwise.
    if len(args) != 1 and len(args) != 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong format. Format must follow `/team_lines_contribution <repo_link> [<username> <password]`", parse_mode='Markdown')
        return

    # first argument is always the repo link
    if not gitguard.is_repo_link_valid(args[0]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong or invalid github repo. Repo format must follow `<username>/<repo_name>`", parse_mode='Markdown')
        return

    # check validity of credentials
    if len(args) == 3 and not gitguard.is_user_valid(args[1], args[2]):
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong github credentials.")
        return

    viz_file = 'tmp.png'
    if len(args) == 1:
        visualizer.get_team_total_lines_summary(args[0], viz_file)
    else:
        visualizer.get_team_total_lines_summary(args[0], viz_file, username=args[1], password=args[2])

    #TODO(tjonganthony): change the message returned
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(viz_file, 'rb'))

team_lines_contribution_handler = CommandHandler('team_lines_contribution', team_lines_contribution, pass_args=True)
dispatcher.add_handler(team_lines_contribution_handler)

updater.start_polling()
