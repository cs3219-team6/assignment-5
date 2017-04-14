import re
import github
import datetime
import git
import re
import os
import shutil
import stat
import subprocess
from git import Repo

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
        list:   commits in chronological order in specified range
                each element is a dict containing ['sha'] and ['commit_message']
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
    if author_name and path:
        commit_history = gh.repos(owner)(repo).commits.get(author = author_name, since = start_date_formatted, until = end_date_formatted, path = path ) 
    elif not author_name and path: 
        commit_history = gh.repos(owner)(repo).commits.get(since = start_date_formatted, until = end_date_formatted, path = path)
    elif author_name and not path:
        commit_history = gh.repos(owner)(repo).commits.get(author = author_name, since = start_date_formatted, until = end_date_formatted)
    else:
        commit_history = gh.repos(owner)(repo).commits.get(since = start_date_formatted, until = end_date_formatted)

    n = len(commit_history)
    history = [] 
    for i in range(n):
        commit = {}
        commit['sha'] = commit_history[i]["sha"]
        commit['commit_message'] = commit_history[i]["commit"]["message"]
        history.append(commit)
    return history

def _add_write_access(func, path, excinfo):
    """
    Helper function to remove change read-only file status to editable
    Source: http://stackoverflow.com/questions/1889597/deleting-directory-in-python
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def _clone_repo(repo_link, destination=None):
    """
    Helper function to clone a repo to destination. If folder already exists, delete all version
    
    Args:
        repo_link:      owner/repo format
        destination:    local file path, set to default if not supplied

    Return:
        reference to the cloned repo
    """
    if not destination:
        destination = "%s%s" % ("./gitguard/", repo_link)
    if os.path.exists(destination):
        shutil.rmtree(destination, onerror=_add_write_access)
    repo_url = "%s%s%s" % ("https://github.com/", repo_link, ".git");
    
    repo = Repo.clone_from(repo_url , destination, branch="master")
    return repo


def get_commit_history_for_file(repo_link, file_path, author_name=None):
    """
    Return commit history for a file. Options: by author.
    
    Args:
        repo_link:      owner/repo format
        file_path:      path to file in repo
        author_name:    (optional) limit history to one author

    Return:
        list of commits in format [sha, author, title] if author's name no given
        OR
        list of commits in format [sha, title] if author's name is given
    """
    repo = _clone_repo(repo_link)
    if not author_name:
        log = repo.git.log("--pretty=format:'%H\t%an\t%s'", file_path)
    else:
        author_parameter = "--author=%s" % (author_name)
        log = repo.git.log("--pretty=format:'%H\t%an\t%s'", author_parameter, file_path)
    log_split = log.splitlines()
    history = []
    for line in log_split:
        line = line.strip()
        elements = re.split(r'\t+', line)
        commit = {}
        commit['sha'] = elements[0]
        if not author_name:
            commit['author'] = elements[1]
        commit['commit_message'] = elements[2]
        history.append(commit)
    return history

def get_stats_by_author(repo_link, author_name, username=None, password=None):
    """
    Return total number of commits, lines added and lines delted by an author
    
    Args:
        repo_link:      owner/repo format
        author_name:    limit history to one author
        username (str)          : github username
        password (str)          : github password

    Return:
        three numbers: commits, additions, deletions
    """
    owner, repo = process_repo_link(repo_link)
    gh = github.GitHub(username=username, password=password) if username and password else GITHUB
    all_data = gh.repos(owner)(repo).stats.contributors.get(author = author_name)[0];
    total_commits = all_data['total']
    weekly_data = all_data['weeks']
    adds = 0
    dels = 0
    for week in weekly_data:
        adds += week['a']
        dels += week['d']
    return total_commits, adds, dels

def compare_history_in_files(repo_link, file_path, start_line, end_line, *authors):
    """
    Return commit history for a file. Options: by author, specify code chunk
    
    Args:
        repo_link:      owner/repo format
        file_path:      path to file in repo
        start_line:     (optional) specify the starting line in the file
                        input negative value to ignore this field
        end_line:       (optional) specigy the ending line in the file to inspect
                        input negative value to ignore this field
        *authors:       name of authors to compare

    Return:
        list of commits in format [author_name, stats] with stats being the result
        of calling get_commit_history_for_file(repo_link, file_path, author)
    """
    num_authors = len(authors)
    if start_line <= 0:
        start_line = 1
    author_history = []
    for author in authors:
        history = {}
        history['name'] = author
        if end_line <= 0:
            history['stats'] = get_commit_history_for_file(repo_link, file_path, author)
        else:
            history['stats'] = get_commit_history_for_file_with_lines(repo_link, file_path, start_line, end_line, author)
        author_history.append(history)
    return author_history

def get_commit_history_for_file_with_lines(repo_link, file_name, start, end, author_name):
    """
    Return commit history for a file with lines litmit
    
    Args:
        repo_link:      owner/repo format
        file_path:      path to file in repo
        start:          specify the starting line in the file
                        input negative value to ignore this field
        end:            specify the ending line in the file to inspect
                        input negative value to ignore this field
        author_name:    name of author

    Return:
        list of commits by that author in those lines
    """
    _clone_repo(repo_link)
    command = 'git log --author="%s" -L %s,%s:%s | grep "commit [a-zA-Z0-9]"' % (author_name, start, end, file_name)
    try:
        result = subprocess.check_output(command, shell=True)
        lines = result.splitlines()
        history = []
        for line in lines:
            if line[0] == 'c':
                history.append(line)
        return history
    except subprocess.CalledProcessError as e:
        print(e)