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

def get_top_contributor(repo_link):
    return get_top_n_contributors(repo_link, 1)

def get_top_n_contributors(repo_link, n):
    owner, repo = process_repo_link(repo_link)

    # connect to github API
    gh = github.GitHub()
    contributors = gh.repos(owner)(repo).contributors.get() 

    answer = ''
    persons = 0
    for contributor in contributors:
        answer += '%5d %s\n' % (contributor['contributions'], contributor['login'])
        persons += 1

        # only show top n contributors
        if persons >= n:
            break

    answer += '\nTop contributors for %s!' % repo_link
    return answer
