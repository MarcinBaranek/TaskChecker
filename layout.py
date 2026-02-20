from dash import dcc, html
from tasks import Task


# coding=utf-8
layout = html.Div(
    style={
        "fontFamily": "Arial",
        # "backgroundColor": "#f4f6f9",
        "padding": "40px"
    },
    children=[
        html.H1("🗂 Task Tracker", style={"textAlign": "center"}),
        # dcc.Dropdown(list(set([task.room for task in Task.load()])) + ['ALL'], 'ALL', multi=True),
        dcc.Store(id="task-store", data=[task.to_dict() for task in Task.load()]),

        html.Div(id="task-container")
    ]
)