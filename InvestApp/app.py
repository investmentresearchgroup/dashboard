import dash
import dash_bootstrap_components as dbc

# Try https://bootswatch.com/lux/
# dbc.themes.LUX


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True
                )

app.title = "Investment Application"
server = app.server
