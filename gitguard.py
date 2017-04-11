import re
import subprocess
import github

"""
gitguard_extractor.py

Extracts data for the visualizer.

repo_link is in the format USER/REPO_NAME or ORGANIZATION/REPO_NAME
"""

REGEX_REPO_LINK_DELIMITER = '\s*/\s*'

def process_repo_link(repo_link):
    #returns owner, repo_name
    return re.compile(REGEX_REPO_LINK_DELIMITER).split(repo_link)

def _get_contributors_from_api(repo_link):
    owner, repo = process_repo_link(repo_link)
    # connect to github API
    gh = github.GitHub()
    return gh.repos(owner)(repo).contributors.get() 
    
def get_top_n_contributors(repo_link, n):
    answer = ''
    persons = 0
    contributors = _get_contributors_from_api(repo_link)
    for contributor in contributors:
        answer += '%5d %s\n' % (contributor['contributions'], contributor['login'])
        persons += 1

        # only show top n contributors
        if persons >= n:
            break

    answer += '\nTop contributors for %s!' % repo_link
    return answer

def _get_commits_from_api(repo_link):
    owner, repo = process_repo_link(repo_link)
    # GET /repos/:owner/:repo/commits
    gh = github.GitHub()
    return gh.repos(owner)(repo).commits.get() 
    
def get_latest_commit_summary(repo_link):
    latest_commit = _get_commits_from_api(repo_link)[0]
    answer = 'Latest commit for %s\n' % repo_link
    answer += '\n%s\n' % latest_commit['commit']['message']
    answer += 'by %s on %s\n' % (latest_commit['committer']['login'], latest_commit['commit']['committer']['date'])
    return answer
