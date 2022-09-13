import logging
import traceback
import sys

DEBUG = True
HOST = "192.168.1.20"
PORT = "80"

# Setting up logging
FORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
logging.basicConfig(
    level=logging.DEBUG, filename="log_dashboard.txt", filemode="w", format=FORMAT
)
log = logging.getLogger(__name__)

# Logg all unhandled exceptions
def exception_handler(*exc_info):
    msg = "".join(traceback.format_exception(*exc_info))
    log.exception(f"Unhandeled exception: {msg}")


sys.excepthook = exception_handler

from dash import Dash, dcc, html, Input, Output
import enum
import plotly.express as px
from dashboard.data import load_data, Schema
from controller.storage import DATA_PATH  # Todo: Coupling that is unwanted



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
    data = load_data(DATA_PATH)
    log.info("Updating figure")
    fig = px.line(data, x=Schema.TIME, y=Schema.VALUE, color=Schema.CATEGORY)
    fig.update_layout(title="Sensor values", xaxis_title="Time", yaxis_title="Value")
    log.info("Figure updated")
    return fig


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)

