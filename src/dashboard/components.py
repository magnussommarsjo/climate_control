from typing import List, Optional
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

from dashboard.data import Data, Schema, Categories


def create_value_card(title: str, value: str, id: str) -> dbc.Card:

    return dbc.Card(
        [
            dbc.CardHeader(title, class_name="card-title"),
            dbc.CardBody([html.H3(value, className="card-title", id=id)]),
        ],
        class_name="value-card",
    )


def render_line_chart(data: Data, categories: List[Categories]) -> Figure:
    fig = px.line(
        data.filter(categories).to_df(),
        x=Schema.TIME,
        y=Schema.VALUE,
        color=Schema.CATEGORY,
    )
    fig.update_layout(title="Sensor values", xaxis_title="Time", yaxis_title="Value")
    return fig


def render_histogram(data: Data, categories: List[Categories]) -> Figure:
    fig = px.histogram(
        data.filter(categories).to_df(), x=Schema.VALUE, color=Schema.CATEGORY
    )
    return fig
