# coding=utf-8
import dash
import datetime
from dash import html, Input, Output, State, ALL
from collections import defaultdict
from dash import dcc

from app import app
from tasks import Task

# ----------------------
# MARK DONE
# ----------------------

@app.callback(
    Output("task-store", "data", allow_duplicate=True),
    Input({"type": "done-btn", "index": ALL}, "n_clicks"),
    State("task-store", "data"),
    prevent_initial_call=True
)
def mark_done(_, tasks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return tasks
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    task_id = eval(button_id)["index"]
    for task in tasks:
        if task["task_id"] == task_id:
            task["last_done"] = datetime.date.today().isoformat()
            Task.from_dict(task).save()
    return tasks

@app.callback(
    Output("task-store", "data", allow_duplicate=True),
    Input({"type": "date-picker", "index": ALL}, "date"),
    State("task-store", "data"),
    prevent_initial_call=True
)
def update_date(date_list, tasks):

    ctx = dash.callback_context
    if not ctx.triggered:
        return tasks

    triggered = ctx.triggered[0]
    task_id = eval(triggered["prop_id"].split(".")[0])["index"]
    new_date = triggered["value"]

    for task in tasks:
        if task["task_id"] == task_id:
            task["last_done"] = new_date
            Task.from_dict(task).save()
    return tasks

# ----------------------
# DISPLAY TASKS
# ----------------------
def parse_frequency(frequency: int) -> str:
    if frequency == 1:
        return "Daily"
    elif frequency == 7:
        return "Weekly"
    elif 28 <= frequency <= 31:
        return "Monthly"
    else:
        return f"Evry {frequency} days"

@app.callback(
    Output("task-container", "children"),
    Input("task-store", "data")
)
def display_tasks(tasks):
    grouped = defaultdict(list)
    for task in sorted(tasks, key=lambda t: t["frequency"]):
        grouped[task["frequency"]].append(task)
    sections = []
    for frequency, task_list in grouped.items():
        sections.append(
            html.H2(f"{parse_frequency(frequency)} Tasks", style={"marginTop": "40px"})
        )
        if not task_list:
            sections.append(
                html.P("No tasks yet.", style={"color": "gray"})
            )
        for task in task_list:
            if task["last_done"]:
                last_done_date = datetime.date.fromisoformat(task["last_done"])
                days_since = (datetime.date.today() - last_done_date).days
                status_color = "#4CAF50"
                status_text = f"{days_since} day(s) ago"
                if days_since == 0:
                    status_color = "#636363"
                if days_since > frequency:
                    status_color = "#bf0000"
            else:
                days_since = None
                status_color = "#e74c3c"
                status_text = "Never completed"
            sections.append(
                html.Div([
                    html.Div([
                        html.H4(task["name"], style={"margin": "0"}),
                        html.Small(
                            f"Last done: {task['last_done'] if task['last_done'] else '—'}"
                        ),
                    ]),
                    html.Div([
                        html.Span("Last done: "),
                        dcc.DatePickerSingle(
                            id={"type": "date-picker", "index": task["task_id"]},
                            date=task["last_done"],
                            display_format="YYYY-MM-DD",
                            placeholder="Select date"
                        )
                    ]),
                    html.Div([
                        html.Span(
                            status_text,
                            style={
                                "color": status_color,
                                "marginRight": "15px",
                                "fontWeight": "bold"
                            }
                        ),
                        html.Button(
                            "✓ Done",
                            id={"type": "done-btn", "index": task["task_id"]},
                            n_clicks=0,
                            style={
                                # "backgroundColor": "#3498db",
                                # "color": "white",
                                "border": "none",
                                "padding": "8px 15px",
                                "cursor": "pointer",
                                "borderRadius": "5px"
                            }
                        )
                    ])
                ],
                style={
                    "backgroundColor": "#3b3b3b",
                    "padding": "15px 20px",
                    "borderRadius": "10px",
                    "boxShadow": "0 3px 8px rgba(0,0,0,0.05)",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "10px",
                })
            )

    return sections