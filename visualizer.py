import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# authentication
from settings_secret import PLOTLY_USERNAME, PLOTLY_API_TOKEN
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_TOKEN)

import dateutil.parser

# relies on gitguard to interface with github API
import gitguard

STANDARD_WIDTH = 800
STANDARD_HEIGHT = 640

def make_plot(data, layout, out_file='out.png'):
    """
    Generates and saves a plotly plot given some data.

    Args:
        data (list): a list of graph_objs (e.g. go.Bar, go.Line)
        layout (go.Layout): a go.Layout object
        out_file (str): name of the output file; default 'out.png'

    """
    fig = go.Figure(data=data, layout=layout)
    py.image.save_as(fig, filename = out_file)
    return

def _get_team_contribution_data_layout(repo_link):
    contributors = gitguard._get_contributors_from_api(repo_link, gitguard.GITHUB)
    contributor_names = []
    contributor_commits = []
    #contributor_insertions = []
    #contributor_deletions = []

    for contributor in contributors:
        contributor_names.append(contributor['login'])
        contributor_commits.append(contributor['contributions'])
        
    trace_commit =  go.Bar(
        x = contributor_names,
        y = contributor_commits,
        name = 'Commits',
    )

    layout_team_contribution = go.Layout(
        barmode = 'group',
        title = 'Team Contribution',
        width = STANDARD_WIDTH,
        height = STANDARD_HEIGHT,
    )

    return [trace_commit], layout_team_contribution

def get_team_contribution_summary(repo_link, out_file):
    data, layout = _get_team_contribution_data_layout(repo_link)
    make_plot(data, layout, out_file)
    return

def _extract_date_from_timestamp(timestamp):
    return dateutil.parser.parse(timestamp).date()
    
def _get_commit_history_for_author(repo_link, author_name=None, start=None, end=None, path=None, username=None, password=None):
    commit_history = gitguard.get_commit_history(repo_link, author_name, start, end, path, username, password)
    commit_counts = _histogram_commit_history(commit_history)
    return _extract_x_y_data(commit_counts)

def _histogram_commit_history(commit_history):
    commit_counts = {}

    for commit in commit_history:
        date = _extract_date_from_timestamp(commit['timestamp'])
        if date not in commit_counts:
            commit_counts[date] = 0
        commit_counts[date] += 1
    
    return commit_counts

def _extract_x_y_data(histogram):
    x = list(histogram.keys())
    x.sort()
    y = []
    for key in x:
        y.append(histogram[key])
    return x, y

def _get_team_commit_history_data_layout(repo_link, team, start=None, end=None, path=None, username=None, password=None):
    data = []
    # make a Scatter graph object (trace) for each author labelled appropriately
    for author in team:
        timestamps, commits = _get_commit_history_for_author(repo_link, author, start, end, path, username, password)
        trace = go.Scatter(
            x = timestamps,
            y = commits,
            name = author
        )
        data.append(trace)

    title = 'Team Commit History for %s' % repo_link
    
    if start:
        title += ' from %s' % start
    if end:
        title += ' to %s' % end
    if path:
        title += ' for %s' % path

    layout = go.Layout(
        title = title,
        yaxis = dict(title = 'Commits'),
    )

    return data, layout

def get_team_commit_history(repo_link, out_file, start=None, end=None, path=None, username=None, password=None):
    team = gitguard.get_repo_contributors(repo_link)
    data, layout = _get_team_commit_history_data_layout(repo_link, team)
    make_plot(data, layout, out_file)
    return
