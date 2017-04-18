import re
import github

"""
gitguard_extractor.py

Extracts data for the visualizer.

repo_link is in the format USER/REPO_NAME or ORGANIZATION/REPO_NAME
"""

REGEX_REPO_LINK_DELIMITER = '\s*/\s*'
REPO_LINK_REGEX = re.compile(REGEX_REPO_LINK_DELIMITER)
GITHUB = github.GitHub()

def is_repo_link_valid(repo_link, username=None, password=None):
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
        gh = github.GitHub(username=username, password=password) if username and password else GITHUB
        gh.repos(owner)(repo).get()
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

def _get_user(username):
    return GITHUB.users(username).get()

def get_name_from_username(username):
    """
    Retrieves a user's profile name from their username

    Args:
        username (str): github username

    Returns:
        str: the user's name, None if no such username found
    """
    try:
        return _get_user(username)['name']
    except github.ApiNotFoundError:
        return None

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


def _get_contributor_stats(repo_link, gh):
    owner, repo = process_repo_link(repo_link)
    return gh.repos(owner)(repo).stats.contributors.get()

def get_top_contributor_in_past_week(repo_link, username=None, password=None):
    """
    Return top contributor of within the last week

    Args:
        repo_link (str) : the repository link in the format owner/repo_name
        username (str): github username
        password (str): github password

    Returns:
        dict:   {   'username': <username>,
                    'name': <name>,
                    'commits': <commits>
                    'additions': <additions>
                    'deletions': <deletions>
                }
    """
    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    top = _get_contributor_stats(repo_link, gh)[0]

    return {'username': top['author']['login'], 'name': get_name_from_username(top['author']['login']), 'commits': top['weeks'][0]['c'], 'additions': top['weeks'][0]['a'], 'deletions': top['weeks'][0]['d']}
