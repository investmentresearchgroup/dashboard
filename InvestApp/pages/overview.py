import os
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
from dash_bootstrap_components._components.Row import Row
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

from app import app

df_company = pd.read_csv('data/gse_historical_data.csv', low_memory=False,
                         parse_dates=['Date'])
df_company.set_index('Date', inplace=True)
# df_company.loc[:, 'sector'] = df_company.sector.fillna(
#     'Financials')  # Need to clean up the data for missing columns

sectors = set(df_company['sector'])
metrics = ['price', 'volume']

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(id="ticker_box", type="search", value="BOPP")),
        dbc.Col(
            dbc.Button("Search", id="search_button",
                       color="primary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


layout = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Navbar(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(src=PLOTLY_LOGO, height="60px")),
                                dbc.Col(dbc.NavbarBrand(
                                    "INVESTMENT RESEARCH GROUP", className="ml-2")),
                            ],
                            align="center",
                            no_gutters=True,
                        ),
                        href="https://plot.ly",
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(
                        search_bar, id="navbar-collapse", navbar=True),
                ],
                color="dark",
                dark=True,
            ),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H3('Sectors')
                ),
                dcc.RadioItems(
                    id='sector-items',
                    options=[{'label': i, 'value': i}
                             for i in sectors],
                    value='Financials',
                    labelStyle={'display': 'block'},
                ),
            ]), width=2
        ),
        dbc.Col(
            dbc.Card([
                html.H3("Sector Companies"),
                dcc.Dropdown(
                    id='sector-company-dropdown',
                    multi=True
                ),
                dbc.CardHeader(
                    html.H4(id='timeseries-title')
                ),
                dbc.CardBody([
                    dcc.RadioItems(
                        id='chosen-metric',
                        options=[{'label': k, 'value': k} for k in metrics],
                        value='price',
                        labelStyle={'display': 'inline-block'}
                    ),
                    dbc.ButtonGroup(
                        [dbc.Button("Capital", disabled=True, color='primary', className="mr-1"), dbc.Button(
                            "Price", color='primary', className="mr-1", id='price'), dbc.Button("Shares", color='primary', className="mr-1", id='volume')],
                        size="sm",
                    ),
                    dcc.Graph(
                        id='multi-company-graphs'
                    )
                ])
            ]), width=10
        ),
    ]),
])


def generate_company_figures(df_sector):
    pass


@app.callback(
    [Output('sector-company-dropdown', 'options'),
     Output('sector-company-dropdown', 'value'),
     Output('timeseries-title', 'children')],
    [Input('chosen-metric', 'value'),
     Input('sector-items', 'value')]
)
def display_sector(metric, value):
    df_sector = df_company.query("sector == @value")
    sector_companies = df_sector['name'].unique()
    company_options = [{'label': i, 'value': i} for i in sector_companies]
    return company_options, [sector_companies[0]], f'{metric} plot for companies specialising in {value}'


@app.callback(
    Output('multi-company-graphs', 'figure'),
    [Input('chosen-metric', 'value'),
     Input('sector-company-dropdown', 'value')])
def display_selected_company_graphs(metric, selected_companies):
    fig = go.Figure()
    for c in selected_companies:
        df_sector_company = df_company.query(
            "name == @c").sort_index()
        fig.add_trace(go.Scatter(x=df_sector_company.index,
                                 y=df_sector_company[metric],
                                 mode='lines',
                                 name=c))
    fig.update_layout(xaxis_title='Date',
                      yaxis_title=metric,
                      showlegend=True,
                      legend_title_text='Companies',
                      template='simple_white')
    return fig


def get_single_name_trace(df_name, metric):
    trace = go.Scatter(x=df_name)
    pass
