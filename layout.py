from dash import dcc, html
from tasks import Task
from styles import edit_modal_style

rooms = list(set([task.room for task in Task.load()]))

# coding=utf-8
layout = html.Div(
    style={
        "fontFamily": "Arial",
        # "backgroundColor": "#f4f6f9",
        "padding": "40px"
    },
    children=[
        html.H1("🗂 Task Tracker", style={"textAlign": "center"}),
        dcc.Checklist(
            options=[
                {'label': room, 'value': room} for room in rooms
            ] + [{'label': 'Hide Done', 'value': 'hide-done'}],
            value=rooms + ['hide-done'],
            id='hide-done-checkbox',
            inline=True,
            inputStyle={"width": "20px", "height": "20px",
                        "cursor": "pointer", "margin": "7px"},
            labelStyle={"fontSize": "20px", "cursor": "pointer"},
            style={'marginLeft': '20px', 'whiteSpace': 'nowrap'}
        ),
        dcc.Store(id="edit-task-id-store"),
        html.Div(
            id="edit-modal",
            children=[
                html.Div([
                    html.H3("Edit Task", style={"marginTop": 0}),

                    html.Label("Task Name"),
                    dcc.Input(id="edit-task-name", type="text", style={"width": "100%", "marginBottom": "10px"}),

                    html.Label("Frequency (days)"),
                    dcc.Input(id="edit-task-frequency", type="number", style={"width": "100%", "marginBottom": "20px"}),

                    html.Div([
                        html.Button("💾 Save", id="edit-save-btn", n_clicks=0,
                            style={"marginRight": "10px", "padding": "8px 20px", "cursor": "pointer"}),
                        html.Button("✕ Cancel", id="edit-cancel-btn", n_clicks=0,
                            style={"padding": "8px 20px", "cursor": "pointer"}),
                    ])
                ],
                style={
                    "background": "#2b2b2b",
                    "padding": "30px",
                    "borderRadius": "10px",
                    "width": "400px",
                    "position": "relative"
                })
            ],
            style={
                "display": "none",           # hidden by default
                **edit_modal_style
            }
        ),
        dcc.Store(id="task-store", data=[task.to_dict() for task in Task.load()]),

        html.Div(id="task-container")
    ]
)