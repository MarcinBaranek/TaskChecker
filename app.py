import dash
from logger import logger
from layout import layout
import dash_bootstrap_components as dbc


# -------------------------
# Initialize Dash app
# -------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Task Checker"
server = app.server
app.layout = layout


@server.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled Flask exception")
    return "Internal Server Error", 500
