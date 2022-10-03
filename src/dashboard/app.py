import logging
import enum

import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from dashboard.data import load_data, Schema, Categories
from controller.storage import DATA_PATH
from dashboard.components import *

# Todo: Coupling that is unwanted
# Maybe wrap the app varaible creation in an function? How then do with @callbacks?

HOST = "192.168.1.20"
PORT = "80"

log = logging.getLogger(__name__)


@enum.unique
class ID(str, enum.Enum):
    GRAPH_LINE_TEMPERATURE = "graph_line_temperature"
    GRAPH_HIST_TEMPERATURE = "graph_hist_temperature"
    CARD_TEMPERATURE = "temperature_card"
    UPDATE_BUTTON = "update_button"
    MEMORY = "memory"


load_figure_template("cyborg")
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Store(id=ID.MEMORY),
        html.H1("Home Climate dashboard"),
        html.Br(),
        dbc.Container(
            [
                dbc.Button("Update", id=ID.UPDATE_BUTTON, color="dark"),
            ],
            id="navigtion_pane",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        create_value_card(
                            title="Temperature", value="", id=ID.CARD_TEMPERATURE
                        ),
                        create_value_card("Other", value="100 kW", id=""),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dcc.Graph(id=ID.GRAPH_HIST_TEMPERATURE),
                    ]),
                dbc.Col([
                        dcc.Graph(id=ID.GRAPH_LINE_TEMPERATURE),
                    ]),
            ]
        ),
    ],
    id="main_div",
)


@app.callback(
    Output(ID.GRAPH_LINE_TEMPERATURE, "figure"),
    Output(ID.GRAPH_HIST_TEMPERATURE, "figure"),
    Output(ID.CARD_TEMPERATURE, "children"),
    Input(ID.UPDATE_BUTTON, "n_clicks"),
)
def update_figure(_):
    data = load_data(DATA_PATH)
    if data is None:
        raise PreventUpdate("No data to load")

    log.info("Updating figure")
    # fig = render_line_chart(data)
    fig_hist = render_histogram(data, [Categories.TEMPERATURE_FIRST_FLOOR])

    fig_line = render_line_chart(
        data,
        [
            Categories.TEMPERATURE_FIRST_FLOOR,
            Categories.ROOM_TEMP_SETPOINT,
            Categories.OUTDOOR_TEMP_OFFSET,
            Categories.OUTDOOR,
        ],
    )
    log.info("Figure updated")

    temperature = data.get_latest_value(Categories.TEMPERATURE_FIRST_FLOOR)
    temperature_text = f"{temperature:.1f}°C"
    return fig_line, fig_hist, temperature_text


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
    # Hosting on port 80 could cause troubles. Only use for production.
