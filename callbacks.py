# coding=utf-8
import dash
import datetime
from dash import html, Input, Output, State, ALL
from collections import defaultdict
from dash import dcc

from app import app
from tasks import Task
from config import BACKGROUND_COLORS

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
    tasks = [task.to_dict() for task in Task.load()]
    for item in ctx.triggered:
        if not item.get("value", 0):
            continue
        task_id = eval(item["prop_id"].split(".")[0])["index"]
        break
    else:
        task_id = None
    for i, task in enumerate(tasks):
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
    tasks = Task.load()
    triggered = ctx.triggered[0]
    task_id = eval(triggered["prop_id"].split(".")[0])["index"]
    new_date = triggered["value"]

    for task in tasks:
        if task.task_id == task_id:
            task.last_done = datetime.date.fromisoformat(new_date)
            task.save()
    return [t.to_dict() for t in tasks]

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
    tasks = Task.load()
    grouped = defaultdict(list)
    for task in sorted(tasks, key=lambda t: t.frequency):
        grouped[task.frequency].append(task)
    sections = []
    for frequency, task_list in grouped.items():
        task_list = sorted(task_list, key=lambda t: (t.last_done, t.name))
        sections.append(
            html.H2(f"{parse_frequency(frequency)} Tasks", style={"marginTop": "40px"})
        )
        if not task_list:
            sections.append(
                html.P("No tasks yet.", style={"color": "gray"})
            )
        for task in task_list:
            if task.last_done:
                status_color = "#4CAF50"
                status_text = f"{task.days_since_last_done} day(s) ago"
                if task.days_since_last_done == 1:
                    status_color = "#636363"
                if task.days_since_last_done > frequency:
                    status_color = "#bf0000"
            else:
                status_color = "#e74c3c"
                status_text = "Never completed"
            sections.append(
                html.Div([
                    html.Div([
                        html.H4(task.name, style={"margin": "0"}),
                        html.Small(
                            f"Last done: {task.last_done if task.last_done else '—'}"
                        ),
                    ]),
                    html.Div([
                        html.Span("Last done: "),
                        dcc.DatePickerSingle(
                            id={"type": "date-picker", "index": task.task_id},
                            date=task.last_done,
                            display_format="YYYY-MM-DD",
                            placeholder="Select date"
                        )
                    ],
                        style={"alignItems": "right"}
                    ),
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
                            id={"type": "done-btn", "index": task.task_id},
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
                    "backgroundColor": BACKGROUND_COLORS.get(task.room, "#3b3b3b"),
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
