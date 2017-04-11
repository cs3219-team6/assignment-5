import re
import subprocess
import github

"""
gitguard_extractor.py

Extracts data for the visualizer.

repo_link is in the format USER/REPO_NAME or ORGANIZATION/REPO_NAME
"""

REGEX_REPO_LINK_DELIMITER = '\s*/\s*'
GITHUB = github.GitHub()

def is_repo_link_valid(repo_link):
    """
    Repository link validator.

    Args:
        repo_link (str): the repository link in the format owner/repo_name

    Returns:
        bool: True if repository exists (valid owner and repo_name), False otherwise
    """
    owner, repo = process_repo_link(repo_link)
    try:
        GITHUB.repos(owner)(repo).get()
    except github.ApiNotFoundError:
        return False
    return True

def process_repo_link(repo_link):
    #returns owner, repo_name
    return re.compile(REGEX_REPO_LINK_DELIMITER).split(repo_link)

def _get_contributors_from_api(repo_link):
    owner, repo = process_repo_link(repo_link)
    # connect to github API
    return GITHUB.repos(owner)(repo).contributors.get() 
    
def get_top_n_contributors(repo_link, n):
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
    contributors = _get_contributors_from_api(repo_link)

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

def _get_commits_from_api(repo_link):
    owner, repo = process_repo_link(repo_link)
    # GET /repos/:owner/:repo/commits
    return GITHUB.repos(owner)(repo).commits.get() 
    
def get_latest_commit_summary(repo_link):
    """
    Extracts latest commit info for a given repository.

    Args:
        repo_link (str) : the repository link in the format owner/repo_name

    Returns:
        dict: ['user'] --> {'name', 'email', 'username'}, ['message'], ['timestamp']
    """
    latest_commit = _get_commits_from_api(repo_link)[0]
    latest_commit_dict = {}
    latest_commit_dict['user'] = {}

    latest_commit_dict['user']['name'] = latest_commit['commit']['author']['name']
    latest_commit_dict['user']['email'] = latest_commit['commit']['author']['email']
    latest_commit_dict['user']['username'] = latest_commit['committer']['login']
    latest_commit_dict['message'] = latest_commit['commit']['message']
    latest_commit_dict['timestamp'] = latest_commit['commit']['committer']['date']
    return latest_commit_dict
