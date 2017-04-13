import re
import github
import datetime

"""
gitguard_extractor.py

Extracts data for the visualizer.

repo_link is in the format USER/REPO_NAME or ORGANIZATION/REPO_NAME
"""

REGEX_REPO_LINK_DELIMITER = '\s*/\s*'
REPO_LINK_REGEX = re.compile(REGEX_REPO_LINK_DELIMITER)
GITHUB = github.GitHub()

def is_repo_link_valid(repo_link):
    """
    Repository link validator.

    Args:
        repo_link (str): the repository link in the format owner/repo_name

    Returns:
        bool: True if repository exists (valid owner and repo_name) AND repository is public, False otherwise
    """

    owner = repo = ''
    try:
        owner, repo = process_repo_link(repo_link)
    except ValueError:
        return False

    try:
        GITHUB.repos(owner)(repo).get()
        return True
    except github.ApiNotFoundError:
        return False

def is_user_valid(username, password):
    """
    User credentials validator.

    Args:
        username (str): github username
        password (str): github password

    Returns:
        bool: True if user credentials is valid. False if otherwise
    """

    gh = github.GitHub(username=username, password=password)
    try:
        gh.users('githubpy').followers.get()
        return True
    except github.ApiError:
        return False

def process_repo_link(repo_link):
    #returns owner, repo_name
    return REPO_LINK_REGEX.split(repo_link)

def _get_contributors_from_api(repo_link, gh):
    owner, repo = process_repo_link(repo_link)
    # connect to github API
    return gh.repos(owner)(repo).contributors.get()

def get_top_n_contributors(repo_link, n, username = None, password = None):
    """
    Extracts top contributors for a given repository.

    Args:
        repo_link (str) : the repository link in the format owner/repo_name
        n (int)         : top n contributors; must be greater than 0

    Returns:
        list:   top contributors in descending order of contributions
                the n-th element of the list is the top (n+1)th contributor
                each element is a dict containing ['username'] and ['contributions']
    """
    assert n > 0

    persons = 0
    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    contributors = _get_contributors_from_api(repo_link, gh)

    contributions = []
    for contributor in contributors:
        this_contributor = {}
        this_contributor['username'] = contributor['login']
        this_contributor['contributions'] = contributor['contributions']
        contributions.append(this_contributor)

        persons += 1
        # only show top n contributors
        if persons >= n:
            break

    return contributions

def _get_commits_from_api(repo_link, gh):
    owner, repo = process_repo_link(repo_link)
    # GET /repos/:owner/:repo/commits
    return gh.repos(owner)(repo).commits.get()

def get_latest_commit_summary(repo_link, username=None, password=None):
    """
    Extracts latest commit info for a given repository.

    Args:
        repo_link (str) : the repository link in the format owner/repo_name
        username (str): github username
        password (str): github password

    Returns:
        dict: ['user'] --> {'name', 'email', 'username'}, ['message'], ['timestamp']
    """

    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    latest_commit = _get_commits_from_api(repo_link, gh)[0]
    latest_commit_dict = {}
    latest_commit_dict['user'] = {}

    latest_commit_dict['user']['name'] = latest_commit['commit']['author']['name']
    latest_commit_dict['user']['email'] = latest_commit['commit']['author']['email']
    latest_commit_dict['user']['username'] = latest_commit['committer']['login']
    latest_commit_dict['message'] = latest_commit['commit']['message']
    latest_commit_dict['timestamp'] = latest_commit['commit']['committer']['date']
    return latest_commit_dict


def get_latest_top_contributor(repo_link, since, username=None, password=None):
    """
    Return top contributor of recent period.

    Args:
        repo_link (str) : the repository link in the format owner/repo_name
        since (datetime.date) : datetime object of starting observation time
        username (str): github username
        password (str): github password

    Returns:
        dict: {'username': <username>, 'name': <name'}
    """
    #TODO(Darren): implement this
    return {'username': 'username', 'name': 'name'}

def get_total_insertions_deletions(repo_link, username=None, password=None):
    """
    Return the total number of insertions and deletions
    API: GET /repos/:owner/:repo/stats/code_frequency

    Args:
        repo_link (str) : the repository link in the format owner/repo_name
        username (str): github username
        password (str): github password

    Returns:
        insertions, deletions
    """
    owner, repo = process_repo_link(repo_link)
    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    weekly_data = gh.repos(owner)(repo).stats.code_frequency.get();

    adds = 0
    dels = 0
    for week in weekly_data:
        adds += week[1]
        dels += week[2]
    return adds, dels * -1

def get_commit_history(repo_link, author_name=None, start=None, end=None, path=None, username=None, password=None):
    """
    Return the commit history of a specific author over a period of time
    API: https://api.github.com/repos/:owner/:repo/commits?author?since?until

    Args:
        repo_link (str)         : the repository link in the format owner/repo_name
        author_name (str)       : author's GitHub username
        start (datetime.date)   : datetiem.date object to be converted to YYYY-MM-DDTHH:MM:SSZ
                                  if not value provided set to 10 years ago
        end (datetime.date)     : datetime.date object to be converted to YYYY-MM-DDTHH:MM:SSZ
                                  if no value provided set to current time
        path (str)              : filepath. if none provided then set to whole repository
        username (str)          : github username
        password (str)          : github password

    Returns:
        history[#commits][i]: commit SHA (i =0) and commit message (i=1)
    """
    now = datetime.datetime.now()

    if start:
        start_date_formatted = "%s-%s-%sT%s:%s:%sZ" % (start.year, start.month, start.day, "00", "00", "00")
    else:
        start_date_formatted = "%s-%s-%sT%s:%s:%sZ" % (now.year - 10, "01", "01", "00", "00", "00")

    if end:
        end_date_formatted = "%s-%s-%sT%s:%s:%sZ" % (end.year, end.month, end.day, "23", "59", "59")
    else:
        end_date_formatted = "%s-%s-%sT%s:%s:%sZ" % (now.year, now.month, now.day, "23", "59", "59")


    owner, repo = process_repo_link(repo_link)
    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    if (author_name and path):
        commit_history = gh.repos(owner)(repo).commits.get(author = author_name, since = start_date_formatted, until = end_date_formatted, path = path ) 
    elif (!author_name and path): 
        gh.repos(owner)(repo).commits.get(since = start_date_formatted, until = end_date_formatted, path = path)
    elif (author_name and !path):
        gh.repos(owner)(repo).commits.get(author = author_name, since = start_date_formatted, until = end_date_formatted)
    else:
        gh.repos(owner)(repo).commits.get(since = start_date_formatted, until = end_date_formatted)

    n = len(commit_history)
    history = [[0 for x in range(2)] for y in range(n)] 
    for i in range(n):
        history[i][0] = commit_history[i]["sha"]
        history[i][1] = commit_history[i]["commit"]["message"]
    return history
