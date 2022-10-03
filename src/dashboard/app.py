import logging
import enum

import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from dashboard.data import load_data, Schema
from controller.storage import DATA_PATH  
# Todo: Coupling that is unwanted
# Maybe wrap the app varaible creation in an function? How then do with @callbacks?

HOST = "192.168.1.20"
PORT = "80"

log = logging.getLogger(__name__)


class ID(str, enum.Enum):
    MAIN_GRAPH = "main_graph"
    UPDATE_BUTTON = "update_button"

load_figure_template("darkly")
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

app.layout = html.Div(
    [
        html.H1("Home Climate dashboard"),
        html.Div(
            [
                dbc.Button("Update", id=ID.UPDATE_BUTTON),
                dbc.Button("Other"),
                dbc.Button("Nav"),
                dbc.Button("Buttons"),
            ],
            id="navigtion_pane",
        ),
        html.Div([dcc.Graph(id=ID.MAIN_GRAPH)], id="chart_pane"),
    ],
    id="main_div",
)


@app.callback(
    Output(ID.MAIN_GRAPH, "figure"),
    Input(ID.UPDATE_BUTTON, "n_clicks"),
)
def update_figure(_):
    data = load_data(DATA_PATH)
    if data is None:
        raise PreventUpdate("No data to load")

    log.info("Updating figure")
    fig = px.line(data, x=Schema.TIME, y=Schema.VALUE, color=Schema.CATEGORY)
    fig.update_layout(title="Sensor values", xaxis_title="Time", yaxis_title="Value")
    log.info("Figure updated")
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
    # Hosting on port 80 could cause troubles. Only use for production. 
