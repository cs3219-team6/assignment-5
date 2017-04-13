import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# authentication
from settings_secret import PLOTLY_USERNAME, PLOTLY_API_TOKEN
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_TOKEN)

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
