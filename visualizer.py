import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# authentication
from settings_secret import PLOTLY_USERNAME, PLOTLY_API_TOKEN
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_TOKEN)

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
