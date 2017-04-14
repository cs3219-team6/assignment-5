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

def _make_plot(data, layout, out_file='out.png'):
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

def _get_team_contribution_data_layout(repo_link, username=None, password=None):
    contributor_names = gitguard.get_repo_contributors(repo_link, username, password)
    contributor_commits = []
    contributor_insertions = []
    contributor_deletions = []
    print(contributor_names)

    for contributor in contributor_names:
        c, a, d = gitguard.get_stats_by_author(repo_link, contributor, username, password)
        print('%d %d %d' % (c, a, d))
        contributor_commits.append(c)
        contributor_insertions.append(a)
        contributor_deletions.append(d)
        
    print(contributor_commits)
    print(contributor_insertions)

    trace_commit =  go.Bar(
        x = contributor_names,
        y = contributor_commits,
        name = 'Commits',
        xaxis = 'x1',
        yaxis = 'y1',
    )

    trace_insertion =  go.Bar(
        x = contributor_names,
        y = contributor_insertions,
        name = 'Insertions',
        xaxis = 'x2',
        yaxis = 'y2',
    )

    trace_deletion =  go.Bar(
        x = contributor_names,
        y = contributor_deletions,
        name = 'Deletions',
        xaxis = 'x3',
        yaxis = 'y3',
    )

    layout_team_contribution = go.Layout(
        barmode = 'group',
        title = 'Team Contribution for %s' % repo_link,
        #width = STANDARD_WIDTH,
        #height = STANDARD_HEIGHT,

	    xaxis=dict(
	        domain=[0, 0.3]
	    ),
	    xaxis2=dict(
	        domain=[0.35, 0.65]
	    ),
	    xaxis3=dict(
	        domain=[0.7, 1]
	    ),
        yaxis=dict(
            domain=[0,1],
            anchor='x1',
        ),
        yaxis2=dict(
            domain=[0,1],
            anchor='x2',
        ),
        yaxis3=dict(
            domain=[0,1],
            anchor='x3',
        ),
    )

    return [trace_commit, trace_insertion, trace_deletion], layout_team_contribution

def get_team_contribution_summary(repo_link, out_file, username=None, password=None):
    data, layout = _get_team_contribution_data_layout(repo_link, username, password)
    _make_plot(data, layout, out_file)
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
    _make_plot(data, layout, out_file)
    return
