import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H1('Home Page'),
    dcc.Dropdown(
        id='page-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='page-1-display-value')
])


@app.callback(
    Output('page-1-display-value', 'children'),
    [Input('page-1-dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)
