# coding=utf-8
from pyexpat import features

import dash
import datetime
from dash import html, Input, Output, State, ALL
from collections import defaultdict
from dash import dcc, ctx
from dash.exceptions import PreventUpdate
from styles import edit_modal_style

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
    Input("task-store", "data"),
    Input("edit-task-id-store", "data"),
    Input("hide-done-checkbox", "value"),
)
def display_tasks(tasks, edit_modal, checkboxs):
    if edit_modal is not None:
        raise PreventUpdate
    tasks = Task.load()
    grouped = defaultdict(list)
    for task in sorted(tasks, key=lambda t: t.frequency):
        grouped[task.frequency].append(task)
    sections = []
    for frequency, task_list in grouped.items():
        if 'hide daily' in checkboxs and frequency == 1:
            continue
        task_list = sorted(task_list, key=lambda t: (t.last_done, t.name))
        task_list = list(filter(lambda t: t.room in checkboxs, task_list))
        task_list = list(filter(lambda t: not ('hide-done' in checkboxs and t.days_since_last_done <= 0.7 * frequency), task_list))
        if not task_list:
            continue
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
                if task.days_since_last_done <= 1:
                    status_color = "#636363"
                if task.days_since_last_done >= 0.7 * frequency:
                    status_color = "#929423"
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
                        ),
                        html.Button(
                            "✏️ Edit",
                            id={"type": "edit-btn", "index": task.task_id},
                            n_clicks=0,
                            style={
                                "border": "none",
                                "padding": "8px 15px",
                                "cursor": "pointer",
                                "borderRadius": "5px",
                                "marginLeft": "8px"
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


@app.callback(
    Output("edit-modal", "style"),
    Output("edit-task-name", "value"),
    Output("edit-task-frequency", "value"),
    Output("edit-task-id-store", "data"),
    Input({"type": "edit-btn", "index": ALL}, "n_clicks"),
    Input("edit-cancel-btn", "n_clicks"),
    prevent_initial_call=True
)
def open_edit_modal(edit_clicks, cancel_click):
    modal_hidden = {"display": "none", **edit_modal_style}  # same style as above but display:none
    modal_visible = {"display": "flex", **edit_modal_style} # same style as above but display:flex

    triggered = ctx.triggered_id

    # Close modal on cancel
    if triggered == "edit-cancel-btn":
        return modal_hidden, dash.no_update, dash.no_update, None

    # Open modal when an edit button is clicked
    if isinstance(triggered, dict) and triggered["type"] == "edit-btn":
        if not any(edit_clicks):
            raise PreventUpdate
        task_id = triggered["index"]
        tasks = Task.load()
        task = next(t for t in tasks if t.task_id == task_id)
        return modal_visible, task.name, task.frequency, task_id

    raise PreventUpdate

@app.callback(
    Output("task-store", "data", allow_duplicate=True),
    Output("edit-modal", "style", allow_duplicate=True),
    Input("edit-save-btn", "n_clicks"),
    State("edit-task-id-store", "data"),
    State("edit-task-name", "value"),
    State("edit-task-frequency", "value"),
    prevent_initial_call=True
)
def save_edited_task(n_clicks, task_id, name, frequency):
    if not n_clicks or not task_id:
        raise PreventUpdate

    tasks = Task.load()
    for task in tasks:
        if task.task_id == task_id:
            task.name = name
            task.frequency = frequency
            task.save() # persist changes
            break

    modal_hidden = {"display": "none", **edit_modal_style}
    return [task.to_dict() for task in Task.load()], modal_hidden  # trigger re-render