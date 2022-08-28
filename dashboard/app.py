from dash import Dash, dcc, html, Input, Output
import enum
import plotly.express as px
from data import load_data, Schema


app = Dash(__name__)


class ID(str, enum.Enum):
    MAIN_GRAPH = "main_graph"


data = load_data("")


def create_main_graph() -> dcc.Graph:
    fig = px.line(data, x=Schema.TIME, y=Schema.VALUE, color=Schema.CATEGORY)
    fig.update_layout(title="Sensor values", xaxis_title="Time", yaxis_title="Value")

    graph = dcc.Graph(id=ID.MAIN_GRAPH, figure=fig)
    return graph


app.layout = html.Div([html.H1("Home Climate dashboard"), create_main_graph()])


if __name__ == "__main__":
    app.run_server(debug=True)
