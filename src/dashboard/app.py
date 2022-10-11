import logging
import enum

import plotly.express as px
from dashboard.data import load_data_from_database, Schema
from dash import Dash, dcc, html, Input, Output



HOST = "192.168.1.20"
PORT = "80"

log = logging.getLogger(__name__)


class ID(str, enum.Enum):
    MAIN_GRAPH = "main_graph"
    UPDATE_BUTTON = "update_button"


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Home Climate dashboard"),
        html.Button("Update", id=ID.UPDATE_BUTTON),
        dcc.Graph(id=ID.MAIN_GRAPH),
    ]
)


@app.callback(
    Output(ID.MAIN_GRAPH, "figure"),
    Input(ID.UPDATE_BUTTON, "n_clicks"),
)
def update_figure(_):

    data = load_data_from_database()
    log.info("Updating figure")
    fig = px.line(data, x=Schema.TIME, y=Schema.VALUE, color=Schema.CATEGORY)
    fig.update_layout(title="Sensor values", xaxis_title="Time", yaxis_title="Value")
    log.info("Figure updated")
    return fig


if __name__ == "__main__":
    DEBUG = True
    app.run(debug=DEBUG, host=HOST, port=PORT)
